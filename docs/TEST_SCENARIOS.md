# Test Scenarios for Attack Path Engine

This document contains diverse realistic test scenarios to validate the dynamic prompt builder and ensure attack paths are contextually accurate across different environments.

---

## Scenario 1: Internet-Exposed Web Server (High Risk)

**Environment**: Production DMZ web server with multiple vulnerabilities

```json
{
  "platform": "Linux",
  "version_os": "Ubuntu 20.04.3 LTS",
  "asset_name": "web-prod-01",
  "fqdn": "www.example.com",
  "ip_addresses": ["203.0.113.50"],
  
  "network_segment": "DMZ",
  "internet_exposed": true,
  
  "open_ports": [22, 80, 443, 3306, 2375],
  "services": [
    "OpenSSH 7.6p1 on port 22",
    "Apache httpd 2.4.29 on port 80",
    "Apache httpd 2.4.29 (SSL) on port 443",
    "MySQL 5.7.33 on port 3306",
    "Docker API on port 2375 (no authentication)"
  ],
  
  "vulnerabilities": [
    "CVE-2021-44228: Log4Shell RCE",
    "CVE-2021-3156: Sudo heap overflow",
    "CVE-2023-0286: OpenSSL type confusion"
  ],
  "critical_vuln_count": 3,
  "vulnerability_score": 9.8,
  
  "security_controls": [
    "ModSecurity WAF (detection only)",
    "fail2ban"
  ],
  "antivirus_status": "Not Installed",
  "firewall_status": "Enabled",
  "encryption_status": "Not enabled",
  
  "admin_accounts": ["root", "ubuntu", "webadmin"],
  "mfa_enabled": false,
  "password_policy": "Weak - 8 char minimum, no complexity",
  
  "installed_software": [
    "Docker 20.10.7",
    "Java 1.8.0_292 (vulnerable to Log4Shell)",
    "Git 2.17.1"
  ],
  
  "patch_level": "Severely outdated - 18 months behind",
  "missing_patches": [
    "USN-5361-1 (Linux kernel)",
    "Log4j 2.17.1 update",
    "OpenSSL 1.1.1s update"
  ],
  
  "configurations": [
    "Docker API exposed on 0.0.0.0:2375 without TLS",
    "MySQL root accessible from any host",
    "SSH allows password authentication",
    "Apache server-status endpoint publicly accessible",
    "Directory listing enabled on /backup"
  ],
  
  "asset_criticality": "Critical",
  "business_role": "Public-Facing Web Application",
  "environment": "Production",
  "data_classification": "Confidential - Customer PII",
  
  "backup_location": "/var/backups (chmod 777)",
  
  "threat_intel_matches": [
    "IP in Shodan database with exposed Docker API",
    "Historical brute-force attempts on SSH"
  ]
}
```

**Expected Attack Path Focus**:
- Immediate exploitation via exposed Docker API (no auth)
- Log4Shell RCE as primary vector
- Weak security controls (detection-only WAF)
- Critical asset + PII = Critical risk level

---

## Scenario 2: Hardened Internal Database Server (Low Risk)

**Environment**: Well-secured internal database with strong controls

```json
{
  "platform": "Linux",
  "version_os": "Red Hat Enterprise Linux 8.6",
  "asset_name": "db-internal-01",
  "fqdn": "db-internal-01.corp.local",
  "ip_addresses": ["10.10.50.10"],
  
  "network_segment": "Internal - Database Zone",
  "internet_exposed": false,
  
  "open_ports": [22, 5432],
  "services": [
    "OpenSSH 8.7p1 on port 22",
    "PostgreSQL 14.5 on port 5432"
  ],
  
  "vulnerabilities": [],
  "critical_vuln_count": 0,
  
  "security_controls": [
    "CrowdStrike Falcon EDR - Active and Updated",
    "Palo Alto Next-Gen Firewall",
    "Tripwire File Integrity Monitoring",
    "SELinux Enforcing"
  ],
  "edr_agent": "CrowdStrike Falcon v6.48.15106",
  "antivirus_status": "Active",
  "firewall_status": "Enabled - Strict Ruleset",
  "encryption_status": "LUKS Full Disk Encryption",
  
  "domain_membership": "corp.local",
  "organizational_unit": "OU=Database Servers,OU=Production,DC=corp,DC=local",
  "admin_accounts": ["dbadmin"],
  "service_accounts": ["postgres"],
  "mfa_enabled": true,
  "password_policy": "Strong - 16 char, complexity required, rotated every 60 days",
  
  "installed_software": [
    "PostgreSQL 14.5",
    "pgAdmin4",
    "Ansible"
  ],
  
  "patch_level": "Up-to-date - All patches applied within 7 days",
  "os_end_of_life": false,
  
  "configurations": [
    "PostgreSQL only accepts connections from application subnet",
    "SSH restricted to jump server",
    "Audit logging enabled",
    "Regular automated backups"
  ],
  
  "asset_criticality": "Critical",
  "business_role": "Primary Database Server",
  "environment": "Production",
  "data_classification": "Restricted - Financial Data",
  
  "backup_system": "Veeam Backup & Replication",
  "backup_location": "Encrypted offsite storage"
}
```

