"""Attack path generation service.
Orchestrates the generation workflow using LLM and prompt building.
"""
from app.models.host import InputHost
from app.models.analysis import AttackPathResponse
from app.services.llm_client import LLMClient
from app.core.prompts import PromptBuilder


class AttackPathAnalyzer:
    """Service for generating attack paths from host exposure data."""
    
    def __init__(self):
        """Initialize the generator with required services."""
        self.llm_client = LLMClient()
        self.prompt_builder = PromptBuilder()
    
    async def analyze(self, host: InputHost) -> AttackPathResponse:
        """
        Generate attack path from host exposure data.
        
        Args:
            host: Input host data from external collector
            
        Returns:
            Generated attack path with risk assessment
            
        Raises:
            ValueError: If LLM response is invalid
            Exception: For other generation errors
        """
        # Build prompt
        user_prompt = self.prompt_builder.build_attack_analysis_prompt(host)
        
        # Get analysis from LLM
        analysis = await self.llm_client.complete(
            system_message=self.prompt_builder.SYSTEM_MESSAGE,
            user_prompt=user_prompt,
            json_mode=True
        )
        
        # Validate and build response
        return AttackPathResponse(
            platform=host.platform,
            version_os=host.version_os,
            attack_path=analysis.get("attack_path", []),
            risk_level=analysis.get("risk_level", "Unknown")
        )
