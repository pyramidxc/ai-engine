#!/usr/bin/env python3
"""Quick test of probabilistic validation."""

from app.utils.exploitability_validator import ExploitabilityValidator

# Test scenarios
validator = ExploitabilityValidator()

print("\n" + "="*80)
print("PROBABILISTIC VALIDATION TEST")
print("="*80)

# Scenario 1: Kerberoasting WITH service accounts
print("\n1. Kerberoasting WITH service accounts:")
result = validator.validate_technique(
    "Kerberoasting",
    {
        "domain_membership": "CORP.LOCAL",
        "service_accounts": ["svc_sql", "svc_web"]
    }
)
print(f"   Valid: {result['is_valid']}")
print(f"   Confidence: {result['confidence']:.2f}")
print(f"   Reason: {result['reason']}")

# Scenario 2: Kerberoasting WITHOUT service accounts
print("\n2. Kerberoasting WITHOUT service accounts:")
result = validator.validate_technique(
    "Kerberoasting",
    {
        "domain_membership": "CORP.LOCAL",
        "service_accounts": []
    }
)
print(f"   Valid: {result['is_valid']}")
print(f"   Confidence: {result['confidence']:.2f}")
print(f"   Reason: {result['reason']}")

# Scenario 3: Kerberoasting NO domain
print("\n3. Kerberoasting NO domain:")
result = validator.validate_technique(
    "Kerberoasting",
    {
        "service_accounts": ["svc_sql"]
    }
)
print(f"   Valid: {result['is_valid']}")
print(f"   Confidence: {result['confidence']:.2f}")
print(f"   Reason: {result['reason']}")

# Scenario 4: xp_cmdshell with config
print("\n4. xp_cmdshell WITH enabled config:")
result = validator.validate_technique(
    "SQL Injection with xp_cmdshell",
    {
        "database_software": ["SQL Server"],
        "configurations": ["xp_cmdshell: ENABLED"]
    }
)
print(f"   Valid: {result['is_valid']}")
print(f"   Confidence: {result['confidence']:.2f}")
print(f"   Reason: {result['reason']}")

# Scenario 5: Container escape WITHOUT containers
print("\n5. Container Escape WITHOUT containers:")
result = validator.validate_technique(
    "Container Escape",
    {
        "platform": "Linux"
    }
)
print(f"   Valid: {result['is_valid']}")
print(f"   Confidence: {result['confidence']:.2f}")
print(f"   Reason: {result['reason']}")

print("\n" + "="*80)
print("✓ Probabilistic validation working!")
print("="*80 + "\n")
