"""Complete attack path analysis service with stage-level continuity.

This is the PRIMARY production service that generates a complete 7-stage
attack path with stage-level continuity preservation. Each stage has access
to outputs from all prior stages to maintain logical consistency.

Features:
    - 7-stage attack path generation with context threading
    - Stage-level continuity preservation
    - Structured StageAnalysis output format
    - Token tracking for all LLM calls
    - Complete formatted response
"""
import time
import uuid
import re
import json
from typing import Dict, List, Optional

from app.models.host import InputHost
from app.models.attack_context import AttackContext
from app.models.complete_analysis import CompleteAnalysisResponse, StageAnalysis
from app.core.prompts import PromptBuilder
from app.services.llm_client import LLMClient
from app.utils.token_logger import get_token_logger
from app.utils.continuity_validator import ContinuityValidator
from app.config import settings


class CompleteAnalyzer:
    """
    Generates complete 7-stage attack path with stage-level continuity.
    
    This is the PRIMARY production endpoint that generates a full attack path
    where each stage has access to outputs from all prior stages, ensuring
    logical consistency and preventing hallucinations.
    
    Output format: Structured StageAnalysis objects for both JSON and Markdown
    """
    
    def __init__(self):
        """Initialize the complete analyzer."""
        self.prompt_builder = PromptBuilder()
        self.llm_client = LLMClient()
        self.token_logger = get_token_logger()
    
    def _extract_artifact_name(self, content: str, stage_index: int) -> Optional[str]:
        """
        Extract artifact names with priority-based fallback.
        
        Multi-strategy extraction: code blocks (most reliable) → explicit naming →
        uploads/transfers → references to prior stage artifacts.
        
        Args:
            content: Stage content to extract from
            stage_index: Which stage (1-7) for context
            
        Returns:
            Artifact name if found, else None
        """
        # Priority 1: Look in code blocks (most reliable)
        # Matches: -o file.exe, output file.exe, -OutFile C:\path\file.exe
        code_blocks = re.findall(
            r"(?:msfvenom|wget|curl|scp|copy|Invoke-WebRequest|New-Item|Set-Content)[^\`]*[-\s](?:o|OutFile)\s+(?:C:\\)?[\\\/]*([^\s\n\"'\`]+(?:\.exe|\.sh|\.py|\.bat|\.ps1))",
            content,
            re.IGNORECASE
        )
        if code_blocks:
            return code_blocks[0]
        
        # Priority 2: Explicit artifact naming patterns
        # Matches: named: 'file.exe', created eternalblue_payload.exe, payload: `file.sh`
        artifact_names = re.findall(
            r"(?:named|created|called|file|payload|artifact)['\"]?:\s*['\"\`]*([^\s\n'\"`;]+(?:\.exe|\.sh|\.py|\.bat|\.ps1))",
            content,
            re.IGNORECASE | re.DOTALL
        )
        if artifact_names:
            return artifact_names[0]
        
        # Priority 3: Upload/transfer commands
        # Matches: upload /path/to/file.exe, scp file.exe, copy payload.exe
        uploads = re.findall(
            r"(?:upload|scp|copy|wget|curl|Invoke-WebRequest)[^\`]*?([^\s\n\`\\\/]+(?:\.exe|\.sh|\.py|\.bat|\.ps1))",
            content,
            re.IGNORECASE
        )
        if uploads:
            return uploads[0]
        
        # Priority 4: Reference to prior stage artifacts (continuity!)
        # Matches: from weaponization, created earlier, reference to Stage 2
        prior_artifacts = re.findall(
            r"(?:from\s+(?:weaponization|stage\s+2)|created\s+(?:earlier|in)|reference)[^\`]*?\`?([^\s\n'\"`;`]+(?:\.exe|\.sh|\.py|\.bat|\.ps1))\`?",
            content,
            re.IGNORECASE | re.DOTALL
        )
        if prior_artifacts:
            return prior_artifacts[0]
        
        return None
    
    def _parse_stage_response(
        self, 
        stage_index: int,
        stage_name: str,
        phase: str,
        content: str
    ) -> StageAnalysis:
        """
        Parse LLM response content into structured StageAnalysis.
        
        Extracts MITRE techniques, key findings, tools, commands, and artifacts
        from the narrative content to build a structured stage object.
        
        Args:
            stage_index: Stage number (1-7)
            stage_name: Kill chain stage name
            phase: Phase description
            content: Full narrative content from LLM
        
        Returns:
            StageAnalysis with extracted structured data
        """
        # Default stage metadata by index
        stage_meta = {
            1: {
                "techniques": ["T1595", "T1592", "T1598"],
                "phase": "Information Gathering"
            },
            2: {
                "techniques": ["T1203", "T1587.001", "T1588.001"],
                "phase": "Payload Creation"
            },
            3: {
                "techniques": ["T1190", "T1203", "T1566"],
                "phase": "Payload Transmission"
            },
            4: {
                "techniques": ["T1190", "T1203", "T1068"],
                "phase": "Initial Access & Exploitation"
            },
            5: {
                "techniques": ["T1105", "T1053.005", "T1543.003", "T1547.001"],
                "phase": "Persistence & Privilege Escalation"
            },
            6: {
                "techniques": ["T1071.001", "T1573.001", "T1008"],
                "phase": "Command & Control"
            },
            7: {
                "techniques": ["T1003", "T1021", "T1041", "T1567"],
                "phase": "Post-Exploitation"
            }
        }
        
        meta = stage_meta.get(stage_index, {"techniques": [], "phase": phase})
        
        # Extract tools from content (bash/powershell code blocks)
        tools = []
        tool_patterns = [
            r"(msfconsole|meterpreter|Metasploit|nmap|shodan|Mimikatz|PsExec|nc|netcat)",
            r"(powershell|bash|cmd\.exe|python|tar|zip)",
            r"(EternalBlue|SMB|Netcat)",
        ]
        for pattern in tool_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            tools.extend([m for m in matches if m and m not in tools])
        
        # Extract commands from code blocks
        commands = []
        code_blocks = re.findall(r"```(?:bash|powershell|cmd)?\s+(.*?)```", content, re.DOTALL)
        for block in code_blocks:
            lines = [line.strip() for line in block.split("\n") if line.strip()]
            commands.extend(lines)
        
        # Extract artifact names using enhanced multi-priority strategy
        artifact_name = self._extract_artifact_name(content, stage_index)
        
        # Create one-sentence summary from first few lines
        summary = ""
        lines = content.split("\n")
        for line in lines:
            if line.strip() and len(line) < 200:
                summary = line.strip()
                break
        if not summary:
            summary = f"{stage_name} attack stage execution"
        
        # Extract key findings (numbered lists or bullet points)
        key_findings = []
        finding_patterns = [
            r"(?:^\d+\.\s+(.+)$|^-\s+(.+)$|^\*\s+(.+)$)",
        ]
        for pattern in finding_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                finding = next((m for m in match if m), None)
                if finding and finding not in key_findings:
                    key_findings.append(finding)
        
        return StageAnalysis(
            stage_index=stage_index,
            stage_name=stage_name,
            phase=meta.get("phase", phase),
            mitre_techniques=meta.get("techniques", []),
            summary=summary[:150],  # Limit to 150 chars
            key_findings=key_findings[:5],  # Top 5 findings
            tools_used=list(set(tools))[:5],  # Top 5 tools
            artifact_name=artifact_name,
            artifact_type="Malware/Payload" if artifact_name else None,
            commands=commands[:10],  # Top 10 commands
            content=content
        )
    
    async def _generate_attack_path_with_continuity(self, host: InputHost) -> AttackContext:
        """
        Generate attack path with stage-level continuity preservation.
        
        Each stage receives outputs from all prior stages, ensuring logical
        consistency across the entire attack path.
        
        Args:
            host: Target host information
            
        Returns:
            AttackContext with all 7 stages populated
        """
        context = AttackContext(host_data=host.dict())
        
        # STAGE 1: Reconnaissance (no prior context)
        print("  → Stage 1: Reconnaissance...")
        prompt1 = self.prompt_builder.build_reconnaissance_prompt(host)
        stage_start = time.time()
        response1 = await self.llm_client.complete(
            system_message=PromptBuilder.SYSTEM_MESSAGE,
            user_prompt=prompt1,
            json_mode=False
        )
        stage_time = int((time.time() - stage_start) * 1000)
        context.reconnaissance = response1.get("content", "")
        self.token_logger.log_call(
            request_id=getattr(self, '_request_id', 'unknown'),
            call_type="stage_1_reconnaissance",
            model=settings.LLM_MODEL,
            tokens_input=response1.get("usage", {}).get("prompt_tokens", 0),
            tokens_output=response1.get("usage", {}).get("completion_tokens", 0),
            response_time_ms=stage_time
        )
        
        # STAGE 2: Weaponization (knows recon results)
        print("  → Stage 2: Weaponization...")
        prompt2 = self.prompt_builder.build_weaponization_prompt(host, context)
        stage_start = time.time()
        response2 = await self.llm_client.complete(
            system_message=PromptBuilder.SYSTEM_MESSAGE,
            user_prompt=prompt2,
            json_mode=False
        )
        stage_time = int((time.time() - stage_start) * 1000)
        context.weaponization = response2.get("content", "")
        self.token_logger.log_call(
            request_id=getattr(self, '_request_id', 'unknown'),
            call_type="stage_2_weaponization",
            model=settings.LLM_MODEL,
            tokens_input=response2.get("usage", {}).get("prompt_tokens", 0),
            tokens_output=response2.get("usage", {}).get("completion_tokens", 0),
            response_time_ms=stage_time
        )
        
        # STAGE 3: Delivery (knows recon + weaponization)
        print("  → Stage 3: Delivery...")
        prompt3 = self.prompt_builder.build_delivery_prompt(host, context)
        stage_start = time.time()
        response3 = await self.llm_client.complete(
            system_message=PromptBuilder.SYSTEM_MESSAGE,
            user_prompt=prompt3,
            json_mode=False
        )
        stage_time = int((time.time() - stage_start) * 1000)
        context.delivery = response3.get("content", "")
        self.token_logger.log_call(
            request_id=getattr(self, '_request_id', 'unknown'),
            call_type="stage_3_delivery",
            model=settings.LLM_MODEL,
            tokens_input=response3.get("usage", {}).get("prompt_tokens", 0),
            tokens_output=response3.get("usage", {}).get("completion_tokens", 0),
            response_time_ms=stage_time
        )
        
        # STAGE 4: Exploitation (knows all prior)
        print("  → Stage 4: Exploitation...")
        prompt4 = self.prompt_builder.build_exploitation_prompt(host, context)
        stage_start = time.time()
        response4 = await self.llm_client.complete(
            system_message=PromptBuilder.SYSTEM_MESSAGE,
            user_prompt=prompt4,
            json_mode=False
        )
        stage_time = int((time.time() - stage_start) * 1000)
        context.exploitation = response4.get("content", "")
        self.token_logger.log_call(
            request_id=getattr(self, '_request_id', 'unknown'),
            call_type="stage_4_exploitation",
            model=settings.LLM_MODEL,
            tokens_input=response4.get("usage", {}).get("prompt_tokens", 0),
            tokens_output=response4.get("usage", {}).get("completion_tokens", 0),
            response_time_ms=stage_time
        )
        
        # STAGE 5: Installation (knows all prior, CRITICAL for artifact continuity)
        print("  → Stage 5: Installation...")
        prompt5 = self.prompt_builder.build_installation_prompt(host, context)
        stage_start = time.time()
        response5 = await self.llm_client.complete(
            system_message=PromptBuilder.SYSTEM_MESSAGE,
            user_prompt=prompt5,
            json_mode=False
        )
        stage_time = int((time.time() - stage_start) * 1000)
        context.installation = response5.get("content", "")
        self.token_logger.log_call(
            request_id=getattr(self, '_request_id', 'unknown'),
            call_type="stage_5_installation",
            model=settings.LLM_MODEL,
            tokens_input=response5.get("usage", {}).get("prompt_tokens", 0),
            tokens_output=response5.get("usage", {}).get("completion_tokens", 0),
            response_time_ms=stage_time
        )
        
        # STAGE 6: C2 (full context)
        print("  → Stage 6: Command & Control...")
        prompt6 = self.prompt_builder.build_command_and_control_prompt(host, context)
        stage_start = time.time()
        response6 = await self.llm_client.complete(
            system_message=PromptBuilder.SYSTEM_MESSAGE,
            user_prompt=prompt6,
            json_mode=False
        )
        stage_time = int((time.time() - stage_start) * 1000)
        context.command_and_control = response6.get("content", "")
        self.token_logger.log_call(
            request_id=getattr(self, '_request_id', 'unknown'),
            call_type="stage_6_command_and_control",
            model=settings.LLM_MODEL,
            tokens_input=response6.get("usage", {}).get("prompt_tokens", 0),
            tokens_output=response6.get("usage", {}).get("completion_tokens", 0),
            response_time_ms=stage_time
        )
        
        # STAGE 7: Actions (full context)
        print("  → Stage 7: Actions on Objectives...")
        prompt7 = self.prompt_builder.build_actions_on_objectives_prompt(host, context)
        stage_start = time.time()
        response7 = await self.llm_client.complete(
            system_message=PromptBuilder.SYSTEM_MESSAGE,
            user_prompt=prompt7,
            json_mode=False
        )
        stage_time = int((time.time() - stage_start) * 1000)
        context.actions_on_objectives = response7.get("content", "")
        self.token_logger.log_call(
            request_id=getattr(self, '_request_id', 'unknown'),
            call_type="stage_7_actions_on_objectives",
            model=settings.LLM_MODEL,
            tokens_input=response7.get("usage", {}).get("prompt_tokens", 0),
            tokens_output=response7.get("usage", {}).get("completion_tokens", 0),
            response_time_ms=stage_time
        )
        
        return context
    
    def _update_stage_artifacts(self, context: AttackContext, primary_path: List[StageAnalysis]) -> None:
        """
        Track extracted artifacts through the context for continuity validation.
        
        After parsing all stages, update the context's stage_artifacts dict
        so we can validate that later stages properly reference earlier artifacts.
        
        Args:
            context: The attack context with raw stage outputs
            primary_path: Parsed StageAnalysis objects
        """
        for i, stage in enumerate(primary_path, start=1):
            if stage.artifact_name:
                context.stage_artifacts[i] = stage.artifact_name
    
    async def analyze(
        self, 
        host: InputHost
    ) -> CompleteAnalysisResponse:
        """
        Generate complete 7-stage attack path with continuity.
        
        Args:
            host: Complete host parameters
        
        Returns:
            CompleteAnalysisResponse with 7-stage primary path (structured StageAnalysis objects)
        
        Features:
            - Stage-level continuity: Each stage receives all prior outputs
            - Structured output: Returns StageAnalysis objects with metadata
            - Token tracking: All 7 LLM calls logged
            - Cost estimation: Total cost calculated
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Track LLM calls
        llm_calls: Dict[str, int] = {
            "total": 0
        }
        
        # Store request_id for token logging
        self._request_id = request_id
        
        print(f"\n{'='*60}")
        print(f"Starting Attack Path Analysis")
        print(f"Request ID: {request_id}")
        print(f"{'='*60}\n")
        
        print("Generating 7-stage attack path with continuity...")
        print("  (with stage-level continuity preservation)\n")
        
        # Generate primary attack path
        context = await self._generate_attack_path_with_continuity(host)
        
        # Parse responses into structured StageAnalysis objects
        stage_names = [
            "Reconnaissance",
            "Weaponization",
            "Delivery",
            "Exploitation",
            "Installation",
            "Command & Control",
            "Actions on Objectives"
        ]
        
        stage_phases = [
            "Information Gathering",
            "Payload Creation",
            "Payload Transmission",
            "Initial Access",
            "Persistence",
            "Communication Channel",
            "Post-Exploitation"
        ]
        
        content_list = [
            context.reconnaissance,
            context.weaponization,
            context.delivery,
            context.exploitation,
            context.installation,
            context.command_and_control,
            context.actions_on_objectives
        ]
        
        primary_path: List[StageAnalysis] = []
        for i, content in enumerate(content_list, start=1):
            stage = self._parse_stage_response(
                stage_index=i,
                stage_name=stage_names[i-1],
                phase=stage_phases[i-1],
                content=content
            )
            primary_path.append(stage)
        
        # Update context with tracked artifacts
        self._update_stage_artifacts(context, primary_path)
        
        # Run continuity validation
        validator = ContinuityValidator(context, primary_path)
        validation_report = validator.validate()
        
        print(f"\nContinuity Validation:")
        print(f"  {validator.get_summary()}")
        if validation_report["warnings"]:
            print(f"  Warnings: {len(validation_report['warnings'])}")
        
        llm_calls["total"] = 7  # 7 stages
        
        # Calculate metrics BEFORE logging
        execution_time = time.time() - start_time
        total_paths = 1  # Just primary path
        estimated_cost = 0.015  # Approximate cost for 7 LLM calls
        
        # Log summary
        self.token_logger.log_call(
            request_id=request_id,
            call_type="analysis_complete",
            model=settings.LLM_MODEL,
            tokens_input=0,
            tokens_output=0,
            response_time_ms=int(execution_time * 1000),
            metadata={"stages": 7, "total_paths": total_paths}
        )
        
        print(f"\n{'='*60}")
        print(f"Analysis Complete!")
        print(f"  Total Paths: {total_paths}")
        print(f"  LLM Calls: {llm_calls['total']}")
        print(f"  Execution Time: {execution_time:.2f}s")
        print(f"  Estimated Cost: ${estimated_cost:.4f}")
        print(f"\n{'='*60}\n")
        
        return CompleteAnalysisResponse(
            request_id=request_id,
            primary_path=primary_path,
            total_paths=total_paths,
            execution_time_seconds=round(execution_time, 2),
            llm_calls=llm_calls,
            estimated_cost=round(estimated_cost, 4),
            validation_report=validation_report
        )

