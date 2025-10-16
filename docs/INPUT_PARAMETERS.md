# AI Engine Input Parameters Documentation

## Overview

The AI Engine accepts host data from external vulnerability scanners and collectors to generate context-aware attack paths. **All parameters are optional** to support flexible data collection from various sources. The more context provided, the more accurate and realistic the generated attack paths will be.

## Key Benefits

- **More Context = Better Results**: The more parameters provided, the more accurate and specific the generated attack paths
- **Context-Aware Analysis**: The engine tailors attack paths based on security controls, network segmentation, and asset criticality
- **Fully Optional**: All fields are optional - send only what's available from your data sources
- **Flexible Integration**: Collectors can send any combination of parameters

---

## Input Parameters

### 🔹 Core System Info

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `platform` | `string` | Operating system platform | `"Linux"`, `"Windows"`, `"macOS"` |
| `version_os` | `string` | OS version or distribution | `"Ubuntu 20.04.3 LTS"`, `"Windows Server 2019"` |

### 🔹 Asset Identification

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `asset_id` | `string` | Unique asset identifier | `"AST-12345"` |
| `asset_name` | `string` | Device hostname or asset name | `"web-prod-01"` |
| `mac_addresses` | `array[string]` | MAC addresses | `["00:1B:44:11:3A:B7"]` |
| `ip_addresses` | `array[string]` | IP addresses (IPv4/IPv6) | `["10.0.1.50", "203.0.113.42"]` |
| `fqdn` | `string` | Fully qualified domain name | `"web-prod-01.corp.example.com"` |

### 🔹 Network & Services

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `open_ports` | `array[int]` | List of open ports | `[22, 80, 443, 3306]` |
| `services` | `array[string]` | Services on ports with versions | `["OpenSSH 8.2p1 on port 22", "Apache 2.4.41 on port 80"]` |
| `vulnerabilities` | `array[string]` | Known vulnerabilities (CVEs) | `["CVE-2023-12345: SQL Injection"]` |

### 🔹 Network Context ⭐ HIGH IMPACT

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `network_segment` | `string` | Network segment location | `"DMZ"`, `"Internal"`, `"Isolated"` |
| `internet_exposed` | `boolean` | Internet-facing asset | `true`, `false` |
| `firewall_rules` | `array[string]` | Firewall configuration | `["Allow 80/tcp from any", "Block all outbound"]` |

### 🔹 Security Controls ⭐ CRITICAL IMPACT

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `security_controls` | `array[string]` | Security solutions installed | `["CrowdStrike Falcon EDR", "Palo Alto Firewall"]` |
| `edr_agent` | `string` | EDR/antivirus agent and status | `"CrowdStrike Falcon v6.45"` |
| `antivirus_status` | `string` | Antivirus status | `"Active"`, `"Disabled"`, `"Not Installed"` |
| `firewall_status` | `string` | Firewall status | `"Enabled"`, `"Disabled"` |
| `encryption_status` | `string` | Disk encryption status | `"BitLocker Enabled"`, `"Not enabled"` |

### 🔹 Identity & Access Management ⭐ HIGH IMPACT

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `domain_membership` | `string` | AD domain or workgroup | `"corp.example.com"` |
| `organizational_unit` | `string` | AD OU path | `"OU=Servers,DC=corp,DC=example,DC=com"` |
| `user_accounts` | `array[string]` | Local and domain users | `["john.doe", "admin", "serviceuser"]` |
| `admin_accounts` | `array[string]` | Privileged accounts | `["root", "Administrator", "dbadmin"]` |
| `service_accounts` | `array[string]` | Service account names | `["mysql", "www-data"]` |
| `mfa_enabled` | `boolean` | MFA enabled | `true`, `false` |
| `password_policy` | `string` | Password policy strength | `"Strong"`, `"Weak"`, `"None"` |

### 🔹 Software & Applications ⭐ HIGH IMPACT

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `installed_software` | `array[string]` | Installed applications | `["Docker 20.10.12", "Jenkins 2.346.1"]` |
| `browser_extensions` | `array[string]` | Browser extensions | `["LastPass", "Grammarly"]` |
| `database_software` | `array[string]` | Database systems | `["MySQL 5.7.33", "PostgreSQL 13.4"]` |
| `development_tools` | `array[string]` | Dev tools installed | `["Docker", "Git", "Python"]` |

