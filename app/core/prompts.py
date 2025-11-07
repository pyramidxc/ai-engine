"""
Prompt building logic for LLM interactions - Attack Path Generation.
Minimal, principle-based prompts that rely on model reasoning, not prescribed rules.
"""
from typing import Dict

from app.models.host import InputHost


class PromptBuilder:
    """Builds prompts for attack path generation."""
    
    SYSTEM_MESSAGE = (
        "You are an expert penetration tester analyzing security reconnaissance data "
        "to generate realistic attack paths. You understand offensive security fundamentals, "
        "operating system internals, network protocols, and how different platforms/services work.\n\n"
        
        "CORE PRINCIPLES:\n"
        "1. Understand the target platform and what's actually possible on it\n"
        "2. Base all decisions on the provided reconnaissance data\n"
        "3. Provide probabilistic assessments: main path + alternatives with likelihood\n"
        "4. Use appropriate techniques for the specific environment\n"
        "5. Build on previous state - each step should logically follow\n\n"
        
        "OUTPUT FORMAT:\n"
        "For each state, provide:\n"
        "- Current access level\n"
        "- Main attack action (with probability)\n"
        "- Alternative actions (with probabilities)\n"
        "- Technical details (commands, tools)\n"
        "- Expected outcome\n\n"
        
        "Think like a real penetration tester who understands how systems actually work."
    )
    
    @staticmethod
    def _format_list(items: list | None, default: str = "None detected") -> str:
        """Format a list for display, handling None and empty lists."""
        if not items:
            return default
        return '\n  • ' + '\n  • '.join(str(item) for item in items)
    
    @staticmethod
    def build_reconnaissance_summary(host: InputHost) -> str:
        """
        Build reconnaissance summary from collector data.
        This is NOT an LLM call - just formatting the input data.
        
        Args:
            host: Input host data from external collector
            
        Returns:
            Formatted reconnaissance summary
        """
        pb = PromptBuilder
        sections = []
        
        # Core system info
        if host.platform or host.version_os:
            core = []
            if host.platform:
                core.append(f"Platform: {host.platform}")
            if host.version_os:
                core.append(f"OS Version: {host.version_os}")
            if host.os_end_of_life:
                core.append("⚠️ OS IS END-OF-LIFE (unsupported, likely unpatched)")
            sections.append("=== SYSTEM ===\n" + "\n".join(core))
        
        # Network exposure
        if host.internet_exposed is not None or host.open_ports:
            network = []
            if host.internet_exposed:
                network.append("⚠️ INTERNET-EXPOSED")
            if host.open_ports:
                network.append(f"Open Ports: {', '.join(map(str, host.open_ports))}")
            if host.services:
                network.append(f"Services: {pb._format_list(host.services)}")
            sections.append("=== NETWORK ===\n" + "\n".join(network))
        
        # Vulnerabilities
        if host.vulnerabilities:
            sections.append(f"=== VULNERABILITIES ===\n{pb._format_list(host.vulnerabilities)}")
        
        # Security controls
        if host.security_controls or host.edr_agent or host.antivirus_status:
            security = []
            if host.security_controls:
                security.append(f"Controls: {pb._format_list(host.security_controls)}")
            if host.edr_agent:
                security.append(f"EDR: {host.edr_agent}")
            if host.antivirus_status:
                security.append(f"Antivirus: {host.antivirus_status}")
            sections.append("=== SECURITY CONTROLS ===\n" + "\n".join(security))
        
        # Identity & access
        if host.domain_membership or host.user_accounts or host.mfa_enabled is not None:
            identity = []
            if host.domain_membership:
                identity.append(f"Domain: {host.domain_membership}")
            if host.user_accounts:
                identity.append(f"Users: {pb._format_list(host.user_accounts)}")
            if host.admin_accounts:
                identity.append(f"⚠️ Admin Accounts: {pb._format_list(host.admin_accounts)}")
            if host.mfa_enabled is not None:
                identity.append(f"MFA: {'Enabled' if host.mfa_enabled else '⚠️ DISABLED'}")
            sections.append("=== IDENTITY & ACCESS ===\n" + "\n".join(identity))
        
        # Asset criticality
        if host.asset_criticality or host.business_role:
            criticality = []
            if host.asset_criticality:
                criticality.append(f"⚠️ Criticality: {host.asset_criticality}")
            if host.business_role:
                criticality.append(f"Role: {host.business_role}")
            sections.append("=== ASSET IMPORTANCE ===\n" + "\n".join(criticality))
        
        return "\n\n".join(sections)
    
    @staticmethod
    def build_state_prompt(host: InputHost, state_index: int, context: Dict) -> str:
        """Generates prompt for a specific attack state."""
        recon_summary = PromptBuilder.build_reconnaissance_summary(host)
        
        prompt_parts = []
        prompt_parts.append("=== RECONNAISSANCE DATA ===")
        prompt_parts.append(recon_summary)
        prompt_parts.append("")
        
        # Current state context
        if state_index == 0:
            prompt_parts.append("=== CURRENT STATE: Initial Access ===")
            prompt_parts.append("Starting from external attacker perspective.")
        else:
            prompt_parts.append(f"=== CURRENT STATE: Step {state_index + 1} ===")
            if "previous_actions" in context:
                prompt_parts.append("Previous actions taken:")
                for action in context["previous_actions"]:
                    prompt_parts.append(f"  • {action}")
            if "current_access" in context:
                prompt_parts.append(f"Current access level: {context['current_access']}")
        
        prompt_parts.append("")
        prompt_parts.append("=== YOUR TASK ===")
        prompt_parts.append("Based on the reconnaissance data and current state, determine:")
        prompt_parts.append("1. What's the best next action? (with probability)")
        prompt_parts.append("2. What are viable alternatives? (with probabilities)")
        prompt_parts.append("3. How would you execute each approach?")
        prompt_parts.append("4. What access would each approach gain?")
        
        return "\n".join(prompt_parts)
    
    @staticmethod
    def build_attack_tree_prompt(host: InputHost) -> str:
        """Generates complete attack tree generation prompt."""
        recon_summary = PromptBuilder.build_reconnaissance_summary(host)
        
        return f"""=== RECONNAISSANCE DATA ===
{recon_summary}

=== YOUR TASK ===
Generate a complete attack path from initial access to final objective.

For each step, provide:
1. Main action (with probability)
2. Alternative approaches (with probabilities)
3. Technical execution details
4. Expected outcomes

Start with initial access and progress logically based on what each step achieves."""
    
    @staticmethod
    def build_full_attack_tree_prompt(host: InputHost) -> str:
        """Generates prompt for complete attack tree (legacy compatibility)."""
        # For now, use same minimal approach as build_attack_tree_prompt
        return PromptBuilder.build_attack_tree_prompt(host)
