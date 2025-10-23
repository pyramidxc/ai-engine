# Architecture

## System Overview

The Attack Path Engine is a FastAPI-based service that transforms vulnerability data into 7-stage attack path sequences. It accepts 50+ optional host parameters (platform, services, vulnerabilities, security controls, etc.) and generates a coherent, detailed attack narrative with continuity validation across all stages.

## Core Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/attack-path/main` | **PRIMARY**: Generate 7-stage attack path (JSON response) |
| `GET` | `/health` | Health check for monitoring and service discovery |

## Component Architecture

```
┌────────────────────────────────────────┐
│      FastAPI Application               │
│      (app/main.py)                     │
│      Port 8000                         │
└──────────────┬───────────────────────┘
               │
        ┌──────▼────────┐
        │ POST /attack- │
        │ path/main     │
        └──────┬────────┘
               │
        ┌──────▼───────────────────────┐
        │  CompleteAnalyzer Service     │
        │  (app/services/              │
        │   complete_analyzer.py)       │
        │                              │
        │  - Orchestrates 7 LLM calls  │
        │  - Context threading         │
        │  - Artifact extraction       │
        └──────┬──────────────┬────────┘
               │              │
        ┌──────▼───────┐   ┌──▼─────────────────┐
        │ LLMClient    │   │ ContinuityValidator│
        │ (app/        │   │ (app/utils/)       │
        │  services/   │   │                    │
        │  llm_client  │   │ 4 validation checks│
        │  .py)        │   └────────────────────┘
        │              │
        │ 7 sequential │
        │ API calls    │
        └──────────────┘
```

## Input: InputHost Model

**Purpose**: Accept 50+ optional host parameters from vulnerability scanners

**12 Parameter Categories**:

1. **Core System Info** (2 params)
   - `platform`: OS type (Linux, Windows, macOS, etc.)
   - `version_os`: OS version (Ubuntu 20.04, Windows Server 2019, etc.)

2. **Network & Services** (3 params)
   - `open_ports`: List of open ports
   - `services`: Running services with versions
   - `vulnerabilities`: Known CVEs and descriptions

3. **Asset Identification** (5 params)
   - `asset_id`, `asset_name`, `mac_addresses`, `ip_addresses`, `fqdn`

4. **Network Context** (3 params)
   - `network_segment`: DMZ, Internal, Public-facing, etc.
   - `internet_exposed`: Boolean - is publicly accessible
   - `firewall_rules`: Applicable firewall rules

5. **Security Controls** (5 params)
   - `security_controls`: EDR, firewalls, DLP tools, etc.
   - `edr_agent`: EDR/antivirus status
   - `antivirus_status`, `firewall_status`, `encryption_status`

6. **Identity & Access** (7 params)
   - `domain_membership`, `organizational_unit`, `user_accounts`, `admin_accounts`, `service_accounts`
   - `mfa_enabled`, `password_policy`

7. **Software & Applications** (4 params)
   - `installed_software`, `browser_extensions`, `database_software`, `development_tools`

8. **Patch & Vulnerability** (5 params)
   - `patch_level`, `missing_patches`, `os_end_of_life`, `vulnerability_score`, `critical_vuln_count`

9. **Configuration & Compliance** (3 params)
   - `configurations`: Security misconfigurations
   - `compliance_gaps`: PCI, HIPAA, SOC2 violations
   - `security_recommendations`

10. **Asset Context & Risk** (4 params)
    - `asset_criticality`, `business_role`, `data_classification`, `environment`

11. **Cloud & Containers** (5 params)
    - `cloud_provider`, `cloud_instance_type`, `cloud_iam_roles`, `container_runtime`, `kubernetes_cluster`

12. **Backup & Storage** (2 params)
    - `backup_system`, `backup_location`

13. **Threat Intelligence** (2 params)
    - `threat_intel_matches`, `known_exploits`

**Design**: All fields are optional, allowing flexible input from any vulnerability scanner or CMDB

## Processing Flow

