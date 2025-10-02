"""
Prompt building logic for LLM interactions.
Centralizes all prompt templates and construction for attack path generation.
"""
from app.models.host import InputHost


class PromptBuilder:
    """Builds prompts for attack path generation."""
    
    SYSTEM_MESSAGE = (
        "You are a MITRE ATT&CK and Cyber Kill Chain expert specializing in offensive security. "
        "Your role is to generate realistic, step-by-step attack sequences based on vulnerability "
        "and exposure data provided by external collectors. Structure attack paths following the "
        "Cyber Kill Chain phases and map each action to relevant MITRE ATT&CK techniques. "
        "Provide detailed technical descriptions and include code examples when applicable."
    )
    
    @staticmethod
    def build_attack_analysis_prompt(host: InputHost) -> str:
        """
        Build a prompt for attack path generation.
        
        Args:
            host: Input host data from external collector (platform, version_os, ports, services, vulnerabilities)
            
        Returns:
            Formatted prompt string for LLM to generate attack sequence
        """
        ports_text = (
            ', '.join(map(str, host.open_ports)) 
            if host.open_ports 
            else 'None detected'
        )
        
        services_text = (
            '\n  • '.join(host.services) 
            if host.services 
            else 'None detected'
        )
        
        vulns_text = (
            '\n  • '.join(host.vulnerabilities) 
            if host.vulnerabilities 
            else 'None detected'
        )
        
        prompt = f"""Generate a realistic attack path for the following target based on collected vulnerability and exposure data.

Target Information (from external collector):
- Platform: {host.platform}
- OS Version: {host.version_os}
- Open Ports: {ports_text}
- Services:
  • {services_text}
- Known Vulnerabilities:
  • {vulns_text}

Your task:
1. Generate a detailed, step-by-step attack path following the Cyber Kill Chain phases
2. Map each action to relevant MITRE ATT&CK techniques (TTP - Tactics, Techniques, and Procedures)
3. Provide technical details and include code examples when applicable
4. Assess the overall risk level based on exploitability and impact

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
        "Reconnaissance: [Detailed description of information gathering phase with MITRE mapping, e.g., T1595.002 - Active Scanning: Vulnerability Scanning. Example: nmap -sV -sC <target> to enumerate services and OS version]",
        
        "Weaponization: [Description of exploit/payload preparation with MITRE mapping and tool details]",
        
        "Delivery: [Description of delivery vector with MITRE mapping and technical approach]",
        
        "Exploitation: [Detailed exploitation with CVE, commands, code examples, and MITRE mapping, e.g., T1190 - Exploit Public-Facing Application]",
        
        "Installation: [Description of persistence mechanism with commands/code and MITRE mapping, e.g., T1053.005 - Scheduled Task]",
        
        "Command and Control: [C2 setup details with tools, protocols, and MITRE mapping, e.g., T1071.001 - Web Protocols]",
        
        "Actions on Objectives: [Description of final goals with techniques and MITRE mapping, e.g., T1005 - Data from Local System, T1048 - Exfiltration Over Alternative Protocol]"
    ],
    "risk_level": "Critical|High|Medium|Low"
}}

Risk Level Criteria:
- Critical: Remote code execution, full system compromise, or data breach highly likely with easily exploitable vulnerabilities
- High: Privilege escalation or significant data access possible with moderate exploitation complexity
- Medium: Limited access achievable or requires additional steps/credentials/user interaction
- Low: Minimal impact or highly complex exploitation requiring multiple preconditions

Rules:
- Always return a valid JSON object with keys "attack_path" and "risk_level"
- Each attack_path element must be a single string describing one Cyber Kill Chain phase
- Always map actions to equivalent MITRE ATT&CK technique IDs (T####) to add analytical value
- Include code examples, commands, or technical details when describing exploitation and post-exploitation
- Ensure output is valid, parseable JSON with no additional text outside the JSON structure

Generate a realistic attack sequence now."""
        
        return prompt
