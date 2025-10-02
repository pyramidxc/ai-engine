#!/usr/bin/env python3
"""
Test script for the Attack Path Engine
Requires the API to be running on localhost:8000
"""
import asyncio
import json
from app.main import InputHost, attack_path

async def test_attack_path():
    """Test the attack path generation with sample data"""
    
    # Sample host data
    test_host = InputHost(
        platform="Linux",
        version_os="Ubuntu 20.04.3 LTS",
        open_ports=[22, 80, 443, 3306],
        services=[
            "OpenSSH 8.2p1 on port 22",
            "Apache httpd 2.4.41 on port 80",
            "Apache httpd 2.4.41 (SSL) on port 443",
            "MySQL 5.7.33 on port 3306"
        ],
        vulnerabilities=[
            "CVE-2023-12345: SQL Injection in web application",
            "CVE-2023-23456: Outdated SSH version with known exploits",
            "CVE-2023-34567: MySQL running with default credentials"
        ]
    )
    
    print("=" * 60)
    print("Testing Attack Path Engine")
    print("=" * 50)
    print(f"\nPlatform: {test_host.platform}")
    print(f"OS Version: {test_host.version_os}")
    print(f"Open Ports: {test_host.open_ports}")
    print(f"Services: {len(test_host.services)}")
    print(f"Vulnerabilities: {len(test_host.vulnerabilities)}")
    print("\n" + "=" * 60)
    print("Generating attack path...")
    print("=" * 60 + "\n")
    
    try:
        # Call the attack_path function
        result = await attack_path(test_host)
        
        print(f"✅ Attack Path Generated!\n")
        print(f"🎯 Risk Level: {result.risk_level}")
        print(f"\n📍 Attack Path ({len(result.attack_path)} steps):")
        for i, step in enumerate(result.attack_path, 1):
            print(f"   {step}")
        
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