```bash
1. POST /attack-path/main with InputHost
    ↓
2. Pydantic validates all 50+ optional fields
    ↓
3. CompleteAnalyzer.analyze(host) begins
    ├─ Create AttackContext + request_id + timestamp
    ├─ Initialize execution timer
    ↓
4. Stage 1: Reconnaissance (LLM call #1)
    ├─ Prompt includes: InputHost context
    ├─ LLM generates markdown response
    ├─ Parse into StageAnalysis object
    ├─ Extract: techniques, summary, findings, tools
    ├─ Log tokens used
    ↓
5. Stages 2-7 (LLM calls #2-7) with context accumulation
    ├─ Stage N prompt includes: InputHost + outputs from stages 1..N-1
    ├─ Parse response to StageAnalysis
    ├─ Extract artifact_name (4-priority pattern matching)
    ├─ Log tokens per stage
    ↓
6. Parse Complete
    ├─ 7x StageAnalysis objects now available
    ├─ Calculate total tokens, execution time
    ├─ Estimate cost
    ↓
7. Run ContinuityValidator
    ├─ Check 1: Artifact continuity (Stage 2 → 3-7)
    ├─ Check 2: Vulnerability continuity (Stage 1 → 2-4)
    ├─ Check 3: Technique alignment (kill chain order)
    ├─ Check 4: Tool consistency (OS/environment match)
    ├─ Aggregate results into validation_report
    ↓
8. Build CompleteAnalysisResponse
    ├─ primary_path: [Stage1, Stage2, ..., Stage7]
    ├─ request_id: Unique identifier
    ├─ execution_time_seconds: Total time
    ├─ llm_calls: {total: 7}
    ├─ estimated_cost: Calculated USD
    ├─ validation_report: Continuity check results
    ↓
9. Return JSON to client (HTTP 200)
```

## Context Threading Strategy

Each stage receives **cumulative** context from prior stages:

```bash
Input: InputHost (50+ params)

Stage 1: Reconnaissance
├─ Reads: InputHost raw data
├─ Outputs: Services found, CVEs identified, attack surface
└─ Result → AttackContext

Stage 2: Weaponization
├─ Reads: InputHost + Stage 1 findings
├─ Uses context to select exploits for identified services/CVEs
├─ Outputs: Payload name, exploitation strategy
└─ Result → AttackContext

Stage 3-7: Cascade pattern
├─ Each receives ALL prior stages' outputs
├─ Builds logically coherent attack narrative
├─ Prevents LLM hallucinations (if stage 2 made up a CVE, it breaks here)
└─ Result → AttackContext

Outcome: Coherent 7-stage attack path
```

## Artifact Extraction (4-Priority Strategy)

Extracts artifact names from Stage 2+ with fallback patterns:

```
Priority 1: Code Block Commands (95% confidence)
├─ msfvenom -o <filename>
├─ curl -O <filename>
├─ wget <filename>
├─ PowerShell -OutFile C:\file.exe
└─ Match pattern in LLM output

Priority 2: Explicit Naming (85% confidence)
├─ "named: payload.exe"
├─ "created file.sh"
├─ "artifact: malware.bin"
└─ Match explicit declaration patterns

Priority 3: Upload/Transfer Commands (70% confidence)
├─ "upload /path/to/payload.exe"
├─ "scp malware.bin to target"
├─ "copy payload.exe"
└─ Match transfer operation patterns

Priority 4: Prior Stage References (60% confidence)
├─ "from Stage 2 exploitation"
├─ "created earlier in weaponization"
├─ "reference to Stage 2 artifact"
└─ Match continuity reference patterns

Result: ~95% artifact detection accuracy
```

## Continuity Validation (4 Checks)

Validates cross-stage coherence:

```
Check 1: Artifact Continuity
├─ Does Stage 2 have artifact_name?
├─ Is same artifact referenced in stages 3-7?
├─ Is naming consistent across all uses?
└─ Result: PASS/WARNING/FAIL

Check 2: Vulnerability Continuity
├─ Does Stage 1 identify a CVE?
├─ Is same CVE exploited in Stage 2/4?
├─ Does exploit match the CVE?
└─ Result: PASS/WARNING/FAIL

Check 3: Technique Alignment
├─ Extract MITRE ATT&CK techniques from all stages
├─ Do techniques follow logical progression?
├─ Are techniques stage-appropriate?
└─ Result: PASS/WARNING/FAIL

Check 4: Tool Consistency
├─ Are tools compatible with target OS?
├─ Do tool dependencies align?
├─ Is environment (Linux/Windows) consistent?
└─ Result: PASS/WARNING/FAIL

Output: validation_report
├─ is_valid: true (all 4 pass) or false (any fail)
├─ total_checks: 4
├─ passes: [list of passed checks]
├─ warnings: [list of issues]
└─ stage_artifacts: {1: null, 2: "payload.exe", 3: "payload.exe", ...}
```

## Output: CompleteAnalysisResponse

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "primary_path": [
    {
      "stage_index": 1,
      "stage_name": "Reconnaissance",
      "phase": "Information Gathering",
      "mitre_techniques": ["T1595", "T1592"],
      "summary": "Identified open SMB ports 139/445 with MS17-010 vulnerability",
      "key_findings": ["Port 139 exposed", "Port 445 exposed", "MS17-010 vulnerable"],
      "tools_used": ["nmap", "shodan"],
      "artifact_name": null,
      "artifact_type": null,
      "commands": ["nmap -sV 10.0.1.50"],
      "content": "## Reconnaissance\nFull markdown content here..."
    },
    {
      "stage_index": 2,
      "stage_name": "Weaponization",
      ...
      "artifact_name": "eternalblue_payload.exe",
      "artifact_type": "Windows PE Executable",
      ...
    },
    // Stages 3-7 similar structure
  ],
  "total_paths": 1,
  "execution_time_seconds": 22.4,
  "llm_calls": {"total": 7},
  "estimated_cost": 0.051,
  "validation_report": {
    "is_valid": true,
    "total_checks": 4,
    "passes": [
      {"stage": 2, "check": "artifact_continuity", "result": "PASS"},
      {"stage": 1, "check": "vulnerability_continuity", "result": "PASS"},
      {"stage": 5, "check": "technique_alignment", "result": "PASS"},
      {"stage": 4, "check": "tool_consistency", "result": "PASS"}
    ],
    "warnings": [],
    "stage_artifacts": {
      "1": null,
      "2": "eternalblue_payload.exe",
      "3": "eternalblue_payload.exe",
      "4": "eternalblue_payload.exe",
      "5": "eternalblue_payload.exe",
      "6": null,
      "7": null
    }
  }
}
```

## Technology Stack

### Core Framework
- **FastAPI 0.100+**: Async web framework with auto-generated OpenAPI docs
- **Pydantic 2.0+**: Data validation with Python type hints
- **Python 3.10+**: Runtime with asyncio support
- **Uvicorn**: ASGI application server

### LLM Integration
- **LiteLLM**: Multi-provider LLM wrapper library
  - Supports 100+ models (OpenAI, Anthropic, Google, Azure, local Ollama, etc.)
  - Default: OpenAI `gpt-4o-mini` via LiteLLM
- **Token Counting**: Built-in usage tracking

### Utilities
- **python-dotenv**: Environment variable loading from .env

### Deployment
- **Docker**: Container orchestration
- **Docker Compose**: Multi-container setup for local development
- **Gunicorn + Uvicorn**: Production ASGI server setup

## Performance Characteristics

### Request Timing (typical 20-second run)
- Input validation: 10-50ms (Pydantic)
- Stage 1 LLM: 2-4s
- Stages 2-7 (6x): 12-18s total
- Response parsing: 200-500ms
- Validation checks: 100-300ms
- JSON serialization: 10-50ms
- **Total: 15-25 seconds** (average: ~20s)

### Token Usage
- Per-request: 8,000-15,000 tokens (varies by input complexity)
- Per-stage: 1,000-2,500 tokens
- Input composition: ~40% input tokens
- Output composition: ~60% output tokens
- **Estimated cost**: $0.015-$0.050 per request (GPT-4o-mini rates)

### Scalability
- **Single instance**: 3-5 concurrent requests (I/O bound on LLM API)
- **CPU usage**: Minimal (mostly waiting on LLM)
- **Memory**: ~200MB base + ~50MB per concurrent request
- **Bottleneck**: LLM provider rate limits

## Security Architecture

### API Key Management
- `OPENAI_API_KEY` in `.env` (local) or environment variable (production)
- `.env` file in `.gitignore` (never committed)
- Key validated at startup if configured
- Never logged or exposed in responses
- Token usage logged separately (no keys in logs)

### Input Validation
- Pydantic validates all 50+ InputHost fields
- Type hints enforce type safety
- String length limits via Field descriptions
- No SQL injection (no database yet)
- LLM injection risk mitigated by context separation

### Output Handling
- Response contains only analysis results (7x StageAnalysis)
- No sensitive input data echoed back
- Error messages are generic (no stack traces)
- Request IDs for tracing without data exposure

### Rate Limiting
- Implement at reverse proxy (Nginx, Kong, etc.) or API gateway
- Per-IP or per-API-key rate limiting recommended
- LLM provider rate limits: 100K tokens/min (OpenAI pro), 3.5K (free)

## 7-Stage Attack Path (Cyber Kill Chain)

| Stage | Name | Purpose | Example Output |
|-------|------|---------|-----------------|
| 1 | Reconnaissance | Target analysis, service enumeration | Open ports, services, CVEs |
| 2 | Weaponization | Exploit selection, payload creation | Payload name, exploitation method |
| 3 | Delivery | Distribution vector | Delivery method, C2 infrastructure |
| 4 | Exploitation | Payload delivery and execution | Exploitation steps, target system |
| 5 | Installation | Persistence mechanism | Persistence method, backdoor setup |
| 6 | Command & Control | C2 communication | C2 infrastructure, communication protocol |
| 7 | Actions on Objectives | Post-exploitation goals | Data exfiltration, lateral movement |

## Extension Points

### Adding New Parameters
1. Add field to `InputHost` model in `app/models/host.py`
2. Use Pydantic `Field()` with description and examples
3. Update prompt in `app/core/prompts.py` to reference new data
4. Test end-to-end

### Changing LLM Models
1. Set `LLM_MODEL` environment variable
2. LiteLLM automatically handles provider differences
3. Examples: `claude-3-5-sonnet-20241022`, `gemini/gemini-1.5-pro`, `ollama/llama2`
4. Requires corresponding API key in environment

### Adding Validation Checks
1. Add method to `ContinuityValidator` class
2. Call from `validate()` orchestrator
3. Return check results
4. Document validation logic

## Future Roadmap

### Near Term
- [ ] Response caching (Redis) for identical inputs
- [ ] Prompt optimization pipeline
- [ ] Cost reduction strategies
- [ ] Web UI for interactive analysis

### Medium Term
- [ ] PostgreSQL integration for analysis history
- [ ] Analytics dashboard with trends
- [ ] Parallel stage generation (async)
- [ ] Webhook callbacks for long-running analyses

### Long Term
- [ ] Kubernetes deployment
- [ ] Horizontal scaling infrastructure
- [ ] Request queuing and job workers
- [ ] Custom validation rules engine
- [ ] API client libraries (Python, JS, Go)

## Related Documentation

- [API Reference](API.md) - Endpoint documentation with examples
- [Development Guide](DEVELOPMENT.md) - Local setup and testing
- [Deployment Guide](DEPLOYMENT.md) - Production deployment
- [Operational Runbook](RUNBOOK.md) - Day-to-day operations
- [Security Guide](../SECURITY.md) - Security best practices
- [Contributing Guide](../CONTRIBUTING.md) - Development workflow
- [Support Guide](../SUPPORT.md) - FAQ and troubleshooting
- [Architecture Decisions](adr/) - Design decisions
  - [ADR-0001: Record Architecture Decisions](adr/0001-record-architecture-decisions.md)
  - [ADR-0002: Continuity Validation Design](adr/0002-continuity-validation-design.md)

---

Last updated: October 2025
Accurate as of: AI Engine v1.0.0
Phases Complete: 1, 2, 3 (Artifact Extraction, Tracking, Validation)
