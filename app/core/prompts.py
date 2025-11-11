"""
Prompt building logic for LLM interactions - Attack Path Generation.
Minimal, principle-based prompts that rely on model reasoning, not prescribed rules.
"""
from typing import Dict

from app.models.host import InputHost


class PromptBuilder:
    """Builds prompts for attack path generation."""
    
    SYSTEM_MESSAGE = (
        "You are an expert security analyst generating attack path analysis based on provided reconnaissance data and instructions. "
        "Follow the instructions precisely and base all decisions on the provided data."
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
        if host.OperatingSystem or host.OperatingSystemVersion:
            core = []
            if host.OperatingSystem:
                core.append(f"Operating System: {host.OperatingSystem}")
            if host.OperatingSystemVersion:
                core.append(f"OS Version: {host.OperatingSystemVersion}")
            if host.OperatingSystemServicePack:
                core.append(f"Service Pack: {host.OperatingSystemServicePack}")
            if host.OperatingSystemHotfix:
                core.append(f"Installed Hotfixes: {pb._format_list(host.OperatingSystemHotfix)}")
            sections.append("=== SYSTEM ===\n" + "\n".join(core))
        
        # Network & identity
        if host.DNSHostName or host.IPv4Address or host.DomainName:
            network = []
            if host.DNSHostName:
                network.append(f"DNS Hostname: {host.DNSHostName}")
            if host.IPv4Address:
                network.append(f"IP Address: {host.IPv4Address}")
            if host.DomainName:
                network.append(f"⚠️ Domain: {host.DomainName}")
            sections.append("=== NETWORK & IDENTITY ===\n" + "\n".join(network))
        
        # Asset identification
        if host.SamAccountName or host.DistinguishedName:
            asset = []
            if host.SamAccountName:
                asset.append(f"Account Name: {host.SamAccountName}")
            if host.DistinguishedName:
                asset.append(f"Distinguished Name: {host.DistinguishedName}")
            if host.objectSid:
                asset.append(f"SID: {host.objectSid}")
            sections.append("=== ASSET IDENTIFICATION ===\n" + "\n".join(asset))
        
        # Kerberos & delegation
        if host.ServicePrincipalNames or host.TrustedForDelegation or host.TrustedToAuthForDelegation:
            kerberos = []
            if host.ServicePrincipalNames:
                kerberos.append(f"⚠️ Service Principal Names: {pb._format_list(host.ServicePrincipalNames)}")
            if host.TrustedForDelegation:
                kerberos.append("⚠️ TRUSTED FOR DELEGATION (High Risk!)")
            if host.TrustedToAuthForDelegation:
                kerberos.append("⚠️ CONSTRAINED DELEGATION ENABLED")
            if host.TGTDelegation:
                kerberos.append("⚠️ TGT DELEGATION ALLOWED")
            sections.append("=== KERBEROS & DELEGATION ===\n" + "\n".join(kerberos))
        
        # Security controls & privileges
        if host.adminCount or host.PasswordNeverExpires or host.Enabled is not None:
            security = []
            if host.adminCount == 1:
                security.append("⚠️ PRIVILEGED ACCOUNT (adminCount=1)")
            if host.Enabled is not None:
                security.append(f"Account Status: {'Enabled' if host.Enabled else 'Disabled'}")
            if host.PasswordNeverExpires:
                security.append("⚠️ PASSWORD NEVER EXPIRES")
            if host.ProtectedFromAccidentalDeletion:
                security.append("Protected from Deletion: Yes")
            sections.append("=== SECURITY CONTROLS ===\n" + "\n".join(security))
        
        # Group membership & access
        if host.MemberOf or host.Members:
            groups = []
            if host.MemberOf:
                groups.append(f"⚠️ Member Of: {pb._format_list(host.MemberOf)}")
            if host.Members:
                groups.append(f"Group Members: {pb._format_list(host.Members)}")
            sections.append("=== GROUP MEMBERSHIP ===\n" + "\n".join(groups))
        
        # GPO configuration
        if host.LinkedGroupPolicyObjects or host.DisplayName or host.GpoStatus:
            gpo = []
            if host.DisplayName:
                gpo.append(f"GPO Name: {host.DisplayName}")
            if host.GpoStatus:
                gpo.append(f"GPO Status: {host.GpoStatus}")
            if host.LinkedGroupPolicyObjects:
                gpo.append(f"Linked GPOs: {pb._format_list(host.LinkedGroupPolicyObjects)}")
            if host.WmiFilter:
                gpo.append(f"WMI Filter: {host.WmiFilter}")
            sections.append("=== GROUP POLICY ===\n" + "\n".join(gpo))
        
        # Trust relationships
        if host.Target or host.Source or host.TrustType:
            trust = []
            if host.Source:
                trust.append(f"Source Domain: {host.Source}")
            if host.Target:
                trust.append(f"Target Domain: {host.Target}")
            if host.Direction:
                trust.append(f"Trust Direction: {host.Direction}")
            if host.TrustType:
                trust.append(f"Trust Type: {host.TrustType}")
            if host.ForestTransitive:
                trust.append("⚠️ FOREST TRANSITIVE TRUST")
            if host.SelectiveAuthentication:
                trust.append("Selective Authentication: Enabled")
            if host.SIDFilteringForestAware:
                trust.append("SID Filtering: Enabled")
            sections.append("=== TRUST RELATIONSHIPS ===\n" + "\n".join(trust))
        
        # Risk indicators
        if host.lastLogonTimestamp:
            sections.append(f"=== LAST LOGON ===\nTimestamp: {host.lastLogonTimestamp}")
        
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
        
        return "\n".join(prompt_parts)