**Expected Attack Path Focus**:
- Very limited attack surface
- Strong security controls require sophisticated evasion
- MFA and strong password policy hinder credential attacks
- Risk should be LOW despite critical asset (compensating controls)

---

## Scenario 3: Legacy Windows Domain Controller (Critical Risk)

**Environment**: End-of-life Windows Server with AD services

```json
{
  "platform": "Windows",
  "version_os": "Windows Server 2008 R2 SP1",
  "asset_name": "DC01",
  "fqdn": "dc01.legacy.corp",
  "ip_addresses": ["192.168.10.5"],
  
  "network_segment": "Internal - Core Services",
  "internet_exposed": false,
  
  "open_ports": [53, 88, 135, 139, 389, 445, 636, 3389, 3268, 3269],
  "services": [
    "DNS on port 53",
    "Kerberos on port 88",
    "RPC on port 135",
    "NetBIOS on port 139",
    "LDAP on port 389",
    "SMB on port 445",
    "LDAPS on port 636",
    "RDP on port 3389",
    "Global Catalog on ports 3268, 3269"
  ],
  
  "vulnerabilities": [
    "CVE-2020-1472: Zerologon - Netlogon elevation of privilege",
    "CVE-2017-0144: EternalBlue - SMBv1 RCE",
    "CVE-2019-0708: BlueKeep - RDP RCE",
    "Multiple missing privilege escalation patches"
  ],
  "critical_vuln_count": 4,
  "vulnerability_score": 10.0,
  
  "security_controls": [
    "Windows Defender (outdated definitions)"
  ],
  "antivirus_status": "Outdated - 6 months old definitions",
  "firewall_status": "Disabled",
  "encryption_status": "Not enabled",
  
  "domain_membership": "legacy.corp (Primary DC)",
  "organizational_unit": "Domain Controllers",
  "admin_accounts": [
    "Administrator",
    "Domain Admin",
    "Enterprise Admin"
  ],
  "user_accounts": [
    "500+ domain users"
  ],
  "mfa_enabled": false,
  "password_policy": "Legacy - LM hashes still enabled",
  
  "patch_level": "End-of-Life - No patches since 2020",
  "missing_patches": [
    "All security patches since 2020",
    "MS17-010 (EternalBlue)",
    "KB4586819 (Zerologon)"
  ],
  "os_end_of_life": true,
  
  "configurations": [
    "SMBv1 enabled",
    "LLMNR and NBT-NS poisoning possible",
    "Unconstrained delegation configured",
    "PrintSpooler service running",
    "Weak NTLM authentication allowed"
  ],
  
  "asset_criticality": "Critical",
  "business_role": "Active Directory Domain Controller",
  "environment": "Production",
  "data_classification": "Restricted - All Domain Credentials",
  
  "threat_intel_matches": [
    "Known Zerologon exploit PoC widely available",
    "EternalBlue actively exploited by ransomware gangs"
  ],
  "known_exploits": [
    "Metasploit module: exploit/windows/smb/ms17_010_eternalblue",
    "Zerologon exploitation tools publicly available"
  ]
}
```

**Expected Attack Path Focus**:
- Multiple critical RCE vulnerabilities
- EOL system with no patching
- Domain Controller = complete domain compromise
- CRITICAL risk level (highest asset value + worst security posture)

---

## Scenario 4: Cloud-Native Kubernetes Workload (Medium Risk)

**Environment**: AWS EKS cluster with container workloads

