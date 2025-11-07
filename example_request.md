# example_request

```bash
curl -X POST http://127.0.0.1:8000/attack-path/markdown \
  -H "Content-Type: application/json" \
  -d '{
    "asset_name": "haris-PC",
    "asset_id": "HARIS-PC",
    "fqdn": "haris-PC.WORKGROUP",
    "ip_addresses": ["10.129.80.126"],
    "platform": "Windows",
    "version_os": "Windows 7 Professional 7601 Service Pack 1",
    "os_end_of_life": true,
    "asset_criticality": "Medium",
    "business_role": "Workstation",
    "environment": "Production",
    "network_segment": "WORKGROUP",
    "internet_exposed": true,
    "open_ports": [135, 139, 445, 49152, 49153, 49154, 49155, 49156, 49157],
    "services": [
      "Microsoft Windows RPC (port 135)",
      "NetBIOS-SSN (port 139)",
      "Microsoft-DS SMB (port 445)",
      "Microsoft Windows RPC (ports 49152-49157)"
    ],
    "vulnerabilities": [
      "CVE-2017-0143: MS17-010 EternalBlue - SMBv1 Remote Code Execution",
      "CVE-2017-0144: MS17-010 - SMBv1 Remote Code Execution",
      "CVE-2017-0145: MS17-010 - SMBv1 Remote Code Execution"
    ],
    "vulnerability_score": 9.8,
    "critical_vuln_count": 6,
    "patch_level": "Service Pack 1 (Outdated)",
    "missing_patches": ["MS17-010 (March 2017 Security Update)"],
    "domain_membership": "WORKGROUP",
    "user_accounts": ["guest"],
    "mfa_enabled": false,
    "configurations": [
      "SMB message signing disabled (dangerous, but default)",
      "Guest account authentication enabled",
      "SMBv1 protocol enabled (vulnerable to MS17-010)"
    ],
    "threat_intel_matches": [
      "MS17-010 EternalBlue - Actively exploited by WannaCry, NotPetya"
    ],
    "known_exploits": [
      "EternalBlue (NSA exploit)",
      "MS17-010 Metasploit modules available"
    ]
  }' -o haris-pc_attack_path-23.md


``
```
