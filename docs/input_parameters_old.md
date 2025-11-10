# Input Parameters - Old Version

This document catalogs all input parameters currently accepted by the AI Engine's Attack Path Analysis endpoint.

## Overview

The Attack Path Engine accepts 50+ optional parameters organized into 13 logical categories. All parameters are defined in the `InputHost` model (`app/models/host.py`) and are optional to allow flexible integration with various data sources.

**Model Definition:** `app/models/host.py::InputHost`  
**API Endpoint:** `POST /attack-path`  
**Total Parameters:** 50+

---

## Parameter Categories

### 1. CORE SYSTEM INFO (2 parameters)

Fundamental OS information - typically available from any scanner.

| Parameter    | Type  | Description               | Examples                                                          |
| ------------ | ----- | ------------------------- | ----------------------------------------------------------------- |
| `platform`   | `str` | Operating system platform | `"Linux"`, `"Windows"`, `"macOS"`, `"AIX"`, `"Solaris"`           |
| `version_os` | `str` | Operating system version  | `"Ubuntu 20.04.3 LTS"`, `"Windows Server 2019"`, `"macOS 12.3.1"` |

**Sources:** Nmap OS detection, SCCM, Nessus, OpenVAS

---

### 2. NETWORK & SERVICES (3 parameters)

Network exposure and running services - critical for attack surface analysis.

| Parameter         | Type        | Description                                | Examples                                                             |
| ----------------- | ----------- | ------------------------------------------ | -------------------------------------------------------------------- |
| `open_ports`      | `list[int]` | List of open ports detected on the host    | `[22, 80, 443, 3306, 5432, 8080]`                                    |
| `services`        | `list[str]` | Services running on open ports             | `["OpenSSH 8.2p1 on port 22", "Apache httpd 2.4.41 on port 80"]`     |
| `vulnerabilities` | `list[str]` | Known vulnerabilities (CVEs, descriptions) | `["CVE-2023-12345: SQL Injection", "CVE-2022-67890: RCE in Apache"]` |

**Sources:** Nmap, Masscan, network scanners, Nessus, OpenVAS, Qualys, Tenable

---

### 3. ASSET IDENTIFICATION (5 parameters)

Unique identifiers and naming information - used for asset correlation.

| Parameter       | Type        | Description                              | Examples                                               |
| --------------- | ----------- | ---------------------------------------- | ------------------------------------------------------ |
| `asset_id`      | `str`       | Unique asset identifier                  | `"ASSET-12345"`, `"a1b2c3d4-e5f6-7890"`                |
| `asset_name`    | `str`       | Device hostname or asset name            | `"web-prod-01"`, `"db-server-nyc"`, `"john-laptop"`    |
| `mac_addresses` | `list[str]` | MAC addresses for network identification | `["00:1A:2B:3C:4D:5E", "AA:BB:CC:DD:EE:FF"]`           |
| `ip_addresses`  | `list[str]` | IP addresses (IPv4/IPv6)                 | `["10.0.1.50", "203.0.113.42", "2001:db8::1"]`         |
| `fqdn`          | `str`       | Fully qualified domain name              | `"web-prod-01.corp.example.com"`, `"mail.example.com"` |

**Sources:** CMDB, Asset Management systems, DNS, DHCP, network scanners

---

### 4. NETWORK CONTEXT (3 parameters)

Network positioning and exposure - critical for understanding attack surface.

| Parameter          | Type        | Description                                  | Examples                                                                  |
| ------------------ | ----------- | -------------------------------------------- | ------------------------------------------------------------------------- |
| `network_segment`  | `str`       | Network segment                              | `"DMZ"`, `"Internal"`, `"Production"`, `"Guest Network"`, `"OT/SCADA"`    |
| `internet_exposed` | `bool`      | Whether the asset is exposed to the internet | `true` (public IP), `false` (internal only)                               |
| `firewall_rules`   | `list[str]` | Firewall configuration and rules             | `["Allow TCP 443 from 0.0.0.0/0", "Block TCP 22 except from 10.0.0.0/8"]` |

**Sources:** Firewall configs, security policies, Shodan, external scans

---

### 5. SECURITY CONTROLS (5 parameters)

Defensive mechanisms in place - determines attack difficulty and bypass strategies.

| Parameter           | Type        | Description                         | Examples                                                                    |
| ------------------- | ----------- | ----------------------------------- | --------------------------------------------------------------------------- |
| `security_controls` | `list[str]` | Security solutions                  | `["CrowdStrike Falcon EDR - Active", "Palo Alto NGFW", "Windows Defender"]` |
| `edr_agent`         | `str`       | EDR/antivirus agent name and status | `"CrowdStrike Falcon - Active"`, `"Carbon Black - Outdated"`, `"None"`      |
| `antivirus_status`  | `str`       | Antivirus status                    | `"Active"`, `"Disabled"`, `"Outdated"`, `"Not Installed"`                   |
| `firewall_status`   | `str`       | Firewall status                     | `"Enabled"`, `"Disabled"`, `"Misconfigured"`                                |
| `encryption_status` | `str`       | Disk encryption status              | `"BitLocker Enabled"`, `"FileVault Active"`, `"Not Encrypted"`              |