```json
{
  "platform": "Linux",
  "version_os": "Amazon Linux 2",
  "asset_name": "k8s-worker-03",
  "fqdn": "ip-10-0-3-45.ec2.internal",
  "ip_addresses": ["10.0.3.45", "54.123.45.67"],
  
  "network_segment": "AWS VPC - Private Subnet",
  "internet_exposed": true,
  
  "open_ports": [22, 80, 443, 10250, 10256],
  "services": [
    "OpenSSH 7.4 on port 22",
    "Nginx Ingress Controller on ports 80, 443",
    "Kubelet API on port 10250",
    "kube-proxy healthz on port 10256"
  ],
  
  "vulnerabilities": [
    "CVE-2022-0185: Linux kernel container escape",
    "Kubelet API accessible without authentication"
  ],
  "critical_vuln_count": 2,
  
  "security_controls": [
    "AWS Security Groups",
    "Falco runtime security",
    "AWS GuardDuty"
  ],
  "firewall_status": "Enabled - AWS Security Groups",
  
  "admin_accounts": ["ec2-user"],
  "service_accounts": ["kubelet", "kube-proxy"],
  "mfa_enabled": true,
  
  "installed_software": [
    "Docker 20.10.17",
    "containerd 1.6.8",
    "kubectl 1.24",
    "AWS CLI 2.7"
  ],
  
  "patch_level": "Outdated - 4 months behind on kernel updates",
  
  "configurations": [
    "Kubelet API exposed on 10250 without authentication",
    "Privileged containers allowed",
    "hostPath volumes mounted in pods",
    "No Pod Security Policy enforced",
    "AWS IMDS v1 enabled (SSRF vulnerable)"
  ],
  
  "asset_criticality": "High",
  "business_role": "Kubernetes Worker Node",
  "environment": "Production",
  "data_classification": "Confidential",
  
  "cloud_provider": "AWS",
  "cloud_instance_type": "t3.xlarge",
  "cloud_iam_roles": [
    "EKS-NodeInstanceRole",
    "S3ReadWriteAccess",
    "SecretsManagerReadWrite"
  ],
  "container_runtime": "containerd 1.6.8",
  "kubernetes_cluster": "prod-eks-cluster",
  
  "threat_intel_matches": [
    "Unauthenticated Kubelet API is common attack vector",
    "AWS IMDS v1 SSRF exploitation trending"
  ],
  "known_exploits": [
    "Container escape via CVE-2022-0185",
    "Kubelet API RCE exploitation"
  ]
}
```

**Expected Attack Path Focus**:
- Kubelet API exploitation
- Container escape techniques
- AWS IMDS metadata service exploitation
- IAM role privilege escalation
- Cloud-specific lateral movement

---

## Scenario 5: Developer Workstation (Medium-Low Risk)

**Environment**: macOS developer laptop with dev tools

```json
{
  "platform": "macOS",
  "version_os": "macOS 13.4 (Ventura)",
  "asset_name": "MacBook-Pro-John",
  "ip_addresses": ["192.168.1.142"],
  
  "network_segment": "Internal - Corporate WiFi",
  "internet_exposed": false,
  
  "open_ports": [22],
  "services": [
    "OpenSSH 9.0 on port 22"
  ],
  
  "vulnerabilities": [
    "Outdated NPM packages with known vulnerabilities",
    "Git credentials stored in plaintext"
  ],
  
  "security_controls": [
    "macOS Gatekeeper",
    "FileVault 2 encryption",
    "macOS Firewall"
  ],
  "antivirus_status": "Not Installed",
  "firewall_status": "Enabled",
  "encryption_status": "FileVault 2 Full Disk Encryption Enabled",
  
  "domain_membership": "corp.example.com",
  "admin_accounts": ["john.doe"],
  "mfa_enabled": true,
  
  "installed_software": [
    "Visual Studio Code",
    "Docker Desktop 4.20",
    "Node.js 18.16",
    "Python 3.11",
    "Git 2.40",
    "AWS CLI 2.11",
    "kubectl 1.27"
  ],
  "development_tools": [
    "Docker Desktop",
    "Git",
    "Node.js",
    "Python",
    "kubectl"
  ],
  "browser_extensions": [
    "LastPass",
    "Okta Browser Plugin",
    "React Developer Tools"
  ],
  
  "patch_level": "Up-to-date - Auto-updates enabled",
  
  "configurations": [
    "Git credentials cached in Keychain",
    "AWS credentials in ~/.aws/credentials",
    "SSH keys without passphrase protection",
    "Docker socket exposed to user"
  ],
  
  "asset_criticality": "Medium",
  "business_role": "Developer Workstation",
  "environment": "Development",
  "data_classification": "Internal - Source Code Access",
  
  "cloud_provider": "AWS",
  "cloud_iam_roles": [
    "Developer-ReadOnly"
  ]
}
```