### 🔹 Patch & Vulnerability Management ⭐ CRITICAL IMPACT

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `patch_level` | `string` | Patch status description | `"Up-to-date"`, `"Missing critical patches"` |
| `missing_patches` | `array[string]` | Specific missing patches | `["KB5012345", "USN-5361-1"]` |
| `os_end_of_life` | `boolean` | OS is end-of-life | `true`, `false` |
| `vulnerability_score` | `float` | CVSS or VPR score | `9.8`, `7.5` |
| `critical_vuln_count` | `integer` | Number of critical vulns | `3`, `0` |

### 🔹 Configuration & Compliance

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `configurations` | `array[string]` | Misconfigurations found | `["Docker socket exposed", "Weak SSH config"]` |
| `compliance_gaps` | `array[string]` | Compliance violations | `["PCI-DSS 8.2.3 failed", "HIPAA non-compliant"]` |
| `security_recommendations` | `array[string]` | Security improvements | `["Enable MFA", "Update OpenSSL"]` |

### 🔹 Asset Context & Risk ⭐ HIGH IMPACT

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `asset_criticality` | `string` | Business criticality | `"Critical"`, `"High"`, `"Medium"`, `"Low"` |
| `business_role` | `string` | Asset function | `"Web Server"`, `"Database"`, `"Domain Controller"` |
| `data_classification` | `string` | Data sensitivity | `"Restricted"`, `"Confidential"`, `"Internal"` |
| `environment` | `string` | Environment type | `"Production"`, `"Staging"`, `"Development"` |

### 🔹 Cloud & Containers

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `cloud_provider` | `string` | Cloud provider | `"AWS"`, `"Azure"`, `"GCP"`, `"None"` |
| `cloud_instance_type` | `string` | Instance type | `"t3.medium"`, `"Standard_D2s_v3"` |
| `cloud_iam_roles` | `array[string]` | IAM roles/permissions | `["EC2InstanceRole", "S3ReadAccess"]` |
| `container_runtime` | `string` | Container runtime | `"Docker 20.10.12"`, `"containerd"` |
| `kubernetes_cluster` | `string` | K8s cluster name | `"prod-cluster-01"` |

### 🔹 Backup & Storage

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `backup_system` | `string` | Backup solution | `"Veeam"`, `"rsync"`, `"AWS Backup"` |
| `backup_location` | `string` | Backup storage location | `"/backup"`, `"s3://backups"` |

### 🔹 Threat Intelligence

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `threat_intel_matches` | `array[string]` | Known IOCs detected | `["IP in recent scan activity"]` |
| `known_exploits` | `array[string]` | Applicable exploits | `["Metasploit module available"]` |

---

## Impact Analysis

### Critical Impact Parameters (Implement First)
These parameters have the **highest impact** on attack path accuracy:

1. **`security_controls`** - Determines evasion tactics
2. **`network_segment`** - Affects lateral movement strategies
3. **`admin_accounts`** - Privilege escalation targets
4. **`installed_software`** - Additional attack vectors
5. **`patch_level` / `missing_patches`** - Exploitability
6. **`asset_criticality`** - Risk assessment
7. **`configurations`** - Specific weaknesses to exploit
8. **`internet_exposed`** - Attack surface
9. **`mfa_enabled`** - Credential access difficulty
10. **`domain_membership`** - Lateral movement opportunities

---

## Example Requests

### Basic Request (Few Parameters)

```json
{
  "platform": "Linux",
  "version_os": "Ubuntu 20.04.3 LTS",
  "open_ports": [22, 80, 443],
  "services": [
    "OpenSSH 8.2p1 on port 22",
    "Apache httpd 2.4.41 on port 80"
  ],
  "vulnerabilities": [
    "CVE-2023-12345: SQL Injection"
  ]
}
```

