"""
Prompt building logic for LLM interactions.
Centralizes all prompt templates and construction.
"""
from app.models.host import InputHost


class PromptBuilder:
    """Builds prompts for LLM analysis."""
    
    SYSTEM_MESSAGE = (
        "You are a cybersecurity expert specializing in attack path analysis "
        "and penetration testing."
    )
    
    @staticmethod
    def build_attack_analysis_prompt(host: InputHost) -> str:
        """
        Build a prompt for attack path analysis.
        
        Args:
            host: Input host data containing hostname, ports, and vulnerabilities
            
        Returns:
            Formatted prompt string for the LLM
        """
        ports_text = (
            ', '.join(map(str, host.open_ports)) 
            if host.open_ports 
            else 'None detected'
        )
        
        vulns_text = (
            ', '.join(host.vulnerabilities) 
            if host.vulnerabilities 
            else 'None detected'
        )
        
        prompt = f"""You are a cybersecurity expert analyzing a host for potential attack paths.

Host Information:
- Hostname: {host.hostname}
- Open Ports: {ports_text}
- Known Vulnerabilities: {vulns_text}

Based on this information, provide:
1. A step-by-step attack path that an attacker might follow
2. The overall risk level (Critical, High, Medium, Low)
3. Security recommendations to mitigate the risks

Format your response as JSON with the following structure:
{{
    "attack_path": ["step 1", "step 2", "step 3", ...],
    "risk_level": "High|Medium|Low|Critical",
    "recommendations": ["recommendation 1", "recommendation 2", ...]
}}

Be specific and technical. Each attack path step should describe what an attacker would do."""
        
        return prompt