**Expected Attack Path Focus**:
- Credential theft (Git, AWS, SSH keys)
- Browser extension vulnerabilities
- Social engineering vectors
- Supply chain attacks via npm packages
- Medium risk (less critical asset, but source code access)

---

## Scenario 6: IoT Device / Network Camera (High Risk)

**Environment**: Outdated IP camera on corporate network

```json
{
  "platform": "Linux",
  "version_os": "BusyBox 1.21.1 (embedded)",
  "asset_name": "IP-Camera-Lobby",
  "ip_addresses": ["192.168.5.201"],
  
  "network_segment": "Internal - IoT VLAN",
  "internet_exposed": false,
  
  "open_ports": [23, 80, 554, 8080],
  "services": [
    "Telnet on port 23 (no auth)",
    "Web interface on port 80",
    "RTSP on port 554",
    "Alternative HTTP on port 8080"
  ],
  
  "vulnerabilities": [
    "Default credentials (admin/admin)",
    "Command injection in web interface",
    "Telnet enabled with no authentication",
    "Multiple buffer overflows"
  ],
  "critical_vuln_count": 4,
  
  "security_controls": [],
  "antivirus_status": "Not Applicable",
  "firewall_status": "Not Applicable",
  "encryption_status": "None",
  
  "admin_accounts": ["admin", "root"],
  "mfa_enabled": false,
  "password_policy": "Default - admin/admin",
  
  "patch_level": "Never patched - Firmware from 2015",
  "os_end_of_life": true,
  
  "configurations": [
    "Telnet enabled with default credentials",
    "Web interface uses HTTP (no SSL)",
    "RTSP stream not password protected",
    "UPnP enabled - auto port forwarding",
    "Firmware update disabled by manufacturer"
  ],
  
  "asset_criticality": "Low",
  "business_role": "Security Camera",
  "environment": "Production",
  "data_classification": "Internal",
  
  "threat_intel_matches": [
    "Device model in Mirai botnet target list",
    "Known vulnerability exploited by IoT botnets"
  ],
  "known_exploits": [
    "Mirai botnet scanner targeting default credentials",
    "Multiple exploit-db entries for this camera model"
  ]
}
```

**Expected Attack Path Focus**:
- Default credential exploitation
- Telnet access without authentication
- Pivot point for lateral movement
- Botnet recruitment
- HIGH risk (easy exploitation + pivot point despite low asset value)

---

## Scenario 7: Minimal Data (Backward Compatibility Test)

**Environment**: Minimal information from basic scanner

```json
{
  "platform": "Windows",
  "version_os": "Windows Server 2016",
  "open_ports": [80, 443, 3389],
  "services": [
    "IIS 10.0 on port 80",
    "IIS 10.0 on port 443",
    "RDP on port 3389"
  ],
  "vulnerabilities": [
    "CVE-2019-0708: BlueKeep RDP vulnerability"
  ]
}
```

**Expected Attack Path Focus**:
- Should generate valid attack path with limited data
- Generic but coherent exploitation sequence
- Demonstrates backward compatibility

---

## Scenario 8: Zero Vulnerabilities But High Configuration Risk

**Environment**: Patched system with severe misconfigurations

