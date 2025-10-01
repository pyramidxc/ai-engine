"""
Attack path analysis service.
Orchestrates the analysis workflow using LLM and prompt building.
"""
from app.models.host import InputHost
from app.models.analysis import AttackPathResponse
from app.services.llm_client import LLMClient
from app.core.prompts import PromptBuilder


class AttackPathAnalyzer:
    """Service for analyzing attack paths based on host data."""
    
    def __init__(self):
        """Initialize the analyzer with required services."""
        self.llm_client = LLMClient()
        self.prompt_builder = PromptBuilder()
    
    async def analyze(self, host: InputHost) -> AttackPathResponse:
        """
        Analyze a host and generate attack path.
        
        Args:
            host: Input host data to analyze
            
        Returns:
            Attack path analysis results
            
        Raises:
            ValueError: If LLM response is invalid
            Exception: For other analysis errors
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
            hostname=host.hostname,
            attack_path=analysis.get("attack_path", []),
            risk_level=analysis.get("risk_level", "Unknown"),
            recommendations=analysis.get("recommendations", [])
        )
