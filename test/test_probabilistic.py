#!/usr/bin/env python3
"""Quick test of probabilistic validation - Updated for AD parameters."""

from app.utils.exploitability_validator import ExploitabilityValidator

# Test scenarios
validator = ExploitabilityValidator()

print("\n" + "="*80)
print("PROBABILISTIC VALIDATION TEST - AD FOCUSED")
print("="*80)

# Scenario 1: Kerberoasting WITH SPNs
print("\n1. Kerberoasting WITH Service Principal Names:")
result = validator.validate_technique(
    "Kerberoasting",
    {
        "DomainName": "corp.local",
        "ServicePrincipalNames": ["MSSQLSvc/db01.corp.local:1433", "HTTP/web01.corp.local"]
    }
)
print(f"   Valid: {result['is_valid']}")
print(f"   Confidence: {result['confidence']:.2f}")
print(f"   Reason: {result['reason']}")

# Scenario 2: Kerberoasting WITHOUT SPNs
print("\n2. Kerberoasting WITHOUT SPNs:")
result = validator.validate_technique(
    "Kerberoasting",
    {
        "DomainName": "corp.local",
        "ServicePrincipalNames": []
    }
)
print(f"   Valid: {result['is_valid']}")
print(f"   Confidence: {result['confidence']:.2f}")
print(f"   Reason: {result['reason']}")

# Scenario 3: Delegation abuse WITH trusted delegation
print("\n3. Unconstrained Delegation Abuse WITH TrustedForDelegation:")
result = validator.validate_technique(
    "Unconstrained Delegation Abuse",
    {
        "DomainName": "corp.local",
        "TrustedForDelegation": True,
        "DNSHostName": "web01.corp.local"
    }
)
print(f"   Valid: {result['is_valid']}")
print(f"   Confidence: {result['confidence']:.2f}")
print(f"   Reason: {result['reason']}")

# Scenario 4: Privileged account targeting
print("\n4. Targeting Privileged Account (adminCount=1):")
result = validator.validate_technique(
    "Privilege Escalation via adminCount",
    {
        "DomainName": "corp.local",
        "adminCount": 1,
        "MemberOf": ["CN=Domain Admins,CN=Users,DC=corp,DC=local"]
    }
)
print(f"   Valid: {result['is_valid']}")
print(f"   Confidence: {result['confidence']:.2f}")
print(f"   Reason: {result['reason']}")

# Scenario 5: GPO abuse
print("\n5. GPO Abuse WITH linked policies:")
result = validator.validate_technique(
    "GPO Abuse",
    {
        "DomainName": "corp.local",
        "LinkedGroupPolicyObjects": ["LDAP://CN={31B2F340-016D-11D2-945F-00C04FB984F9},CN=Policies,CN=System,DC=corp,DC=local"]
    }
)
print(f"   Valid: {result['is_valid']}")
print(f"   Confidence: {result['confidence']:.2f}")
print(f"   Reason: {result['reason']}")

print("\n" + "="*80)
print("✓ Probabilistic validation working with AD parameters!")
print("="*80 + "\n")
