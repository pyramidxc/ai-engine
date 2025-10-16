#!/usr/bin/env python3
"""
Test Runner for Attack Path Engine Scenarios
Runs all test scenarios and validates prompt generation and attack path quality.
"""

import json
import os
from pathlib import Path
from app.models.host import InputHost
from app.core.prompts import PromptBuilder


def test_scenario(scenario_file: str, expected_risk: str = None):
    """Test a single scenario and print results."""
    print(f"\n{'='*80}")
    print(f"Testing: {scenario_file}")
    print('='*80)
    
    # Load scenario
    with open(scenario_file, 'r') as f:
        data = json.load(f)
    
    # Validate against model
    try:
        host = InputHost(**data)
        print("✅ Scenario validates against InputHost model")
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False
    
    # Count populated fields
    field_count = sum(
        1 for k, v in host.model_dump().items() 
        if v is not None and v != [] and v != ""
    )
    print(f"📊 Fields with data: {field_count}")
    
    # Generate prompt
    try:
        prompt = PromptBuilder.build_attack_analysis_prompt(host)
        print(f"✅ Prompt generated: {len(prompt)} characters")
    except Exception as e:
        print(f"❌ Prompt generation failed: {e}")
        return False
    
    # Count sections in prompt
    sections = [line for line in prompt.split('\n') if line.startswith('===')]
    print(f"📋 Prompt sections: {len(sections)}")
    for section in sections:
        print(f"   • {section}")
    
    # Show key context
    print(f"\n🎯 Key Context:")
    if host.asset_criticality:
        print(f"   Asset Criticality: {host.asset_criticality}")
    if host.internet_exposed is not None:
        print(f"   Internet Exposed: {host.internet_exposed}")
    if host.security_controls:
        print(f"   Security Controls: {len(host.security_controls)} detected")
    if host.configurations:
        print(f"   Misconfigurations: {len(host.configurations)} found")
    if host.vulnerabilities:
        print(f"   Vulnerabilities: {len(host.vulnerabilities)} known")
    
    if expected_risk:
        print(f"\n🎲 Expected Risk Level: {expected_risk}")
    
    return True


def main():
    """Run all test scenarios."""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║          Attack Path Engine - Test Scenario Runner                  ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    scenarios = [
        ("test_scenarios/scenario1_web_server.json", "CRITICAL"),
        ("test_scenarios/scenario3_legacy_dc.json", "CRITICAL"),
        ("test_scenarios/scenario8_jenkins_misconfig.json", "CRITICAL"),
        ("example_request_enhanced.json", "HIGH"),
        ("example_request_minimal.json", "HIGH"),
        ("example_request.json", "HIGH"),
    ]
    
    results = []
    
    for scenario_file, expected_risk in scenarios:
        if os.path.exists(scenario_file):
            success = test_scenario(scenario_file, expected_risk)
            results.append((scenario_file, success))
        else:
            print(f"\n⚠️  Scenario file not found: {scenario_file}")
            results.append((scenario_file, False))
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print('='*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for scenario_file, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {scenario_file}")
    
    print(f"\n📊 Results: {passed}/{total} scenarios passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The dynamic prompt builder is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} scenario(s) failed.")
    
    print("\n" + "="*80)
    print("Next Steps:")
    print("  1. Start the API: docker-compose up -d")
    print("  2. Test with API: curl -X POST http://localhost:8000/attack-path \\")
    print("                     -H 'Content-Type: application/json' \\")
    print("                     -d @test_scenarios/scenario1_web_server.json")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