**Sources:** EDR consoles, SCCM, endpoint management tools, Windows Security Center

---

### 6. IDENTITY & ACCESS (7 parameters)

User accounts and authentication mechanisms - key for privilege escalation.

| Parameter             | Type        | Description                          | Examples                                                                     |
| --------------------- | ----------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| `domain_membership`   | `str`       | Active Directory domain or workgroup | `"corp.example.com"`, `"WORKGROUP"`, `"child.corp.example.com"`              |
| `organizational_unit` | `str`       | Active Directory OU path             | `"OU=Servers,OU=Production,DC=corp,DC=example,DC=com"`                       |
| `user_accounts`       | `list[str]` | Local and domain user accounts       | `["CORP\\john.doe", "root", "administrator", "service_user"]`                |
| `admin_accounts`      | `list[str]` | Privileged/administrator accounts    | `["root", "Administrator", "CORP\\domain_admins"]`                           |
| `service_accounts`    | `list[str]` | Service account names                | `["svc_sql", "apache", "jenkins", "CORP\\svc_backup"]`                       |
| `mfa_enabled`         | `bool`      | Multi-factor authentication enabled  | `true` (MFA enforced), `false` (password only)                               |
| `password_policy`     | `str`       | Password policy strength             | `"Complex (14+ chars, special chars)"`, `"Weak (no requirements)"`, `"None"` |

**Sources:** Active Directory, local account enumeration, IAM policies, sudoers file, GPO

---

### 7. SOFTWARE & APPLICATIONS (4 parameters)

Installed software inventory - each application is a potential attack vector.

| Parameter            | Type        | Description                      | Examples                                                                 |
| -------------------- | ----------- | -------------------------------- | ------------------------------------------------------------------------ |
| `installed_software` | `list[str]` | Installed applications and tools | `["Microsoft Office 2019", "Adobe Reader DC", "7-Zip 19.00"]`            |
| `browser_extensions` | `list[str]` | Browser extensions               | `["LastPass 4.82.0", "Grammarly", "uBlock Origin"]`                      |
| `database_software`  | `list[str]` | Database systems installed       | `["MySQL 5.7.33", "PostgreSQL 13.2", "MongoDB 4.4.6", "Redis 6.2.1"]`    |
| `development_tools`  | `list[str]` | Development tools                | `["Docker 20.10.12", "Jenkins 2.346.1", "Git 2.34.1", "kubectl 1.23.5"]` |

**Sources:** SCCM, package managers (apt, yum, chocolatey), WMI queries, process lists

---

### 8. PATCH & VULNERABILITY MANAGEMENT (5 parameters)

Patch status and vulnerability metrics - directly indicates exploitability.

| Parameter             | Type        | Description                           | Examples                                                                           |
| --------------------- | ----------- | ------------------------------------- | ---------------------------------------------------------------------------------- |
| `patch_level`         | `str`       | Patch status                          | `"Up-to-date"`, `"Missing critical patches from last 6 months"`, `"Never patched"` |
| `missing_patches`     | `list[str]` | Specific missing patches or KB IDs    | `["KB5012345", "MS17-010 (EternalBlue)", "CVE-2023-12345 patch"]`                  |
| `os_end_of_life`      | `bool`      | Whether OS is end-of-life/unsupported | `true` (Windows 7, Ubuntu 16.04), `false` (current support)                        |
| `vulnerability_score` | `float`     | CVSS or VPR risk score                | `9.8` (critical), `7.5` (high), `4.3` (medium)                                     |
| `critical_vuln_count` | `int`       | Number of critical vulnerabilities    | `0` (clean), `5` (concerning), `25` (severe exposure)                              |

**Sources:** WSUS, SCCM, apt/yum update checks, vulnerability scanners, OS version cross-reference

---

### 9. CONFIGURATION & COMPLIANCE (3 parameters)

Security misconfigurations and compliance issues.

| Parameter                  | Type        | Description                              | Examples                                                             |
| -------------------------- | ----------- | ---------------------------------------- | -------------------------------------------------------------------- |
| `configurations`           | `list[str]` | Misconfigurations or security weaknesses | `["Docker socket exposed on 0.0.0.0:2375", "SSH allows root login"]` |
| `compliance_gaps`          | `list[str]` | Compliance violations                    | `["PCI-DSS: No audit logging", "HIPAA: Unencrypted PHI storage"]`    |
| `security_recommendations` | `list[str]` | Recommended security improvements        | `["Enable MFA for all admin accounts", "Segment database network"]`  |

