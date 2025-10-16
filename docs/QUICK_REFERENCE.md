# Quick Reference: High-Impact Parameters

## 🔥 Top 10 Parameters to Implement First

These parameters have the **highest impact** on attack path accuracy:

| # | Parameter | Type | Why It Matters | Example |
|---|-----------|------|----------------|---------|
| 1 | `security_controls` | `array[string]` | **EDR/firewall evasion tactics** | `["CrowdStrike Falcon EDR"]` |
| 2 | `network_segment` | `string` | **Lateral movement strategy** | `"DMZ"`, `"Internal"` |
| 3 | `admin_accounts` | `array[string]` | **Privilege escalation targets** | `["root", "Administrator"]` |
| 4 | `installed_software` | `array[string]` | **Additional attack vectors** | `["Docker", "Jenkins"]` |
| 5 | `patch_level` | `string` | **Exploit viability** | `"Missing critical patches"` |
| 6 | `asset_criticality` | `string` | **Risk assessment weight** | `"High"`, `"Critical"` |
| 7 | `configurations` | `array[string]` | **Specific weaknesses to exploit** | `["Docker socket exposed"]` |
| 8 | `internet_exposed` | `boolean` | **Attack surface scope** | `true`, `false` |
| 9 | `mfa_enabled` | `boolean` | **Credential access difficulty** | `true`, `false` |
| 10 | `domain_membership` | `string` | **Lateral movement potential** | `"corp.example.com"` |

---

## 📋 Quick Implementation Checklist

### Phase 1: Critical (Week 1)
- [ ] `security_controls` - EDR, antivirus, firewall
- [ ] `network_segment` - Network location
- [ ] `admin_accounts` - Privileged accounts
- [ ] `asset_criticality` - Business importance
- [ ] `configurations` - Misconfigurations

### Phase 2: High-Value (Week 2)
- [ ] `installed_software` - Application inventory
- [ ] `patch_level` - Patch status
- [ ] `internet_exposed` - External exposure
- [ ] `mfa_enabled` - MFA status
- [ ] `domain_membership` - AD domain

### Phase 3: Enhanced Context (Week 3-4)
- [ ] `user_accounts` - User list
- [ ] `service_accounts` - Service accounts
- [ ] `password_policy` - Password strength
- [ ] `business_role` - Asset function
- [ ] `environment` - Prod/dev/staging
- [ ] `cloud_provider` - Cloud platform
- [ ] `missing_patches` - Specific patches
- [ ] `vulnerability_score` - CVSS/VPR
- [ ] `backup_location` - Backup location
- [ ] `threat_intel_matches` - IOCs

---

## 🎯 Impact Matrix

| Parameter Category | Attack Path Accuracy | Implementation Effort | Priority |
|-------------------|---------------------|---------------------|----------|
| Security Controls | 🔥🔥🔥🔥🔥 | Medium | **CRITICAL** |
| Network Context | 🔥🔥🔥🔥 | Low | **HIGH** |
| Identity/Access | 🔥🔥🔥🔥 | Low | **HIGH** |
| Asset Context | 🔥🔥🔥🔥 | Low | **HIGH** |
| Configurations | 🔥🔥🔥🔥 | Low | **HIGH** |
| Software/Apps | 🔥🔥🔥 | Low | MEDIUM |
| Patch Status | 🔥🔥🔥 | Medium | MEDIUM |
| Cloud/Container | 🔥🔥 | Medium | MEDIUM |
| Backup/Storage | 🔥🔥 | Low | LOW |
| Hardware | 🔥 | Low | LOW |

---

## 💡 Before & After Examples

### Minimal Request (5 params)
```json
{
  "platform": "Linux",
  "version_os": "Ubuntu 20.04",
  "open_ports": [22, 80],
  "services": ["OpenSSH 8.2p1", "Apache 2.4.41"],
  "vulnerabilities": ["CVE-2023-12345"]
}
```
**Result**: Generic attack path, basic risk assessment

---

### Enhanced Request (15+ params)
```json
{
  "platform": "Linux",
  "version_os": "Ubuntu 20.04",
  "network_segment": "DMZ",
  "internet_exposed": true,
  "open_ports": [22, 80, 2375],
  "services": ["OpenSSH 8.2p1", "Apache 2.4.41", "Docker API"],
  "vulnerabilities": ["CVE-2023-12345"],
  "security_controls": ["CrowdStrike Falcon EDR"],
  "admin_accounts": ["root", "dbadmin"],
  "installed_software": ["Docker", "Jenkins"],
  "configurations": ["Docker socket exposed on 0.0.0.0:2375"],
  "mfa_enabled": false,
  "asset_criticality": "High",
  "business_role": "Production Web Server",
  "environment": "Production"
}
```
**Result**: 
- ✅ EDR evasion techniques
- ✅ Specific Docker socket exploitation
- ✅ Targets "root" and "dbadmin" accounts
- ✅ Risk considers "High" criticality + "Production" environment
- ✅ Lateral movement from DMZ

---

## 🚀 Quick Start

1. **Keep your existing 5 parameters** (backward compatible)
2. **Add these 5 high-impact fields** immediately:
   ```json
   {
     "platform": "Linux",
     "version_os": "Ubuntu 20.04",
     "open_ports": [22, 80],
     "services": ["SSH", "Apache"],
     "vulnerabilities": ["CVE-2023-12345"],
     
     // ADD THESE 5
     "network_segment": "DMZ",
     "security_controls": ["CrowdStrike EDR"],
     "asset_criticality": "High",
     "mfa_enabled": false,
     "configurations": ["Docker socket exposed"]
   }
   ```
3. **See immediate improvement** in attack path quality
4. **Gradually add more fields** from the checklist above

---

## 📊 Expected Results

| Fields Used | Prompt Size | Attack Path Quality | Context Awareness |
|-------------|-------------|---------------------|-------------------|
| 5 (minimal) | ~5.5 KB | ⭐⭐ Basic | Generic |
| 15 (good) | ~7 KB | ⭐⭐⭐⭐ Good | Contextual |
| 30+ (excellent) | ~9 KB | ⭐⭐⭐⭐⭐ Excellent | Highly Specific |

---

## 🔍 How to Check Your Data

```python
from app.models.host import InputHost
import json

# Load your request
with open('your_request.json', 'r') as f:
    data = json.load(f)

# Validate and count fields
host = InputHost(**data)
field_count = sum(1 for k, v in host.model_dump().items() 
                  if v is not None and v != [] and v != "")

print(f"✅ Valid request with {field_count} fields")

# 5-10 fields: Basic
# 11-20 fields: Good  
# 21-30 fields: Very Good
# 31+ fields: Excellent
```

---

## 📖 Full Documentation

- **Complete Parameter List**: `docs/INPUT_PARAMETERS.md`
- **Implementation Guide**: `docs/IMPLEMENTATION_SUMMARY.md`
- **Examples**: `example_request_enhanced.json`, `example_request_minimal.json`
