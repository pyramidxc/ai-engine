# Phase 1 Scope: Attack Path Engine

## Vision Statement

The AI-powered Attack Path Generator is a microservice that **generates realistic attack sequences** from vulnerability and exposure data collected by external systems. It focuses solely on demonstrating **how an attacker would exploit identified weaknesses** through step-by-step attack paths.

## What We Are

✅ **Attack Path Generator**: We generate sequential attack scenarios based on collected data  
✅ **AI-Powered**: We use LLMs to create realistic, technical attack sequences  
✅ **Collector-Integrated**: We process data from external vulnerability scanners and assessment tools  
✅ **Risk Assessor**: We classify the overall risk level (Critical, High, Medium, Low)  

## What We Are NOT (Yet)

❌ **Remediation Provider**: We do not generate security recommendations (Phase 2)  
❌ **Compliance Mapper**: We do not map to security frameworks (Phase 2)  
❌ **Threat Intelligence**: We do not integrate external threat feeds (Phase 2)  
❌ **Vulnerability Scanner**: We do not collect data - external collectors do this  

---

## Phase 1: Core Functionality

### Input (From External Collectors)

```json
{
  "platform": "Linux",
  "version_os": "Ubuntu 20.04.3 LTS",
  "open_ports": [22, 80, 443, 3306],
  "services": [
    "OpenSSH 8.2p1 on port 22",
    "Apache httpd 2.4.41 on port 80",
    "Apache httpd 2.4.41 (SSL) on port 443",
    "MySQL 5.7.33 on port 3306"
  ],
  "vulnerabilities": [
    "CVE-2023-12345: SQL Injection in web application",
    "CVE-2023-23456: Outdated SSH version",
    "CVE-2023-34567: MySQL with default credentials"
  ]
}
```

### Output (Generated Attack Path)

```json
{
  "platform": "Linux",
  "version_os": "Ubuntu 20.04.3 LTS",
  "attack_path": [
    "Reconnaissance: Active network scanning using nmap (MITRE T1595.002) reveals Ubuntu server with OpenSSH 8.2p1, Apache 2.4.41, MySQL 5.7.33",
    "Weaponization: Prepare SQL injection exploit for Apache/MySQL stack targeting CVE-2023-12345. Tool: sqlmap with tamper scripts for WAF bypass",
    "Delivery: Direct exploitation via HTTP POST to /login.php endpoint (MITRE T1190 - Exploit Public-Facing Application)",
    "Exploitation: SQL injection successful - UNION-based technique extracts MySQL root credentials. Payload: ' UNION SELECT user,password FROM mysql.user--",
    "Installation: Establish persistence via cron job on Linux (MITRE T1053.003). Command: echo '*/5 * * * * /tmp/.update' >> /var/spool/cron/crontabs/www-data",
    "Command and Control: Setup reverse HTTPS shell using Metasploit (MITRE T1071.001). msfvenom payload with SSL encryption to attacker C2 server",
    "Actions on Objectives: Credential dumping /etc/shadow (T1003.008), lateral SSH movement (T1021.004), database exfiltration over encrypted channel (T1048.002)"
  ],
  "risk_level": "Critical"
}
```

### Key Features

1. **Realistic Attack Sequences**
   - Step-by-step progression from reconnaissance to compromise
   - Technical details showing actual exploitation methods
   - Logical flow demonstrating attacker thinking

2. **Risk Assessment**
   - Critical: Remote code execution, full system compromise
   - High: Privilege escalation, significant data access
   - Medium: Limited access, requires additional steps
   - Low: Minimal impact, complex exploitation

3. **AI-Powered Generation**
   - Uses LLMs to create realistic scenarios
   - Supports multiple providers (OpenAI, Anthropic, Google, etc.)
   - Contextual understanding of vulnerability relationships

---

## Phase 2: Future Enhancements

### Planned Features (Not in Current Scope)

1. **Remediation Recommendations**
   - Generate security recommendations
   - Prioritize fixes based on risk
   - Provide step-by-step mitigation guides

2. **Compliance Mapping**
   - Map attack paths to security frameworks
   - NIST, ISO 27001, CIS Controls
   - Generate compliance reports

3. **Threat Intelligence Integration**
   - Incorporate external threat feeds
   - Real-world exploit likelihood
   - Active exploitation indicators

4. **Attack Simulation Playbooks**
   - Generate executable test scenarios
   - Integration with red team tools
   - Automated penetration testing guides

---

## Architecture Alignment

### Current Implementation

```bash

External Collector → Attack Path Engine → Attack Sequence + Risk
     (Nmap, etc.)         (This System)           (JSON Output)
```

### Data Flow

1. **External collector** scans target system
2. Collector sends vulnerability/port data to our API
3. **PromptBuilder** transforms data into generation prompt
4. **LLM** generates realistic attack sequence
5. **Analyzer** validates and structures response
6. **API** returns attack path + risk level

### Phase 2 Integration (Future)

```bash
External Collector → Attack Path Engine → Remediation Engine → Complete Analysis
                          (Phase 1)              (Phase 2)
```

## Development Guidelines

### Do's ✅

- Focus on **realistic attack sequence generation**
- Ensure **logical progression** in attack steps
- Include **technical details** in each step
- Validate data from **external collectors**
- Optimize prompts for **attack path quality**
- Support **multiple LLM providers**

### Don'ts ❌

- Don't add remediation features (Phase 2)
- Don't scan or collect data ourselves
- Don't map to compliance frameworks yet
- Don't integrate threat intelligence yet
- Don't generate defensive recommendations

---

## API Contract

### Endpoint: POST `/attack-path`

**Purpose**: Generate attack path from collector data

**Input Schema** (from external collectors):

- `platform`: Operating system platform (Linux, Windows, macOS, etc.)
- `version_os`: Specific OS version (e.g., "Ubuntu 20.04.3 LTS")
- `open_ports`: List of accessible ports
- `services`: List of services with versions running on ports
- `vulnerabilities`: List of CVEs or vulnerability descriptions

**Output Schema**:

- `platform`: Target system platform
- `version_os`: Target system OS version
- `attack_path`: Ordered list of attack steps with MITRE ATT&CK mappings
- `risk_level`: Overall risk assessment

**No remediation fields** - this is Phase 2

---

## Testing Focus

### Phase 1 Tests Should Cover

1. **Attack Path Quality**
   - Steps are sequential and logical
   - Technical accuracy of exploitation methods
   - Realistic attacker behavior

2. **Risk Assessment Accuracy**
   - Correct classification based on impact
   - Consistency across similar vulnerabilities

3. **Input Validation**
   - Handle various collector data formats
   - Graceful handling of incomplete data

4. **LLM Integration**
   - Multiple provider support
   - Error handling for API failures
   - Response parsing and validation

---

## Success Metrics (Phase 1)

1. **Generation Quality**
   - Attack paths are technically accurate
   - Steps follow realistic progression
   - Risk levels match severity

2. **Performance**
   - Response time < 5 seconds (LLM dependent)
   - High availability (99.9%)
   - Support for concurrent requests

3. **Integration**
   - Easy integration with external collectors
   - Clear API documentation
   - Multiple LLM provider support

---

## Summary

**Phase 1 = Attack Path Generation Only**
We are building a focused, high-quality attack path engine that:

- Takes data from external collectors
- Generates realistic attack sequences
- Assesses overall risk level
- Provides JSON output for integration

Remediation, compliance, and threat intelligence are **Phase 2** features that will be added to the existing architecture without breaking changes.

---

Last Updated: October 1, 2025