**Sources:** Configuration audits, security baselines (CIS, STIG), compliance scanners

---

### 10. ASSET CONTEXT & RISK (4 parameters)

Business context and criticality - determines attack motivation and impact.

| Parameter             | Type  | Description          | Examples                                                                    |
| --------------------- | ----- | -------------------- | --------------------------------------------------------------------------- |
| `asset_criticality`   | `str` | Business criticality | `"Critical"` (payment system), `"High"`, `"Medium"`, `"Low"`                |
| `business_role`       | `str` | Asset function       | `"Web Server"`, `"Domain Controller"`, `"Database Server"`, `"VPN Gateway"` |
| `data_classification` | `str` | Data sensitivity     | `"Restricted"` (PII, PHI, PCI), `"Confidential"`, `"Internal"`, `"Public"`  |
| `environment`         | `str` | Environment type     | `"Production"`, `"Staging"`, `"Development"`, `"Test"`, `"UAT"`             |

**Sources:** CMDB, business impact analysis, data governance policies, DLP tools

---

### 11. CLOUD & CONTAINERS (5 parameters)

Cloud and container-specific context - modern infrastructure attack vectors.

| Parameter             | Type        | Description                     | Examples                                                           |
| --------------------- | ----------- | ------------------------------- | ------------------------------------------------------------------ |
| `cloud_provider`      | `str`       | Cloud provider                  | `"AWS"`, `"Azure"`, `"GCP"`, `"DigitalOcean"`, `"None"` (on-prem)  |
| `cloud_instance_type` | `str`       | Cloud instance type             | `"t2.micro"`, `"m5.large"`, `"Standard_D2s_v3"`, `"n1-standard-1"` |
| `cloud_iam_roles`     | `list[str]` | Cloud IAM roles and permissions | `["arn:aws:iam::123456789:role/EC2-S3-FullAccess"]`                |
| `container_runtime`   | `str`       | Container runtime               | `"Docker 20.10.12"`, `"containerd 1.6.2"`, `"CRI-O 1.23.1"`        |
| `kubernetes_cluster`  | `str`       | Kubernetes cluster name         | `"prod-cluster-us-east"`, `"dev-k8s"`, `"eks-production"`          |

**Sources:** Cloud inventory APIs, instance metadata, kubectl config, kubelet API

---

### 12. BACKUP & STORAGE (2 parameters)

Backup configuration - both a recovery mechanism and potential attack target.

| Parameter         | Type  | Description             | Examples                                                              |
| ----------------- | ----- | ----------------------- | --------------------------------------------------------------------- |
| `backup_system`   | `str` | Backup solution in use  | `"Veeam Backup & Replication 11"`, `"AWS Backup"`, `"rsync to NAS"`   |
| `backup_location` | `str` | Backup storage location | `"\\\\nas01\\backups"`, `"s3://company-backups"`, `"/mnt/backup-nas"` |

**Sources:** Backup software inventory, scheduled tasks, backup software configuration

---

### 13. THREAT INTELLIGENCE (2 parameters)

Threat intelligence context - links host to known threats and exploits.

| Parameter              | Type        | Description                                      | Examples                                                          |
| ---------------------- | ----------- | ------------------------------------------------ | ----------------------------------------------------------------- |
| `threat_intel_matches` | `list[str]` | Known IOCs or threat intelligence matches        | `["IP 203.0.113.42 matches APT29 C2 server"]`                     |
| `known_exploits`       | `list[str]` | Known exploit frameworks applicable to this host | `["Metasploit module: exploit/windows/smb/ms17_010_eternalblue"]` |

**Sources:** Threat intel feeds (AlienVault, ThreatConnect, MISP), Exploit-DB, Metasploit

---

## Additional Parameters Found in Examples

The following parameters were found in example request files but are not currently defined in the `InputHost` model:

| Parameter            | Type         | Found In                         | Description                                   |
| -------------------- | ------------ | -------------------------------- | --------------------------------------------- |
| `waf_enabled`        | `bool`       | `linux_web_server_enhanced.json` | WAF status                                    |
| `ids_enabled`        | `bool`       | `linux_web_server_enhanced.json` | IDS status                                    |
| `encryption_enabled` | `bool`       | `linux_web_server_enhanced.json` | Encryption status                             |
| `accounts`           | `list[dict]` | `linux_web_server_enhanced.json` | Complex account objects with privilege levels |
| `database_exposure`  | `str`        | `linux_web_server_enhanced.json` | Database exposure details                     |

**Note:** These parameters are present in example files but not formally defined in the Pydantic model, suggesting they may be deprecated or experimental.

---

## Complete Example Request

