"""
Prompt building logic for LLM interactions.
Centralizes all prompt templates and construction for attack path generation.
"""
from app.models.host import InputHost


class PromptBuilder:
    """Builds dynamic prompts for attack path generation based on available data."""
    
    SYSTEM_MESSAGE = (
        "You are a MITRE ATT&CK and Cyber Kill Chain expert specializing in offensive security. "
        "Your role is to generate realistic, step-by-step attack sequences based on vulnerability "
        "and exposure data provided by external collectors. Structure attack paths following the "
        "Cyber Kill Chain phases and map each action to relevant MITRE ATT&CK techniques. "
        "Provide detailed technical descriptions and include code examples when applicable. "
        "Tailor your attack path based on the specific context provided - consider security controls, "
        "network segmentation, identity management, and all available asset details."
    )
    
    @staticmethod
    def _format_list(items: list | None, default: str = "None detected") -> str:
        """Format a list for display, handling None and empty lists."""
        if not items:
            return default
        return '\n  • ' + '\n  • '.join(str(item) for item in items)
    
    @staticmethod
    def _format_value(value, default: str = "Not specified") -> str:
        """Format a single value for display."""
        if value is None:
            return default
        if isinstance(value, bool):
            return "Yes" if value else "No"
        return str(value)
    
    @staticmethod
    def build_attack_analysis_prompt(host: InputHost) -> str:
        """
        Build a dynamic prompt for attack path generation.
        
        Intelligently constructs the prompt based on available data fields.
        Only includes sections where data is provided, making the prompt
        concise and relevant to the specific host context.
        
        Args:
            host: Input host data from external collector
            
        Returns:
            Formatted prompt string for LLM to generate attack sequence
        """
        pb = PromptBuilder  # Alias for shorter calls
        
        # Build sections dynamically based on available data
        sections = []
        
        # ==================== CORE SYSTEM INFO ====================
        if host.platform or host.version_os:
            core_info = []
            if host.platform:
                core_info.append(f"- Platform: {host.platform}")
            if host.version_os:
                core_info.append(f"- OS Version: {host.version_os}")
            if host.os_end_of_life:
                core_info.append(f"- ⚠️ OS END-OF-LIFE: System is running unsupported OS version")
            sections.append("=== CORE SYSTEM INFO ===\n" + "\n".join(core_info))
        
        # ==================== ASSET IDENTIFICATION ====================
        asset_info = []
        if host.asset_name:
            asset_info.append(f"- Asset Name: {host.asset_name}")
        if host.asset_id:
            asset_info.append(f"- Asset ID: {host.asset_id}")
        if host.fqdn:
            asset_info.append(f"- FQDN: {host.fqdn}")
        if host.ip_addresses:
            asset_info.append(f"- IP Addresses: {', '.join(host.ip_addresses)}")
        if host.mac_addresses:
            asset_info.append(f"- MAC Addresses: {', '.join(host.mac_addresses)}")
        
        if asset_info:
            sections.append("=== ASSET IDENTIFICATION ===\n" + "\n".join(asset_info))
        
        # ==================== ASSET CONTEXT & RISK ====================
        context_info = []
        if host.asset_criticality:
            context_info.append(f"- 🎯 Asset Criticality: {host.asset_criticality}")
        if host.business_role:
            context_info.append(f"- Business Role: {host.business_role}")
        if host.environment:
            context_info.append(f"- Environment: {host.environment}")
        if host.data_classification:
            context_info.append(f"- Data Classification: {host.data_classification}")
        
        if context_info:
            sections.append("=== ASSET CONTEXT (HIGH PRIORITY FOR RISK ASSESSMENT) ===\n" + "\n".join(context_info))
        
        # ==================== NETWORK & EXPOSURE ====================
        network_info = []
        if host.network_segment:
            network_info.append(f"- Network Segment: {host.network_segment}")
        if host.internet_exposed is not None:
            exposure = "YES - Exposed to Internet 🌐" if host.internet_exposed else "No - Internal only"
            network_info.append(f"- Internet Exposed: {exposure}")
        if host.open_ports:
            network_info.append(f"- Open Ports: {', '.join(map(str, host.open_ports))}")
        if host.services:
            network_info.append(f"- Services:{pb._format_list(host.services)}")
        if host.firewall_rules:
            network_info.append(f"- Firewall Rules:{pb._format_list(host.firewall_rules)}")
        
        if network_info:
            sections.append("=== NETWORK & EXPOSURE ===\n" + "\n".join(network_info))
        
        # ==================== SECURITY CONTROLS ====================
        security_info = []
        if host.security_controls:
            security_info.append(f"- Security Controls:{pb._format_list(host.security_controls)}")
        if host.edr_agent:
            security_info.append(f"- EDR Agent: {host.edr_agent}")
        if host.antivirus_status:
            security_info.append(f"- Antivirus Status: {host.antivirus_status}")
        if host.firewall_status:
            security_info.append(f"- Firewall Status: {host.firewall_status}")
        if host.encryption_status:
            security_info.append(f"- Disk Encryption: {host.encryption_status}")
        
        if security_info:
            sections.append("=== SECURITY CONTROLS (CONSIDER FOR EVASION) ===\n" + "\n".join(security_info))
        
        # ==================== VULNERABILITIES & PATCH STATUS ====================
        vuln_info = []
        if host.vulnerabilities:
            vuln_info.append(f"- Known Vulnerabilities:{pb._format_list(host.vulnerabilities)}")
        if host.vulnerability_score is not None:
            vuln_info.append(f"- Vulnerability Score: {host.vulnerability_score}")
        if host.critical_vuln_count is not None:
            vuln_info.append(f"- Critical Vulnerabilities: {host.critical_vuln_count}")
        if host.patch_level:
            vuln_info.append(f"- Patch Level: {host.patch_level}")
        if host.missing_patches:
            vuln_info.append(f"- Missing Patches:{pb._format_list(host.missing_patches)}")
        
        if vuln_info:
            sections.append("=== VULNERABILITIES & PATCH STATUS ===\n" + "\n".join(vuln_info))
        
        # ==================== IDENTITY & ACCESS MANAGEMENT ====================
        identity_info = []
        if host.domain_membership:
            identity_info.append(f"- Domain: {host.domain_membership}")
        if host.organizational_unit:
            identity_info.append(f"- Organizational Unit: {host.organizational_unit}")
        if host.user_accounts:
            identity_info.append(f"- User Accounts:{pb._format_list(host.user_accounts)}")
        if host.admin_accounts:
            identity_info.append(f"- 🔑 Admin Accounts:{pb._format_list(host.admin_accounts)}")
        if host.service_accounts:
            identity_info.append(f"- Service Accounts:{pb._format_list(host.service_accounts)}")
        if host.mfa_enabled is not None:
            mfa = "Enabled ✓" if host.mfa_enabled else "NOT ENABLED ⚠️"
            identity_info.append(f"- Multi-Factor Authentication: {mfa}")
        if host.password_policy:
            identity_info.append(f"- Password Policy: {host.password_policy}")
        
        if identity_info:
            sections.append("=== IDENTITY & ACCESS MANAGEMENT ===\n" + "\n".join(identity_info))
        
        # ==================== INSTALLED SOFTWARE ====================
        software_info = []
        if host.installed_software:
            software_info.append(f"- Installed Software:{pb._format_list(host.installed_software)}")
        if host.database_software:
            software_info.append(f"- Database Software:{pb._format_list(host.database_software)}")
        if host.development_tools:
            software_info.append(f"- Development Tools:{pb._format_list(host.development_tools)}")
        if host.browser_extensions:
            software_info.append(f"- Browser Extensions:{pb._format_list(host.browser_extensions)}")
        
        if software_info:
            sections.append("=== INSTALLED SOFTWARE (ADDITIONAL ATTACK VECTORS) ===\n" + "\n".join(software_info))
        
        # ==================== MISCONFIGURATIONS ====================
        config_info = []
        if host.configurations:
            config_info.append(f"- ⚠️ Misconfigurations:{pb._format_list(host.configurations)}")
        if host.security_recommendations:
            config_info.append(f"- Security Recommendations:{pb._format_list(host.security_recommendations)}")
        if host.compliance_gaps:
            config_info.append(f"- Compliance Gaps:{pb._format_list(host.compliance_gaps)}")
        
        if config_info:
            sections.append("=== MISCONFIGURATIONS & WEAKNESSES ===\n" + "\n".join(config_info))
        
        # ==================== CLOUD & CONTAINER ====================
        cloud_info = []
        if host.cloud_provider:
            cloud_info.append(f"- Cloud Provider: {host.cloud_provider}")
        if host.cloud_instance_type:
            cloud_info.append(f"- Instance Type: {host.cloud_instance_type}")
        if host.cloud_iam_roles:
            cloud_info.append(f"- IAM Roles:{pb._format_list(host.cloud_iam_roles)}")
        if host.container_runtime:
            cloud_info.append(f"- Container Runtime: {host.container_runtime}")
        if host.kubernetes_cluster:
            cloud_info.append(f"- Kubernetes Cluster: {host.kubernetes_cluster}")
        
        if cloud_info:
            sections.append("=== CLOUD & CONTAINER ENVIRONMENT ===\n" + "\n".join(cloud_info))
        
        # ==================== BACKUP & RECOVERY ====================
        backup_info = []
        if host.backup_system:
            backup_info.append(f"- Backup System: {host.backup_system}")
        if host.backup_location:
            backup_info.append(f"- Backup Location: {host.backup_location}")
        
        if backup_info:
            sections.append("=== BACKUP & RECOVERY (POTENTIAL EXFILTRATION TARGET) ===\n" + "\n".join(backup_info))
        
        # ==================== THREAT INTELLIGENCE ====================
        threat_info = []
        if host.threat_intel_matches:
            threat_info.append(f"- 🔴 Threat Intel Matches:{pb._format_list(host.threat_intel_matches)}")
        if host.known_exploits:
            threat_info.append(f"- Known Exploits:{pb._format_list(host.known_exploits)}")
        
        if threat_info:
            sections.append("=== THREAT INTELLIGENCE ===\n" + "\n".join(threat_info))
        
        # Build the complete prompt
        target_info = "\n\n".join(sections) if sections else "Minimal information available - generate generic attack path"
        
        prompt = f"""Generate a realistic attack path for the following target based on collected vulnerability and exposure data.

TARGET INFORMATION (from external collector):

{target_info}

YOUR TASK:
1. Generate a detailed, step-by-step attack path following the Cyber Kill Chain phases
2. Map each action to relevant MITRE ATT&CK techniques (TTP - Tactics, Techniques, and Procedures)
3. **CRITICAL**: Tailor the attack path to the SPECIFIC CONTEXT provided above:
   - If security controls (EDR, firewall) are present, include evasion techniques
   - If cloud/container environments are detected, include cloud-native attack techniques
   - If misconfigurations are listed, exploit them specifically
   - If admin accounts are identified, target them for privilege escalation
   - If MFA is disabled, note easier credential access
   - If asset criticality is high, emphasize the business impact
   - Consider network segmentation for lateral movement strategies
4. Provide technical details and include code examples when applicable
5. Assess the overall risk level based on exploitability, impact, AND asset criticality

Attack Path Structure - Follow Cyber Kill Chain Phases:

1. **Reconnaissance**: Collect public and observable information about the target to identify assets, services, and potential exposure (passive, non-actionable). Map to MITRE techniques like T1595 (Active Scanning), T1592 (Gather Victim Host Information).

2. **Weaponization**: Design or select a capability or payload tailored to observed weaknesses. Describe the attack tools or exploits prepared. Map to relevant MITRE techniques.

3. **Delivery**: Describe the vector used to deliver the capability to the target (e.g., network exploitation, phishing, direct service attack). Map to MITRE techniques like T1566 (Phishing), T1190 (Exploit Public-Facing Application).

4. **Exploitation**: Trigger vulnerability or misconfiguration to gain initial access. Include specific exploitation techniques, CVE details, and code examples where applicable. Map to MITRE Initial Access techniques.

5. **Installation**: Establish persistent foothold by deploying tools, backdoors, or mechanisms. Describe installation methods and tools used. Map to MITRE Persistence techniques like T1543 (Create or Modify System Process), T1053 (Scheduled Task).

6. **Command and Control (C2)**: Define the channel for remote control and coordination. Include protocols, tools (e.g., Metasploit, Cobalt Strike, custom C2), and communication methods. Map to MITRE C2 techniques like T1071 (Application Layer Protocol), T1573 (Encrypted Channel).

7. **Actions on Objectives**: Describe goals achieved after establishing control such as data access, lateral movement, privilege escalation, data exfiltration, or system disruption. Map to MITRE techniques like T1003 (Credential Dumping), T1021 (Remote Services), T1567 (Exfiltration Over Web Service).

Guidelines:
- Each step must be a single, detailed string describing one concrete attacker action
- Include technical specifics: commands, tools, protocols, file paths when relevant
- Add code examples for exploitation and post-exploitation phases
- Map each phase to specific MITRE ATT&CK technique IDs (T####)
- Number of steps should reflect a realistic progression for the given vulnerabilities
- Ensure logical flow from reconnaissance through objectives
- Be realistic about what an attacker could achieve with the given attack surface

Format your response as JSON with this exact structure:
{{
    "attack_path": [
        "Reconnaissance: [Detailed description with SPECIFIC context from target info, MITRE mapping]",
        "Weaponization: [Description considering security controls present, MITRE mapping]",
        "Delivery: [Description considering network exposure and segmentation, MITRE mapping]",
        "Exploitation: [Detailed exploitation of SPECIFIC vulnerabilities/misconfigurations listed, with CVE, commands, code examples, MITRE mapping]",
        "Installation: [Persistence mechanism considering EDR/security controls, MITRE mapping]",
        "Command and Control: [C2 setup considering firewall rules and network monitoring, MITRE mapping]",
        "Actions on Objectives: [Goals considering asset criticality and data classification, MITRE mapping]"
    ]
}}

Rules:
- Always return a valid JSON object with key "attack_path"
- Each attack_path element must be a single string describing one Cyber Kill Chain phase
- Always map actions to equivalent MITRE ATT&CK technique IDs (T####)
- **REFERENCE SPECIFIC CONTEXT**: Use actual details from the target information (e.g., specific CVEs, account names, software versions, misconfigurations)
- Include code examples, commands, or technical details when describing exploitation
- Ensure output is valid, parseable JSON with no additional text outside the JSON structure

Generate a realistic, context-aware attack sequence now."""
        
        return prompt
