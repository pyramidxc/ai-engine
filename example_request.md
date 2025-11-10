# example_request

```bash
curl -X POST http://127.0.0.1:8000/attack-path \
  -H "Content-Type: application/json" \
  -d '{
    "OperatingSystem": "Windows Server 2019 Standard",
    "OperatingSystemVersion": "10.0.17763",
    "DNSHostName": "dc01.corp.local",
    "IPv4Address": "10.0.10.50",
    "ServicePrincipalNames": [
      "ldap/dc01.corp.local",
      "ldap/dc01"
    ],
    "TrustedForDelegation": true,
    "SamAccountName": "administrator",
    "DistinguishedName": "CN=Administrator,CN=Users,DC=corp,DC=local",
    "Name": "Administrator",
    "objectSid": "S-1-5-21-3623811015-3361044348-30300820-500",
    "DomainName": "corp.local",
    "Enabled": true,
    "adminCount": 1,
    "PasswordNeverExpires": true,
    "MemberOf": [
      "CN=Domain Admins,CN=Users,DC=corp,DC=local",
      "CN=Administrators,CN=Builtin,DC=corp,DC=local"
    ]
  }' -o dc01_attack_path.md
```