```json
{
  "asset_name": "web-prod-01",
  "asset_id": "ASSET-12345",
  "fqdn": "web-prod-01.corp.example.com",
  "ip_addresses": ["10.0.1.50", "203.0.113.42"],
  "mac_addresses": ["00:1A:2B:3C:4D:5E"],
  "platform": "Linux",
  "version_os": "Ubuntu 20.04.3 LTS",
  "os_end_of_life": false,
  "asset_criticality": "High",
  "business_role": "Production Web Server",
  "environment": "Production",
  "data_classification": "Confidential",
  "network_segment": "DMZ",
  "internet_exposed": true,
  "open_ports": [22, 80, 443, 3306, 2375],
  "services": [
    "OpenSSH 8.2p1 on port 22",
    "Apache httpd 2.4.41 on port 80",
    "Apache httpd 2.4.41 (SSL) on port 443",
    "MySQL 5.7.33 on port 3306",
    "Docker API on port 2375 (unauthenticated)"
  ],
  "firewall_rules": [
    "Allow TCP 443 from 0.0.0.0/0",
    "Allow TCP 80 from 0.0.0.0/0"
  ],
  "security_controls": [
    "CrowdStrike Falcon EDR - Active",
    "pfSense Firewall - Permissive ruleset"
  ],
  "edr_agent": "CrowdStrike Falcon - Active",
  "antivirus_status": "Active",
  "firewall_status": "Enabled",
  "encryption_status": "Not Encrypted",
  "vulnerabilities": [
    "CVE-2023-12345: SQL Injection in web application",
    "CVE-2023-23456: Outdated SSH version",
    "CVE-2023-34567: MySQL with default credentials"
  ],
  "vulnerability_score": 9.8,
  "critical_vuln_count": 3,
  "patch_level": "Missing critical kernel patches from last 6 months",
  "missing_patches": ["CVE-2023-12345 patch"],
  "domain_membership": "corp.example.com",
  "organizational_unit": "OU=Servers,OU=Production,DC=corp,DC=example,DC=com",
  "user_accounts": ["root", "apache", "dbadmin"],
  "admin_accounts": ["root", "dbadmin"],
  "service_accounts": ["apache", "mysql"],
  "mfa_enabled": false,
  "password_policy": "Weak (no requirements)",
  "installed_software": ["Docker 20.10.12", "Jenkins 2.346.1", "Git 2.34.1"],
  "browser_extensions": [],
  "database_software": ["MySQL 5.7.33"],
  "development_tools": ["Docker 20.10.12", "Jenkins 2.346.1", "Git 2.34.1"],
  "configurations": [
    "Docker socket exposed on 0.0.0.0:2375",
    "Jenkins running without authentication on /script endpoint"
  ],
  "compliance_gaps": ["PCI-DSS: No audit logging"],
  "security_recommendations": [
    "Enable MFA for all admin accounts",
    "Segment database network",
    "Remove exposed Docker API"
  ],
  "cloud_provider": "None",
  "cloud_instance_type": null,
  "cloud_iam_roles": [],
  "container_runtime": "Docker 20.10.12",
  "kubernetes_cluster": null,
  "backup_system": "rsync to NAS",
  "backup_location": "/mnt/backup-nas",
  "threat_intel_matches": [],
  "known_exploits": ["Public exploit available for CVE-2023-12345"]
}
```

---

## Minimal Example Request

```json
{
  "platform": "Windows",
  "version_os": "Windows 7",
  "open_ports": [139, 445],
  "services": ["SMB"],
  "vulnerabilities": ["MS17-010"]
}
```

---

## Implementation Notes

### Model Definition

- **File:** `app/models/host.py`
- **Class:** `InputHost(BaseModel)`
- **Validation:** Pydantic with type safety
- **Required Fields:** None (all optional)

### Design Philosophy

- All fields are optional for maximum flexibility
- More context = better attack path generation
- Supports partial data from any vulnerability scanner
- Backward compatible with any subset of parameters

### Integration Points

The API accepts this model at the following endpoint:

- **POST** `/attack-path` → Returns Markdown-formatted attack path

### Response Models

The system uses these models for output:

- `AttackContext` - Shared context across all 7 Kill Chain stages
- `StageAnalysis` - Structured analysis of a single stage
- `CompleteAnalysisResponse` - Complete 7-stage response with validation

---

## Source Files Referenced

1. `app/models/host.py` - Primary model definition
2. `app/models/attack_context.py` - Attack threading context
3. `app/models/complete_analysis.py` - Response models
4. `app/main.py` - API endpoint implementation
5. `examples/requests/complete.json` - Complete example
6. `examples/requests/linux_web_server_enhanced.json` - Enhanced Linux example
7. `examples/requests/windows_7_ms17_010_minimal.json` - Minimal Windows example
8. `example_request.md` - EternalBlue example

---

**Document Generated:** 2025-11-10  
**AI Engine Version:** 1.0.0  
**Total Parameters Documented:** 50+