### Comprehensive Request (More Context)
```json
{
  "platform": "Linux",
  "version_os": "Ubuntu 20.04.3 LTS",
  "asset_name": "web-prod-01",
  "fqdn": "web-prod-01.corp.example.com",
  "ip_addresses": ["10.0.1.50", "203.0.113.42"],
  
  "network_segment": "DMZ",
  "internet_exposed": true,
  
  "open_ports": [22, 80, 443, 3306],
  "services": [
    "OpenSSH 8.2p1 on port 22",
    "Apache httpd 2.4.41 on port 80",
    "MySQL 5.7.33 on port 3306"
  ],
  
  "vulnerabilities": [
    "CVE-2023-12345: SQL Injection",
    "CVE-2023-23456: Outdated SSH version"
  ],
  "critical_vuln_count": 2,
  
  "security_controls": [
    "CrowdStrike Falcon EDR - Active",
    "pfSense Firewall"
  ],
  "mfa_enabled": false,
  
  "domain_membership": "corp.example.com",
  "admin_accounts": ["root", "dbadmin"],
  
  "installed_software": [
    "Docker 20.10.12",
    "Jenkins 2.346.1"
  ],
  
  "patch_level": "Missing critical patches",
  "configurations": [
    "Docker socket exposed on 0.0.0.0:2375",
    "MySQL root accessible remotely"
  ],
  
  "asset_criticality": "High",
  "business_role": "Production Web Server",
  "environment": "Production"
}
```

---

## How the Dynamic Prompt Builder Works

The prompt builder intelligently constructs prompts based on available data:

1. **Conditional Sections**: Only includes sections where data is provided
2. **Contextual Instructions**: Tells the LLM to reference specific details
3. **Priority Indicators**: Highlights critical fields (🎯, ⚠️, 🔑)
4. **Smart Formatting**: Handles None/empty values gracefully

### Example Output Sections

With minimal data:
```
=== CORE SYSTEM INFO ===
- Platform: Linux
- OS Version: Ubuntu 20.04
```

With enhanced data:
```
=== CORE SYSTEM INFO ===
- Platform: Linux
- OS Version: Ubuntu 20.04

=== ASSET CONTEXT (HIGH PRIORITY FOR RISK ASSESSMENT) ===
- 🎯 Asset Criticality: High
- Business Role: Production Web Server
- Environment: Production

=== SECURITY CONTROLS (CONSIDER FOR EVASION) ===
- Security Controls:
  • CrowdStrike Falcon EDR - Active
  • pfSense Firewall

=== MISCONFIGURATIONS & WEAKNESSES ===
- ⚠️ Misconfigurations:
  • Docker socket exposed on 0.0.0.0:2375
  • MySQL root accessible remotely
```

---

## Integration Guide

### From Vulnerability Scanners

Map scanner output to AI Engine parameters:

```python
# Example mapping from external scanner
payload = {
    "platform": scan_results.os_type,
    "version_os": scan_results.os_version,
    "open_ports": scan_results.ports,
    "services": scan_results.detected_services,
    "vulnerabilities": scan_results.cves,
    "network_segment": scan_results.network_zone,
    "security_controls": scan_results.security_agents,
    "patch_level": scan_results.patch_status,
    "asset_criticality": asset_db.get_criticality(asset_id),
    # ... add as many fields as available
}
```

### Best Practices

1. **Send All Available Data**: More context = better results
2. **Prioritize High-Impact Fields**: Focus on security controls, network context, and asset criticality
3. **Keep Data Current**: Update regularly as configurations change
4. **Use Specific Descriptions**: Provide detailed service versions and CVE information
5. **Include Business Context**: Asset criticality and role improve risk assessment

---

## Validation

All parameters are validated using Pydantic models:

- ✅ Type checking (string, int, bool, arrays)
- ✅ Optional fields (all fields are optional)
- ✅ Schema validation
- ✅ Automatic documentation generation

---

## Support

For questions or feature requests, please refer to:
- `TECHNICAL_SPECIFICATION.md` - Architecture details
- `USAGE.md` - API usage guide
- `example_request_enhanced.json` - Full example
- `example_request_minimal.json` - Minimal example