```json
{
  "platform": "Linux",
  "version_os": "Ubuntu 22.04.2 LTS",
  "asset_name": "jenkins-ci-01",
  "ip_addresses": ["10.20.30.40"],
  
  "network_segment": "Internal - CI/CD Zone",
  "internet_exposed": false,
  
  "open_ports": [22, 8080, 50000],
  "services": [
    "OpenSSH 8.9p1 on port 22",
    "Jenkins 2.400 on port 8080",
    "Jenkins agent on port 50000"
  ],
  
  "vulnerabilities": [],
  "critical_vuln_count": 0,
  
  "security_controls": [
    "AppArmor enabled"
  ],
  "firewall_status": "Enabled",
  
  "admin_accounts": ["jenkins", "deploy"],
  "mfa_enabled": false,
  
  "installed_software": [
    "Jenkins 2.400",
    "Docker 24.0",
    "Git 2.34",
    "AWS CLI 2.11",
    "kubectl 1.27"
  ],
  
  "patch_level": "Up-to-date - All patches current",
  
  "configurations": [
    "Jenkins script console accessible without authentication",
    "Groovy script execution enabled globally",
    "Jenkins running as root user",
    "Docker socket mounted in Jenkins container",
    "AWS credentials stored in Jenkins credentials store (unencrypted)",
    "kubectl config with cluster-admin privileges",
    "Git repositories cloned with embedded credentials",
    "No authorization strategy configured"
  ],
  
  "asset_criticality": "Critical",
  "business_role": "CI/CD Pipeline Server",
  "environment": "Production",
  "data_classification": "Restricted - All source code and deployment credentials",
  
  "cloud_iam_roles": [
    "JenkinsDeploymentRole (AdministratorAccess)"
  ]
}
```

**Expected Attack Path Focus**:
- Zero CVE vulnerabilities but CRITICAL risk
- Configuration weaknesses as primary attack vector
- Jenkins script console RCE
- Credential theft leading to cloud compromise
- Demonstrates importance of configuration parameters

---

## Testing Instructions

### 1. Test Each Scenario Individually

```bash
# Test Scenario 1
curl -X POST http://localhost:8000/attack-path \
  -H "Content-Type: application/json" \
  -d '<paste scenario 1 JSON>'

# Compare risk levels and attack path specificity
```

### 2. Validate Dynamic Prompt Sections

For each scenario, verify the generated prompt includes:
- Appropriate sections based on available data
- Context-specific instructions
- Correct risk indicators (🎯, ⚠️, 🔑)

### 3. Check Attack Path Quality

Attack paths should reference:
- Specific vulnerabilities mentioned (CVE numbers)
- Exact misconfigurations listed
- Named security controls for evasion
- Specific admin accounts for targeting
- Network segment for lateral movement

### 4. Validate Risk Scoring

Expected risk levels:
- Scenario 1: **CRITICAL** (internet-exposed + weak controls + critical asset)
- Scenario 2: **LOW** (strong controls + patched + internal)
- Scenario 3: **CRITICAL** (EOL DC + multiple RCE + domain compromise)
- Scenario 4: **HIGH** (cloud misconfig + container escape)
- Scenario 5: **MEDIUM** (developer workstation + credential access)
- Scenario 6: **HIGH** (default creds + pivot point)
- Scenario 7: **HIGH** (BlueKeep RCE)
- Scenario 8: **CRITICAL** (config risk + credential access + critical asset)

### 5. Python Test Script

```python
import requests
import json

scenarios = [
    ("Scenario 1: Internet Web Server", "scenario1.json"),
    ("Scenario 2: Hardened Database", "scenario2.json"),
    # ... add all scenarios
]

for name, file in scenarios:
    with open(file) as f:
        data = json.load(f)
    
    response = requests.post(
        "http://localhost:8000/attack-path",
        json=data
    )
    
    result = response.json()
    print(f"\n{name}")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Attack Steps: {len(result['attack_path'])}")
    print(f"  First Step: {result['attack_path'][0][:100]}...")
```

---

## Success Criteria

✅ **All scenarios generate valid JSON responses**
✅ **Risk levels match expected severity**
✅ **Attack paths reference specific context** (CVEs, accounts, configs)
✅ **Security controls influence evasion tactics**
✅ **Network segments affect lateral movement**
✅ **Asset criticality impacts risk scoring**
✅ **Backward compatibility maintained** (Scenario 7)
✅ **Configuration-only risks detected** (Scenario 8)

---

## Expected Outcomes

1. **Scenario 1**: Exploitation via Docker API, Log4Shell, weak controls
2. **Scenario 2**: Complex multi-step attack, EDR evasion required, LOW risk
3. **Scenario 3**: Zerologon → Domain Admin, CRITICAL
4. **Scenario 4**: Kubelet API → Container Escape → AWS IAM escalation
5. **Scenario 5**: Credential theft → Cloud access
6. **Scenario 6**: Default creds → Botnet → Lateral movement
7. **Scenario 7**: Generic but valid attack path
8. **Scenario 8**: Jenkins script console → Root → Cloud compromise

