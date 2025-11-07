"""Probabilistic Attack Tree Analysis Service.

Generates dynamic, context-aware attack paths as decision trees with
probability-weighted alternatives at each state.

This replaces the rigid 7-stage pipeline with an adaptive state machine
that generates realistic attack paths of varying complexity (3-15+ states).
"""
import time
import uuid
from typing import Dict

from app.config import settings
from app.core.prompts import PromptBuilder
from app.models.host import InputHost
from app.services.llm_client import LLMClient
from app.utils.token_logger import get_token_logger


class AttackTreeAnalyzer:
    """
    Generates probabilistic attack trees with dynamic state progression.
    
    Unlike the old 7-stage system, this analyzer:
    - Generates variable-length attack paths (3-15+ states)
    - Shows probability-weighted decision points
    - Adapts to actual target complexity
    - Provides main path + alternative branches
    """
    
    def __init__(self):
        """Initialize the attack tree analyzer."""
        self.prompt_builder = PromptBuilder()
        self.llm_client = LLMClient()
        self.token_logger = get_token_logger()
    
    async def analyze(self, host: InputHost) -> Dict:
        """
        Generate probabilistic attack tree for the target using orchestrated state progression.
        
        Uses an orchestrator pattern:
        - Generate one state at a time
        - Validate and parse each state
        - Decide whether to continue based on current state
        - Stop when objective reached or max states hit
        
        Args:
            host: Target host information from collector
            
        Returns:
            Dictionary containing:
            - reconnaissance: Formatted recon summary
            - states: List of attack states with decisions
            - metadata: Execution time, tokens used, etc.
        """
        request_id = str(uuid.uuid4())
        self._request_id = request_id
        
        start_time = time.time()
        
        print(f"\n{'='*60}")
        print("Starting Probabilistic Attack Tree Analysis")
        print(f"Request ID: {request_id}")
        print(f"{'='*60}\n")
        
        # Step 1: Build reconnaissance summary (no LLM - just formatting)
        print("  → Parsing reconnaissance data...")
        recon_summary = self.prompt_builder.build_reconnaissance_summary(host)
        
        # Step 2: Orchestrated state generation
        states = []
        current_context = {
            "reconnaissance": recon_summary,
            "previous_states": []
        }
        
        max_states = 15  # Safety limit
        total_tokens = 0
        
        for state_index in range(max_states):
            print(f"  → Generating State {state_index}...")
            
            # Build prompt for current state
            state_prompt = self.prompt_builder.build_state_prompt(
                host=host,
                state_index=state_index,
                context=current_context
            )
            
            # Call LLM for this state
            llm_start = time.time()
            response = await self.llm_client.complete(
                system_message=PromptBuilder.SYSTEM_MESSAGE,
                user_prompt=state_prompt,
                json_mode=False
            )
            llm_time = int((time.time() - llm_start) * 1000)
            
            state_content = response.get("content", "")
            usage = response.get("usage", {})
            total_tokens += usage.get("total_tokens", 0)
            
            # Log token usage for this state
            self.token_logger.log_call(
                request_id=request_id,
                call_type=f"state_{state_index}",
                model=settings.LLM_MODEL,
                tokens_input=usage.get("prompt_tokens", 0),
                tokens_output=usage.get("completion_tokens", 0),
                response_time_ms=llm_time
            )
            
            # Parse state and check if objective reached
            state_data = {
                "state_index": state_index,
                "content": state_content,
                "tokens": usage.get("total_tokens", 0),
                "response_time_ms": llm_time
            }
            
            states.append(state_data)
            current_context["previous_states"].append(state_content)
            
            # Orchestrator decision: Should we continue?
            if self._is_objective_reached(state_content) or state_index >= 10:
                print("  → Objective reached or sufficient states generated")
                break
        
        total_time = time.time() - start_time
        
        print(f"\n{'='*60}")
        print("Attack Tree Analysis Complete")
        print(f"Total States: {len(states)}")
        print(f"Execution Time: {total_time:.2f} seconds")
        print(f"Total Tokens: {total_tokens}")
        print(f"{'='*60}\n")
        
        return {
            "request_id": request_id,
            "reconnaissance": recon_summary,
            "states": states,
            "metadata": {
                "execution_time_seconds": round(total_time, 2),
                "total_states": len(states),
                "tokens_total": total_tokens,
                "model": settings.LLM_MODEL
            }
        }
    
    def _is_objective_reached(self, state_content: str) -> bool:
        """
        Orchestrator decision: Check if attack objective is reached.
        
        Args:
            state_content: Content of the current state
            
        Returns:
            True if objective reached, False otherwise
        """
        # Simple heuristics - can be improved
        objective_keywords = [
            "full system compromise",
            "domain admin",
            "system access achieved",
            "root access",
            "administrator access",
            "objective achieved",
            "complete control"
        ]
        
        content_lower = state_content.lower()
        return any(keyword in content_lower for keyword in objective_keywords)
    
    def format_markdown(self, analysis_result: Dict) -> str:
        """
        Format the orchestrated attack tree analysis as markdown.
        
        Args:
            analysis_result: Dictionary from analyze() containing states
            
        Returns:
            Formatted markdown document
        """
        recon = analysis_result["reconnaissance"]
        states = analysis_result["states"]
        metadata = analysis_result["metadata"]
        
        # Build markdown with reconnaissance + all states
        sections = [
            "# Probabilistic Attack Tree Analysis",
            "",
            "---",
            "",
            "## Reconnaissance Summary",
            "",
            recon,
            "",
            "---",
            "",
            "## Attack Progression",
            ""
        ]
        
        # Add each state
        for state in states:
            sections.append(state["content"])
            sections.append("")
        
        # Add metadata footer
        sections.extend([
            "---",
            "",
            "## Analysis Metadata",
            "",
            f"- **Total States Generated:** {metadata['total_states']}",
            f"- **Execution Time:** {metadata['execution_time_seconds']}s",
            f"- **Total Tokens Used:** {metadata['tokens_total']}",
            f"- **Model:** `{metadata['model']}`",
            ""
        ])
        
        return "\n".join(sections)
