"""
Host-related data models.

This module defines the input data structure for the Attack Path Engine.
It uses Pydantic for data validation and type safety, ensuring that all
incoming data from external vulnerability collectors is properly validated.

The InputHost model accepts 50+ optional parameters organized into 12 categories,
allowing flexible integration with various data sources while maintaining
a consistent interface.

Design Philosophy:
    - All fields are optional (no required fields except indirectly)
    - More context = better attack path generation
    - Supports partial data from any vulnerability scanner
    - Backward compatible with any subset of parameters

Architecture Role:
    - Data Layer component
    - Defines API contract for input data
    - Provides validation and type safety
    - Self-documenting via Field descriptions

Usage:
    >>> # Minimal input
    >>> host = InputHost(platform="Linux", open_ports=[22, 80])
    
    >>> # Rich input
    >>> host = InputHost(
    ...     platform="Linux",
    ...     version_os="Ubuntu 20.04",
    ...     asset_criticality="High",
    ...     mfa_enabled=False,
    ...     security_controls=["CrowdStrike EDR"],
    ...     vulnerabilities=["CVE-2023-12345"]
    ... )
"""
from typing import Optional
from pydantic import BaseModel, Field


# =============================================================================
# Input Host Model
# =============================================================================

class InputHost(BaseModel):
    """
    Input model for host exposure data from external vulnerability collectors.
    
    This model defines the complete data structure accepted by the Attack Path
    Engine. It supports 50+ optional parameters organized into 12 logical
    categories, allowing flexible integration with various data sources.
    
    Key Features:
        - All 50+ fields are optional for maximum flexibility
        - Organized into logical categories for clarity
        - Self-documenting with detailed Field descriptions
        - Supports any combination of parameters
        - Example included for API documentation
    
    Design Rationale:
        The optional nature of all fields allows the engine to work with:
        - Minimal scanner output (just platform + ports)
        - Rich CMDB data (comprehensive asset context)
        - Partial data from multiple sources
        - Any combination in between
    
    Integration Examples:
        - Nmap: platform, open_ports, services
        - OpenVAS: vulnerabilities, services, patch_level
        - CMDB: asset_name, criticality, business_role
        - Cloud API: cloud_provider, iam_roles, instance_type
        - EDR: security_controls, installed_software
    
    Parameter Categories:
        1. Core System Info (2 params)
        2. Network & Services (3 params)
        3. Asset Identification (5 params)
        4. Network Context (3 params)
        5. Security Controls (5 params)
        6. Identity & Access (7 params)
        7. Software & Applications (4 params)
        8. Patch & Vulnerability (5 params)
        9. Configuration & Compliance (3 params)
        10. Asset Context & Risk (4 params)
        11. Cloud & Containers (5 params)
        12. Backup & Storage (2 params)
        13. Threat Intelligence (2 params)
    
    Total Parameters: 50+
    
    Example:
        >>> # Create minimal input
        >>> minimal = InputHost(platform="Linux", open_ports=[22, 80])
        >>> print(minimal.platform)
        'Linux'
        
        >>> # Create comprehensive input
        >>> comprehensive = InputHost(
        ...     platform="Linux",
        ...     version_os="Ubuntu 20.04.3 LTS",
        ...     asset_name="web-prod-01",
        ...     asset_criticality="Critical",
        ...     internet_exposed=True,
        ...     open_ports=[22, 80, 443, 3306],
        ...     services=["SSH", "Apache", "MySQL"],
        ...     vulnerabilities=["CVE-2023-12345: SQL Injection"],
        ...     security_controls=["CrowdStrike Falcon EDR"],
        ...     mfa_enabled=False,
        ...     admin_accounts=["root", "dbadmin"],
        ...     patch_level="Missing critical patches",
        ...     environment="Production"
        ... )
        >>> print(comprehensive.asset_criticality)
        'Critical'
    
    See Also:
        - docs/INPUT_PARAMETERS.md: Complete parameter reference
        - test_scenarios/: Example JSON files with various parameter combinations
    """
    
    # =============================================================================
    # CATEGORY 1: CORE SYSTEM INFO
    # =============================================================================
    # Fundamental OS information - typically available from any scanner.
    # These are often the starting points for attack path generation.
    
    platform: Optional[str] = Field(
        None,
        description="Operating system platform (e.g., Linux, Windows, macOS)"
        # Examples: "Linux", "Windows", "macOS", "AIX", "Solaris"
        # Source: Nmap OS detection, SCCM, Nessus, OpenVAS
    )
    version_os: Optional[str] = Field(
        None,
        description="Operating system version (e.g., Ubuntu 20.04, Windows Server 2019)"
        # Examples: "Ubuntu 20.04.3 LTS", "Windows Server 2019", "macOS 12.3.1"
        # Used for: Identifying version-specific vulnerabilities and exploits
    )
    
    # =============================================================================
    # CATEGORY 2: NETWORK & SERVICES
    # =============================================================================
    # Network exposure and running services - critical for attack surface analysis.
    # Used to identify potential entry points and lateral movement paths.
    
    open_ports: Optional[list[int]] = Field(
        default=None,
        description="List of open ports detected on the host"
        # Examples: [22, 80, 443, 3306, 5432, 8080]
        # Source: Nmap, Masscan, network scanners
        # Impact: Each open port is a potential attack vector
    )
    services: Optional[list[str]] = Field(
        default=None,
        description="Services running on open ports (e.g., 'SSH on port 22', 'Apache 2.4.41 on port 80')"
        # Examples: ["OpenSSH 8.2p1 on port 22", "Apache httpd 2.4.41 on port 80"]
        # Source: Nmap service detection, Nessus, OpenVAS
        # Used for: Service-specific vulnerability mapping
    )
    vulnerabilities: Optional[list[str]] = Field(
        default=None,
        description="Known vulnerabilities (CVEs, descriptions, etc.)"
        # Examples: ["CVE-2023-12345: SQL Injection", "CVE-2022-67890: RCE in Apache"]
        # Source: Nessus, OpenVAS, Qualys, Tenable
        # Critical for: Direct exploit path identification
    )
    
    # =============================================================================
    # CATEGORY 3: ASSET IDENTIFICATION
    # =============================================================================
    # Unique identifiers and naming information - used for asset correlation
    # and tracking across different data sources.
    
    asset_id: Optional[str] = Field(
        None,
        description="Unique asset identifier"
        # Examples: "ASSET-12345", "a1b2c3d4-e5f6-7890"
        # Source: CMDB, Asset Management systems
    )
    asset_name: Optional[str] = Field(
        None,
        description="Device hostname or asset name"
        # Examples: "web-prod-01", "db-server-nyc", "john-laptop"
        # Source: DNS, DHCP, host configuration
    )
    mac_addresses: Optional[list[str]] = Field(
        default=None,
        description="MAC addresses for network identification"
        # Examples: ["00:1A:2B:3C:4D:5E", "AA:BB:CC:DD:EE:FF"]
        # Source: Network scanners, DHCP logs, switch MAC tables
    )
    ip_addresses: Optional[list[str]] = Field(
        default=None,
        description="IP addresses (IPv4/IPv6)"
        # Examples: ["10.0.1.50", "203.0.113.42", "2001:db8::1"]
        # Source: Network scanners, DHCP, DNS
        # Note: Multiple IPs common for multi-homed hosts
    )
    fqdn: Optional[str] = Field(
        None,
        description="Fully qualified domain name"
        # Examples: "web-prod-01.corp.example.com", "mail.example.com"
        # Source: DNS, host configuration
    )
    
    # =============================================================================
    # CATEGORY 4: NETWORK CONTEXT
    # =============================================================================
    # Network positioning and exposure - critical for understanding attack surface.
    # Determines whether external or internal attack paths are more realistic.
    
    network_segment: Optional[str] = Field(
        None,
        description="Network segment (e.g., DMZ, Internal, Isolated, Public-facing)"
        # Examples: "DMZ", "Internal", "Production", "Guest Network", "OT/SCADA"
        # Source: CMDB, Network diagrams, VLAN configuration
        # Impact: DMZ/Public = external attacks, Internal = lateral movement
    )
    internet_exposed: Optional[bool] = Field(
        None,
        description="Whether the asset is exposed to the internet"
        # Values: True (public IP, NAT forwarding), False (internal only)
        # Source: Firewall rules, Shodan, external scans
        # Critical: Determines initial access vectors
    )
    firewall_rules: Optional[list[str]] = Field(
        default=None,
        description="Firewall configuration and rules"
        # Examples: ["Allow TCP 443 from 0.0.0.0/0", "Block TCP 22 except from 10.0.0.0/8"]
        # Source: Firewall configs, security policies
        # Used for: Understanding access restrictions
    )
    
    # =============================================================================
    # CATEGORY 5: SECURITY CONTROLS
    # =============================================================================
    # Defensive mechanisms in place - determines attack difficulty and bypass strategies.
    # Presence/absence of controls directly influences attack path feasibility.
    
    security_controls: Optional[list[str]] = Field(
        default=None,
        description="Security solutions (e.g., CrowdStrike EDR, Palo Alto Firewall, Windows Defender)"
        # Examples: ["CrowdStrike Falcon EDR - Active", "Palo Alto NGFW", "Windows Defender"]
        # Source: EDR consoles, SCCM, security tool inventory
        # Impact: Each control requires specific bypass techniques
    )
    edr_agent: Optional[str] = Field(
        None,
        description="EDR/antivirus agent name and status"
        # Examples: "CrowdStrike Falcon - Active", "Carbon Black - Outdated", "None"
        # Source: Endpoint management tools
        # Critical: EDR presence forces attackers to use evasion techniques
    )
    antivirus_status: Optional[str] = Field(
        None,
        description="Antivirus status (Active, Disabled, Not Installed)"
        # Values: "Active", "Disabled", "Outdated", "Not Installed"
        # Source: Windows Security Center, endpoint management
    )
    firewall_status: Optional[str] = Field(
        None,
        description="Firewall status (Enabled, Disabled)"
        # Values: "Enabled", "Disabled", "Misconfigured"
        # Source: Host firewall config (iptables, Windows Firewall)
    )
    encryption_status: Optional[str] = Field(
        None,
        description="Disk encryption status (e.g., BitLocker Enabled, FileVault, LUKS)"
        # Examples: "BitLocker Enabled", "FileVault Active", "Not Encrypted"
        # Source: Encryption management tools
        # Impact: Limits offline attack vectors
    )
    
    # =============================================================================
    # CATEGORY 6: IDENTITY & ACCESS
    # =============================================================================
    # User accounts and authentication mechanisms - key for privilege escalation
    # and lateral movement paths. Weak IAM is a common attack vector.
    
    domain_membership: Optional[str] = Field(
        None,
        description="Active Directory domain or workgroup"
        # Examples: "corp.example.com", "WORKGROUP", "child.corp.example.com"
        # Source: Active Directory, host configuration
        # Impact: Domain membership enables Kerberos attacks, GPO abuse
    )
    organizational_unit: Optional[str] = Field(
        None,
        description="Active Directory OU path"
        # Examples: "OU=Servers,OU=Production,DC=corp,DC=example,DC=com"
        # Source: Active Directory queries
        # Used for: Understanding GPO application and admin access patterns
    )
    user_accounts: Optional[list[str]] = Field(
        default=None,
        description="Local and domain user accounts"
        # Examples: ["CORP\\john.doe", "root", "administrator", "service_user"]
        # Source: Local account enumeration, AD queries
    )
    admin_accounts: Optional[list[str]] = Field(
        default=None,
        description="Privileged/administrator accounts"
        # Examples: ["root", "Administrator", "CORP\\domain_admins"]
        # Source: Group membership queries, sudoers file
        # Critical: Primary targets for privilege escalation
    )
    service_accounts: Optional[list[str]] = Field(
        default=None,
        description="Service account names"
        # Examples: ["svc_sql", "apache", "jenkins", "CORP\\svc_backup"]
        # Source: Process lists, service configurations
        # Risk: Often have weak passwords or excessive permissions
    )
    mfa_enabled: Optional[bool] = Field(
        None,
        description="Multi-factor authentication enabled"
        # Values: True (MFA enforced), False (password only)
        # Source: IAM policies, authentication logs
        # Impact: MFA absence = easier credential-based attacks
    )
    password_policy: Optional[str] = Field(
        None,
        description="Password policy strength (e.g., Weak, Strong, Complex, None)"
        # Examples: "Complex (14+ chars, special chars)", "Weak (no requirements)", "None"
        # Source: GPO, /etc/security/pwquality.conf, PAM configuration
        # Impact: Weak policies enable brute force and password spray attacks
    )
    
    # =============================================================================
    # CATEGORY 7: SOFTWARE & APPLICATIONS
    # =============================================================================
    # Installed software inventory - each application is a potential attack vector.
    # Development tools and databases are particularly high-value targets.
    
    installed_software: Optional[list[str]] = Field(
        default=None,
        description="Installed applications and tools"
        # Examples: ["Microsoft Office 2019", "Adobe Reader DC", "7-Zip 19.00"]
        # Source: SCCM, package managers (apt, yum, chocolatey), WMI queries
        # Used for: Identifying vulnerable software versions
    )
    browser_extensions: Optional[list[str]] = Field(
        default=None,
        description="Browser extensions (potential attack vector)"
        # Examples: ["LastPass 4.82.0", "Grammarly", "uBlock Origin"]
        # Source: Browser policy queries, user profiles
        # Risk: Malicious or vulnerable extensions enable browser-based attacks
    )
    database_software: Optional[list[str]] = Field(
        default=None,
        description="Database systems installed"
        # Examples: ["MySQL 5.7.33", "PostgreSQL 13.2", "MongoDB 4.4.6", "Redis 6.2.1"]
        # Source: Process lists, service enumeration
        # Critical: Databases often contain sensitive data and have default credentials
    )
    development_tools: Optional[list[str]] = Field(
        default=None,
        description="Development tools (Git, Docker, Jenkins, etc.)"
        # Examples: ["Docker 20.10.12", "Jenkins 2.346.1", "Git 2.34.1", "kubectl 1.23.5"]
        # Source: Command availability checks, process lists
        # High-risk: Dev tools often have admin access and weak security configs
    )
    
    # =============================================================================
    # CATEGORY 8: PATCH & VULNERABILITY MANAGEMENT
    # =============================================================================
    # Patch status and vulnerability metrics - directly indicates exploitability.
    # Missing patches and high CVSS scores correlate with successful attacks.
    
    patch_level: Optional[str] = Field(
        None,
        description="Patch status (e.g., Up-to-date, Outdated, Critical gaps)"
        # Examples: "Up-to-date", "Missing critical patches from last 6 months", "Never patched"
        # Source: WSUS, SCCM, apt/yum update checks
        # Impact: Outdated systems = known exploits available
    )
    missing_patches: Optional[list[str]] = Field(
        default=None,
        description="Specific missing patches or KB IDs"
        # Examples: ["KB5012345", "MS17-010 (EternalBlue)", "CVE-2023-12345 patch"]
        # Source: Vulnerability scanners, patch management systems
        # Critical: Identifies specific exploitable gaps
    )
    os_end_of_life: Optional[bool] = Field(
        None,
        description="Whether OS is end-of-life/unsupported"
        # Values: True (Windows 7, Ubuntu 16.04), False (current support)
        # Source: OS version cross-reference with vendor support dates
        # Impact: EOL systems = no security updates = guaranteed vulnerabilities
    )
    vulnerability_score: Optional[float] = Field(
        None,
        description="CVSS or VPR risk score"
        # Examples: 9.8 (critical), 7.5 (high), 4.3 (medium)
        # Source: Vulnerability scanners (CVSS v3, Tenable VPR)
        # Range: 0.0-10.0 (higher = more severe)
    )
    critical_vuln_count: Optional[int] = Field(
        None,
        description="Number of critical vulnerabilities"
        # Examples: 0 (clean), 5 (concerning), 25 (severe exposure)
        # Source: Vulnerability scanner aggregation
        # Impact: High count = multiple exploitation paths available
    )
    
    # =============================================================================
    # CATEGORY 9: CONFIGURATION & COMPLIANCE
    # =============================================================================
    # Security misconfigurations and compliance issues - often easier to exploit
    # than CVE vulnerabilities. Configuration errors are extremely common.
    
    configurations: Optional[list[str]] = Field(
        default=None,
        description="Misconfigurations or security weaknesses"
        # Examples: ["Docker socket exposed on 0.0.0.0:2375", "SSH allows root login",
        #           "Jenkins /script endpoint without auth", "Default credentials"]
        # Source: Configuration audits, security baselines (CIS, STIG)
        # Critical: Misconfigurations often enable direct exploitation
    )
    compliance_gaps: Optional[list[str]] = Field(
        default=None,
        description="Compliance violations (PCI-DSS, HIPAA, SOC2, etc.)"
        # Examples: ["PCI-DSS: No audit logging", "HIPAA: Unencrypted PHI storage",
        #           "SOC2: No MFA for admin access"]
        # Source: Compliance scanners, audit reports
        # Impact: Gaps indicate security control failures
    )
    security_recommendations: Optional[list[str]] = Field(
        default=None,
        description="Recommended security improvements"
        # Examples: ["Enable MFA for all admin accounts", "Segment database network",
        #           "Remove exposed Docker API", "Update to latest OS version"]
        # Source: Vulnerability scanner output, security assessments
        # Used for: Understanding known weaknesses and required fixes
    )
    
    # =============================================================================
    # CATEGORY 10: ASSET CONTEXT & RISK
    # =============================================================================
    # Business context and criticality - determines attack motivation and impact.
    # High-value assets are prioritized targets for advanced adversaries.
    
    asset_criticality: Optional[str] = Field(
        None,
        description="Business criticality (Critical, High, Medium, Low)"
        # Examples: "Critical" (payment system), "High" (customer database),
        #           "Medium" (web server), "Low" (test environment)
        # Source: CMDB, business impact analysis
        # Impact: Higher criticality = more targeted attacks, higher risk tolerance
    )
    business_role: Optional[str] = Field(
        None,
        description="Asset function (e.g., Web Server, Database, Workstation, Domain Controller)"
        # Examples: "Web Server", "Domain Controller", "Database Server",
        #           "File Server", "VPN Gateway", "Executive Workstation"
        # Source: CMDB, asset inventory
        # Used for: Understanding attack value and lateral movement pivots
    )
    data_classification: Optional[str] = Field(
        None,
        description="Data sensitivity (Public, Internal, Confidential, Restricted)"
        # Examples: "Restricted" (PII, PHI, PCI), "Confidential" (trade secrets),
        #           "Internal" (business docs), "Public" (marketing materials)
        # Source: Data governance policies, DLP tools
        # Impact: Sensitive data = more sophisticated attacks, compliance requirements
    )
    environment: Optional[str] = Field(
        None,
        description="Environment type (Production, Staging, Development, Test)"
        # Examples: "Production", "Staging", "Development", "Test", "UAT"
        # Source: CMDB, network design documentation
        # Impact: Prod = critical attacks, Dev/Test = lower priority but easier access
    )
    
    # =============================================================================
    # CATEGORY 11: CLOUD & CONTAINERS
    # =============================================================================
    # Cloud and container-specific context - modern infrastructure attack vectors.
    # Cloud IAM and container escapes are common advanced attack techniques.
    
    cloud_provider: Optional[str] = Field(
        None,
        description="Cloud provider (AWS, Azure, GCP, None)"
        # Examples: "AWS", "Azure", "GCP", "DigitalOcean", "None" (on-prem)
        # Source: Cloud inventory APIs, instance metadata
        # Impact: Each cloud has unique attack paths (IAM, metadata service, etc.)
    )
    cloud_instance_type: Optional[str] = Field(
        None,
        description="Cloud instance type (e.g., t2.micro, m5.large)"
        # Examples: "t2.micro", "m5.large", "Standard_D2s_v3", "n1-standard-1"
        # Source: Cloud instance metadata
        # Used for: Understanding compute resources and instance profile access
    )
    cloud_iam_roles: Optional[list[str]] = Field(
        default=None,
        description="Cloud IAM roles and permissions"
        # Examples: ["arn:aws:iam::123456789:role/EC2-S3-FullAccess",
        #           "roles/storage.admin", "Contributor"]
        # Source: Cloud IAM APIs, instance metadata
        # Critical: Overly permissive roles enable privilege escalation to cloud resources
    )
    container_runtime: Optional[str] = Field(
        None,
        description="Container runtime (Docker, containerd, CRI-O)"
        # Examples: "Docker 20.10.12", "containerd 1.6.2", "CRI-O 1.23.1"
        # Source: Process lists, service enumeration
        # Risk: Container runtime vulnerabilities enable container escape
    )
    kubernetes_cluster: Optional[str] = Field(
        None,
        description="Kubernetes cluster name"
        # Examples: "prod-cluster-us-east", "dev-k8s", "eks-production"
        # Source: kubectl config, kubelet API
        # Impact: K8s access enables lateral movement across all cluster workloads
    )
    
    # =============================================================================
    # CATEGORY 12: BACKUP & STORAGE
    # =============================================================================
    # Backup configuration - both a recovery mechanism and potential attack target.
    # Attackers often target backups to prevent recovery from ransomware.
    
    backup_system: Optional[str] = Field(
        None,
        description="Backup solution in use"
        # Examples: "Veeam Backup & Replication 11", "AWS Backup", "rsync to NAS",
        #           "Acronis Cyber Backup", "No backup configured"
        # Source: Backup software inventory, scheduled tasks
        # Risk: Backup systems often have broad file access permissions
    )
    backup_location: Optional[str] = Field(
        None,
        description="Backup storage location"
        # Examples: "\\\\nas01\\backups", "s3://company-backups", "/mnt/backup-nas",
        #           "Azure Blob Storage", "Local disk (D:\\Backups)"
        # Source: Backup software configuration
        # Impact: Accessible backups can be encrypted by ransomware
    )
    
    # =============================================================================
    # CATEGORY 13: THREAT INTELLIGENCE
    # =============================================================================
    # Threat intelligence context - links host to known threats and exploits.
    # Presence of IOCs or known exploits indicates active targeting.
    
    threat_intel_matches: Optional[list[str]] = Field(
        default=None,
        description="Known IOCs or threat intelligence matches"
        # Examples: ["IP 203.0.113.42 matches APT29 C2 server",
        #           "File hash matches Cobalt Strike beacon",
        #           "Domain contacted known phishing infrastructure"]
        # Source: Threat intel feeds (AlienVault, ThreatConnect, MISP)
        # Critical: IOC matches indicate potential compromise
    )
    known_exploits: Optional[list[str]] = Field(
        default=None,
        description="Known exploit frameworks applicable to this host"
        # Examples: ["Metasploit module: exploit/windows/smb/ms17_010_eternalblue",
        #           "Public exploit available for CVE-2023-12345",
        #           "Weaponized in ransomware campaigns"]
        # Source: Exploit-DB, Metasploit, vulnerability intelligence
        # Impact: Known exploits = low skill barrier for attacks
    )
    
    # =============================================================================
    # Pydantic Configuration
    # =============================================================================
    
    class Config:
        """
        Pydantic model configuration with OpenAPI example.
        
        The json_schema_extra provides a comprehensive example that appears in:
        - FastAPI's automatic OpenAPI documentation (/docs, /redoc)
        - JSON Schema generation for client libraries
        - API documentation and integration guides
        
        This example demonstrates:
        - A realistic production web server scenario
        - Multiple vulnerabilities and misconfigurations
        - Mix of high-risk parameters (internet-exposed, missing patches, weak security)
        - Comprehensive coverage of different parameter categories
        
        The example is designed to generate an interesting attack path that includes:
        - Initial access via vulnerable services
        - Privilege escalation through misconfigurations
        - Lateral movement potential through Docker/Jenkins
        - Data access via MySQL with default credentials
        """
        json_schema_extra = {
            "example": {
                "platform": "Linux",
                "version_os": "Ubuntu 20.04.3 LTS",
                "asset_name": "web-prod-01",
                "fqdn": "web-prod-01.corp.example.com",
                "ip_addresses": ["10.0.1.50", "203.0.113.42"],
                "network_segment": "DMZ",
                "internet_exposed": True,
                "open_ports": [22, 80, 443, 3306, 2375],
                "services": [
                    "OpenSSH 8.2p1 on port 22",
                    "Apache httpd 2.4.41 on port 80",
                    "Apache httpd 2.4.41 (SSL) on port 443",
                    "MySQL 5.7.33 on port 3306",
                    "Docker API on port 2375 (unauthenticated)"
                ],
                "vulnerabilities": [
                    "CVE-2023-12345: SQL Injection in web application",
                    "CVE-2023-23456: Outdated SSH version",
                    "CVE-2023-34567: MySQL with default credentials"
                ],
                "security_controls": [
                    "CrowdStrike Falcon EDR - Active",
                    "pfSense Firewall - Permissive ruleset"
                ],
                "domain_membership": "corp.example.com",
                "admin_accounts": ["root", "dbadmin"],
                "installed_software": [
                    "Docker 20.10.12",
                    "Jenkins 2.346.1",
                    "Git 2.34.1"
                ],
                "patch_level": "Missing critical kernel patches from last 6 months",
                "asset_criticality": "High",
                "business_role": "Production Web Server",
                "environment": "Production",
                "configurations": [
                    "Docker socket exposed on 0.0.0.0:2375",
                    "Jenkins running without authentication on /script endpoint"
                ],
                "mfa_enabled": False
            }
        }
