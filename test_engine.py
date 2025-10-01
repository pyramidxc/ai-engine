#!/usr/bin/env python3
"""
Test script for the Attack Path Engine
"""
import asyncio
import json
from app.main import InputHost, attack_path

async def test_attack_path():
    """Test the attack path generation with sample data"""
    
    # Sample host data
    test_host = InputHost(
        hostname="test-server.example.com",
        open_ports=[22, 80, 443, 3306],
        vulnerabilities=[
            "CVE-2023-12345: SQL Injection in web application",
            "CVE-2023-23456: Outdated SSH version with known exploits",
            "CVE-2023-34567: MySQL running with default credentials"
        ]
    )
    
    print("=" * 60)
    print("Testing Attack Path Engine")
    print("=" * 60)
    print(f"\nHost: {test_host.hostname}")
    print(f"Open Ports: {test_host.open_ports}")
    print(f"Vulnerabilities: {len(test_host.vulnerabilities)}")
    print("\n" + "=" * 60)
    print("Generating attack path analysis...")
    print("=" * 60 + "\n")
    
    try:
        # Call the attack_path function
        result = await attack_path(test_host)
        
        print(f"✅ Analysis Complete!\n")
        print(f"🎯 Risk Level: {result.risk_level}")
        print(f"\n📍 Attack Path:")
        for i, step in enumerate(result.attack_path, 1):
            print(f"   {i}. {step}")
        
        print(f"\n🛡️  Security Recommendations:")
        for i, rec in enumerate(result.recommendations, 1):
            print(f"   {i}. {rec}")
        
        print("\n" + "=" * 60)
        print("✅ Test completed successfully!")
        print("=" * 60)
        
        # Save result to file
        with open("test_result.json", "w") as f:
            json.dump(result.model_dump(), f, indent=2)
        print("\n💾 Result saved to test_result.json")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nPlease check:")
        print("  1. Your API key is set in .env file")
        print("  2. You have installed litellm: pip install litellm")
        print("  3. Your API key has sufficient credits")
        raise

if __name__ == "__main__":
    asyncio.run(test_attack_path())
