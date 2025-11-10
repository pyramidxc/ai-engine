"""
Orchestrator - Central coordination of attack path generation.

Coordinates the full RAG pipeline:
1. Input validation
2. Thread initialization via Context Threader
3. Stage-by-stage generation loop:
   - Get next stage context
   - Build prompt
   - Call LLM
   - Parse and validate output
   - Reconcile with thread state
4. Decide next action (continue/stop/retry)
5. Emit telemetry and logs
"""

import json
import time
from datetime import datetime
from typing import Any, Dict, Optional

from app.config import settings
from app.core.prompts import PromptBuilder
from app.models.host import InputHost
from app.services.context_threader import ContextThreader
from app.services.llm_client import LLMClient
from app.utils.exploitability_validator import ExploitabilityValidator
from app.utils.token_logger import TokenLogger


class Orchestrator:
    """
    Central orchestrator for attack path generation.
    
    Implements the complete RAG flow from the architecture diagram:
    - Validates input
    - Coordinates Context Threader, Prompt Builder, LLM
    - Parses and validates LLM output
    - Persists thread state
    - Decides next actions
    """
    
    def __init__(self):
        """Initialize orchestrator with dependencies."""
        self.context_threader = ContextThreader()
        self.prompt_builder = PromptBuilder()
        self.llm_client = LLMClient()
        self.token_logger = TokenLogger()
        self.exploitability_validator = ExploitabilityValidator()
        
        # Orchestration configuration
        self.max_stages = 15
        self.max_retries_per_stage = 3
        self.validation_strict = True
    
    async def generate_attack_path(
        self,
        request_id: str,
        host: InputHost,
        client_metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Main orchestration flow for attack path generation.
        
        Args:
            request_id: Unique request identifier
            host: Target host parameters from client
            client_metadata: Optional client context (client_id, timestamp, etc.)
            
        Returns:
            Complete attack path result with thread state and metadata
        """
        start_time = time.time()
        
        print(f"\n{'='*70}")
        print("ORCHESTRATOR - Attack Path Generation")
        print(f"Request ID: {request_id}")
        print(f"{'='*70}\n")
        
        # Step 1: Validate input
        print("  [1/9] Validating input...")
        validation_result = self._validate_input(host)
        if not validation_result["valid"]:
            return self._error_response(
                request_id=request_id,
                error_type="validation_error",
                message=validation_result["errors"]
            )
        
        # Step 2: Initialize thread via Context Threader
        print("  [2/9] Initializing attack thread...")
        reconnaissance = self.prompt_builder.build_reconnaissance_summary(host)
        constraints = self._build_constraints(host)
        
        thread_state = self.context_threader.initialize_thread(
            asset_id=host.asset_id or f"asset_{request_id[:8]}",
            reconnaissance=reconnaissance,
            constraints=constraints
        )
        thread_id = thread_state.thread_id
        
        print(f"         Thread ID: {thread_id}")
        
        # Step 3: Generate STAGE 0 ONLY
        print("\n  [3/5] Generating STAGE 0...")
        stage_index = 0
        
        # 3a: Get next stage context from CT
        print("         → Requesting context from CT")
        next_context = self.context_threader.get_next_stage_context(
            thread_id=thread_id,
            stage_index=stage_index
        )
        
        # 3b: Build prompt
        print("         → Building STAGE 0 prompt")
        stage_prompt = self.prompt_builder.build_state_prompt(
            host=host,
            state_index=stage_index,
            context=next_context
        )
        
        # 3c: Call LLM
        print("         → Calling LLM Provider")
        llm_result = await self._call_llm_with_retry(
            stage_index=stage_index,
            prompt=stage_prompt,
            request_id=request_id
        )
        
        if llm_result["status"] == "error":
            return self._error_response(
                request_id=request_id,
                error_type="llm_error",
                message=llm_result["error"]
            )
        
        raw_output = llm_result["content"]
        usage = llm_result["usage"]
        total_tokens = usage.get("total_tokens", 0)
        
        # 3d: Parse and validate output
        print("         → Parsing and validating output")
        parsed_result = self._parse_stage_output(raw_output, stage_index, host)
        
        validation_context = {**next_context, "stage_index": stage_index}
        validation = self._validate_stage_output(
            parsed=parsed_result,
            constraints=constraints,
            context=validation_context
        )
        
        if not validation["valid"]:
            print(f"         ✗ Validation failed: {validation['errors']}")
            return self._error_response(
                request_id=request_id,
                error_type="validation_error",
                message=validation["errors"]
            )
        
        # 3e: Reconcile and persist via CT
        print("         → Reconciling ThreadState with CT")
        reconcile_result = self.context_threader.reconcile_and_persist(
            thread_id=thread_id,
            stage_index=stage_index,
            stage_result=parsed_result,
            merge_strategy="append"
        )
        
        print(f"         ✓ Persisted - Version: {reconcile_result['version']}")
        
        # Store stage result
        stage_result = {
            "stage_index": stage_index,
            "content": raw_output,
            "parsed": parsed_result,
            "tokens": usage.get("total_tokens", 0),
            "response_time_ms": llm_result["response_time_ms"]
        }
        
        total_time = time.time() - start_time
        
        # Step 4: Get thread snapshot
        print("\n  [4/5] Retrieving thread snapshot...")
        final_snapshot = self.context_threader.get_thread_snapshot(thread_id)
        
        # Step 5: Emit telemetry
        print("  [5/5] Emitting telemetry and logs...")
        self._emit_telemetry(
            request_id=request_id,
            thread_id=thread_id,
            stages_count=1,
            total_tokens=total_tokens,
            execution_time=total_time
        )
        
        print(f"\n{'='*70}")
        print("ORCHESTRATOR - STAGE 0 Complete")
        print(f"Execution Time: {total_time:.2f}s")
        print(f"{'='*70}\n")
        
        return {
            "request_id": request_id,
            "thread_id": thread_id,
            "status": "success",
            "stage": {
                "stage_index": 0,
                "technique": parsed_result.get("technique"),
                "action": parsed_result.get("action"),
                "expected_outcome": parsed_result.get("expected_outcome"),
                "probability": parsed_result.get("probability"),
                "bifurcations": parsed_result.get("bifurcations", [])
            },
            "raw_content": raw_output,
            "thread_snapshot": final_snapshot,
            "metadata": {
                "execution_time_seconds": round(total_time, 2),
                "stage_index": 0,
                "tokens_used": total_tokens,
                "model": settings.LLM_MODEL
            }
        }
    
    def _validate_input(self, host: InputHost) -> Dict[str, Any]:
        """
        Validate incoming host parameters.
        
        Args:
            host: Input host object
            
        Returns:
            Validation result with valid flag and errors list
        """
        errors = []
        
        # For AD-focused analysis, we just check if we have SOME identifying information
        has_identity = (
            host.DNSHostName or 
            host.SamAccountName or 
            host.DistinguishedName or 
            host.DomainName
        )
        
        if not has_identity:
            errors.append("Missing identity information: need at least one of DNSHostName, SamAccountName, DistinguishedName, or DomainName")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _build_constraints(self, host: InputHost) -> Dict[str, Any]:
        """Build constraints object from host parameters."""
        return {
            "operating_system": host.OperatingSystem,
            "os_version": host.OperatingSystemVersion,
            "domain": host.DomainName,
            "spns": host.ServicePrincipalNames or [],
            "delegation": {
                "trusted_for_delegation": host.TrustedForDelegation,
                "trusted_to_auth_for_delegation": host.TrustedToAuthForDelegation,
                "tgt_delegation": host.TGTDelegation
            },
            "privileges": {
                "admin_count": host.adminCount,
                "member_of": host.MemberOf or []
            },
            "trust_relationships": {
                "source": host.Source,
                "target": host.Target,
                "trust_type": host.TrustType,
                "direction": host.Direction
            }
        }
    
    async def _call_llm_with_retry(
        self,
        stage_index: int,
        prompt: str,
        request_id: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Call LLM with retry logic.
        
        Args:
            stage_index: Current stage number
            prompt: Built prompt text
            request_id: Request identifier
            max_retries: Maximum retry attempts
            
        Returns:
            LLM response with status, content, usage, response_time
        """
        for attempt in range(max_retries):
            try:
                llm_start = time.time()
                response = await self.llm_client.complete(
                    system_message=PromptBuilder.SYSTEM_MESSAGE,
                    user_prompt=prompt,
                    json_mode=False
                )
                llm_time = int((time.time() - llm_start) * 1000)
                
                # Log token usage
                usage = response.get("usage", {})
                self.token_logger.log_call(
                    request_id=request_id,
                    call_type=f"stage_{stage_index}",
                    model=settings.LLM_MODEL,
                    tokens_input=usage.get("prompt_tokens", 0),
                    tokens_output=usage.get("completion_tokens", 0),
                    response_time_ms=llm_time
                )
                
                return {
                    "status": "success",
                    "content": response.get("content", ""),
                    "usage": usage,
                    "response_time_ms": llm_time
                }
                
            except Exception as e:
                print(f"         ✗ Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                if attempt == max_retries - 1:
                    return {
                        "status": "error",
                        "error": str(e)
                    }
                time.sleep(1)  # Brief delay before retry
        
        return {"status": "error", "error": "Max retries exceeded"}
    
    def _parse_stage_output(self, raw_output: str, stage_index: int, host: InputHost) -> Dict[str, Any]:
        """
        Parse LLM output into structured format and validate bifurcations.
        
        Args:
            raw_output: Raw text from LLM
            stage_index: Stage number
            host: Target host parameters for validation
            
        Returns:
            Parsed dictionary with technique, action, outcome, validated bifurcations, etc.
        """
        import re
        
        # Extract bifurcations
        bifurcations = []
        bifurcation_section = re.search(
            r'\*\*Bifurcations.*?\*\*:(.*?)(?=\n\n|\Z)', 
            raw_output, 
            re.DOTALL | re.IGNORECASE
        )
        
        if bifurcation_section:
            bifurcation_text = bifurcation_section.group(1)
            # Match patterns like: "1. [Technique Name] (X% probability)\n   - Description: ..."
            pattern = r'\d+\.\s*\[([^\]]+)\]\s*\((\d+)%.*?\)\s*-\s*Description:\s*([^\n]+(?:\n(?!\d+\.)[^\n]+)*)'
            matches = re.findall(pattern, bifurcation_text, re.MULTILINE)
            
            for idx, (technique, probability, description) in enumerate(matches):
                bifurcations.append({
                    "id": f"b{stage_index}-{idx + 1}",
                    "technique": technique.strip(),
                    "probability": float(probability) / 100.0,
                    "description": description.strip(),
                    "status": "not_generated"
                })
        
        # Validate bifurcations against target parameters
        if bifurcations:
            print(f"         → Validating {len(bifurcations)} bifurcations against target parameters")
            validated_bifurcations = self.exploitability_validator.validate_bifurcations(
                bifurcations=bifurcations,
                target_params=host.dict()  # Convert Pydantic model to dict
            )
            
            removed_count = len(bifurcations) - len(validated_bifurcations)
            if removed_count > 0:
                print(f"         ✗ Removed {removed_count} non-exploitable bifurcations")
            print(f"         ✓ {len(validated_bifurcations)} validated bifurcations")
            
            bifurcations = validated_bifurcations
        
        parsed = {
            "stage": stage_index,
            "raw_content": raw_output,
            "technique": self._extract_technique(raw_output),
            "action": self._extract_action(raw_output),
            "expected_outcome": self._extract_outcome(raw_output),
            "probability": self._extract_probability(raw_output),
            "objective_status": self._check_objective_status(raw_output),
            "bifurcations": bifurcations
        }
        
        return parsed
    
    def _extract_technique(self, text: str) -> str:
        """Extract technique name from output."""
        # Simple heuristic - look for "STATE N: [technique]"
        if "STATE" in text:
            lines = text.split("\n")
            for line in lines:
                if line.strip().startswith("##") and "STATE" in line:
                    return line.split(":", 1)[-1].strip() if ":" in line else "Unknown"
        return "Unknown"
    
    def _extract_action(self, text: str) -> str:
        """Extract main action/command from output."""
        # Look for "Action:" or "- Action:"
        for line in text.split("\n"):
            if "action:" in line.lower():
                return line.split(":", 1)[-1].strip()
        return "Not specified"
    
    def _extract_outcome(self, text: str) -> str:
        """Extract expected outcome."""
        for line in text.split("\n"):
            if "expected outcome:" in line.lower() or "outcome:" in line.lower():
                return line.split(":", 1)[-1].strip()
        return "Not specified"
    
    def _extract_probability(self, text: str) -> float:
        """Extract probability percentage."""
        import re
        # Look for patterns like "85% probability" or "(85%)"
        match = re.search(r'(\d+)%', text)
        if match:
            return float(match.group(1)) / 100.0
        return 0.5  # Default 50%
    
    def _check_objective_status(self, text: str) -> str:
        """Check if objective is reached."""
        text_lower = text.lower()
        achieved_keywords = [
            "objective achieved",
            "objective status:** achieved",
            "domain admin",
            "system access achieved",
            "full system compromise"
        ]
        
        if any(keyword in text_lower for keyword in achieved_keywords):
            return "achieved"
        return "in_progress"
    
    def _validate_stage_output(
        self,
        parsed: Dict[str, Any],
        constraints: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate parsed output against constraints.
        
        Args:
            parsed: Parsed stage result
            constraints: OS/security constraints
            context: Thread context
            
        Returns:
            Validation result
        """
        errors = []
        
        # Schema validation
        if not parsed.get("technique") or parsed["technique"] == "Unknown":
            errors.append("Missing or invalid technique")
        
        # Semantic validation - check for reconnaissance duplication
        if parsed.get("stage") == 0:
            content = parsed.get("raw_content", "").lower()
            if any(word in content for word in ["nmap", "port scan", "network scan"]):
                errors.append("Stage 0 should not include reconnaissance (already completed)")
        
        # OS compatibility validation - CRITICAL
        content = parsed.get("raw_content", "").lower()
        os_version = constraints.get("os_version", "").lower()
        
        # Check for Windows Server 2016+ incompatible exploits
        if any(version in os_version for version in ["2016", "2019", "2022", "server 2016", "server 2019"]):
            incompatible_exploits = [
                ("ms17-010", "MS17-010/EternalBlue only works on Windows 7-2012R2, not 2016+"),
                ("eternalblue", "EternalBlue only works on Windows 7-2012R2, not 2016+"),
                ("ms08-067", "MS08-067 only works on Windows XP/2003, not 2016+"),
                ("ms14-070", "MS14-070 only works on Server 2003-2012R2, not 2016+"),
                ("cve-2009", "CVE-2009 exploits target old systems (XP/2003), not 2016+")
            ]
            
            for exploit, error_msg in incompatible_exploits:
                if exploit in content:
                    errors.append(f"OS INCOMPATIBLE: {error_msg}")
        
        # Check for Windows Server 2012/2008 incompatible exploits
        if any(version in os_version for version in ["2012", "2008", "server 2012", "server 2008"]):
            if "ms08-067" in content:
                errors.append("OS INCOMPATIBLE: MS08-067 only works on Windows XP/2003, not 2008/2012")
        
        # CVE HALLUCINATION CHECK - CRITICAL
        # If configurations are present, reject ANY CVE mention
        has_configs = len(constraints.get("configurations", [])) > 0
        provided_vulns = constraints.get("provided_vulnerabilities", [])
        
        if has_configs:
            # Look for CVE patterns: CVE-YYYY-NNNNN or MS##-###
            import re
            cve_pattern = r'cve-\d{4}-\d{4,7}'
            ms_pattern = r'ms\d{2}-\d{3}'
            
            found_cves = re.findall(cve_pattern, content)
            found_ms = re.findall(ms_pattern, content)
            
            if found_cves:
                # Check if these CVEs were provided in input
                allowed_cves = [vuln.lower() for vuln in provided_vulns if 'cve-' in vuln.lower()]
                for cve in found_cves:
                    if cve not in allowed_cves:
                        errors.append(f"CVE HALLUCINATION: {cve.upper()} was NOT in reconnaissance. Focus on misconfigurations instead.")
            
            if found_ms:
                # Check if these MS bulletins were provided
                allowed_ms = [vuln.lower() for vuln in provided_vulns if 'ms' in vuln.lower()]
                for ms in found_ms:
                    if ms not in allowed_ms:
                        errors.append(f"CVE HALLUCINATION: {ms.upper()} was NOT in reconnaissance. Focus on misconfigurations instead.")
        
        # Check if inventing CVEs when misconfigurations are available
        if context.get("stage_index") == 0:  # Only for first stage
            has_configs = len(constraints.get("configurations", [])) > 0 if "configurations" in constraints else False
            has_cve_mentions = any(cve in content for cve in ["cve-", "ms17-", "ms08-", "ms14-"])
            
            if has_configs and has_cve_mentions:
                # This is acceptable but note it
                pass  # Allow CVE mentions even with configs, but configs should be prioritized
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _emit_telemetry(
        self,
        request_id: str,
        thread_id: str,
        stages_count: int,
        total_tokens: int,
        execution_time: float
    ):
        """Emit telemetry and logs for observability."""
        # In production, this would send to logging/monitoring systems
        telemetry = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "thread_id": thread_id,
            "stages_generated": stages_count,
            "total_tokens": total_tokens,
            "execution_time_seconds": round(execution_time, 2),
            "model": settings.LLM_MODEL
        }
        
        # For now, just print (in prod: send to metrics system)
        print(f"  [TELEMETRY] {json.dumps(telemetry, indent=2)}")
    
    def _error_response(
        self,
        request_id: str,
        error_type: str,
        message: Any
    ) -> Dict[str, Any]:
        """Build error response."""
        return {
            "request_id": request_id,
            "status": "error",
            "error_type": error_type,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
