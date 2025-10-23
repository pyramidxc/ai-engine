# API Reference

Complete documentation of AI Engine endpoints, request/response formats, and error handling.

## Base URL

```
http://localhost:8000
```

Production deployments may use different hosts/ports. See [DEPLOYMENT.md](DEPLOYMENT.md).

## Authentication

Currently, no authentication is required. Security recommendations:
- Deploy behind API gateway with authentication
- Use rate limiting per client
- Implement API keys for production
- See [SECURITY.md](../SECURITY.md) for details

## Endpoints

### POST /attack-path/main

Generate complete 7-stage attack path analysis.

**Description**:
Generates a complete 7-stage attack path analysis with context threading and continuity validation. This is the PRIMARY endpoint for the AI Engine.

**Request**:

```http
POST /attack-path/main HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "platform": "Windows",
  "version_os": "Server 2019",
  "open_ports": [139, 445],
  "services": ["SMB", "NetBIOS"],
  "vulnerabilities": ["MS17-010"],
  "vulnerability_score": 9.8
}
```

**Request Schema** (InputHost model - all fields optional):

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `platform` | string | No | OS type | "Windows", "Linux", "macOS" |
| `version_os` | string | No | OS version | "Server 2019", "Ubuntu 20.04" |
| `open_ports` | array | No | List of open ports | [22, 80, 443, 3306] |
| `services` | array | No | Running services | ["SSH", "Apache", "MySQL"] |
| `vulnerabilities` | array | No | Known CVEs | ["MS17-010", "CVE-2021-44228"] |
| `vulnerability_score` | number | No | CVSS score (0-10) | 9.8 |
| + 40+ more fields | various | No | Complete InputHost model details | See ARCHITECTURE.md |

**Request Limits**:
- All fields optional, fully flexible input from any scanner/CMDB
- Max request size: Limited by OpenAI token limits (~128k total)
- Timeout: 60 seconds per request
- Concurrent requests: Limited by LLM provider rate limits

**Response**:

```http
HTTP/1.1 200 OK
Content-Type: application/json

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
      "commands": ["nmap -sV 10.0.1.50"],
      "content": "## Reconnaissance\nFull markdown content here..."
    }
  ],
  "total_paths": 1,
  "execution_time_seconds": 22.4,
  "llm_calls": {"total": 7},
  "estimated_cost": 0.051,
  "validation_report": {
    "is_valid": true,
    "total_checks": 4,
    "passes": [
      {"check": "artifact_continuity", "result": "PASS"},
      {"check": "vulnerability_continuity", "result": "PASS"},
      {"check": "technique_alignment", "result": "PASS"},
      {"check": "tool_consistency", "result": "PASS"}
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

**Response Schema**:

```typescript
{
  request_id: string,
  primary_path: StageAnalysis[],
  total_paths: number,
  execution_time_seconds: number,
  llm_calls: { total: number },
  estimated_cost: number,
  validation_report: ValidationReport
}
```

**StageAnalysis** (one per stage 1-7):

| Field | Type | Description |
|-------|------|-------------|
| `stage_index` | integer | Stage number (1-7) |
| `stage_name` | string | Stage name (Reconnaissance, Weaponization, etc.) |
| `phase` | string | Phase description |
| `mitre_techniques` | string[] | MITRE ATT&CK technique IDs |
| `summary` | string | Stage summary |
| `key_findings` | string[] | Key findings for this stage |
| `tools_used` | string[] | Tools identified for this stage |
| `artifact_name` | string \| null | Artifact (file, script, etc.) if applicable |
| `commands` | string[] | Example commands for this stage |
| `content` | string | Full markdown narrative for this stage |

**ValidationReport**:

| Field | Type | Description |
|-------|------|-------------|
| `is_valid` | boolean | Overall validation result (true = all checks passed) |
| `total_checks` | integer | Number of checks performed (always 4) |
| `passes` | array | Checks that passed |
| `warnings` | array | Issues or warnings detected |
| `stage_artifacts` | object | Artifact tracking by stage |

**Success Response Codes**:
- `200 OK` - Analysis successful, returned in response body

**Typical Response Time**: 15-25 seconds (average: ~20s)

**Cost**: ~$0.015-$0.050 per request (GPT-4o-mini rates)

**Example cURL Request**:

```bash
curl -X POST "http://localhost:8000/attack-path/main" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "Windows",
    "version_os": "Server 2019",
    "open_ports": [139, 445],
    "vulnerabilities": ["MS17-010"]
  }' \
  --max-time 60
```

**Example Python Request**:

```python
import requests
import json

url = "http://localhost:8000/attack-path/main"
payload = {
    "platform": "Windows",
    "version_os": "Server 2019",
    "open_ports": [139, 445],
    "services": ["SMB"],
    "vulnerabilities": ["MS17-010"]
}

response = requests.post(url, json=payload, timeout=60)
result = response.json()

print(f"Request ID: {result['request_id']}")
print(f"Execution time: {result['execution_time_seconds']}s")
print(f"Cost: ${result['estimated_cost']}")
print(f"Valid: {result['validation_report']['is_valid']}")

for stage in result['primary_path']:
    print(f"\nStage {stage['stage_index']}: {stage['stage_name']}")
    print(f"Artifact: {stage['artifact_name']}")
```

### GET /health

Health check endpoint for monitoring and service discovery.

**Description**:
Returns service status, version, and configured LLM model. Used by Docker health checks, Kubernetes probes, load balancers, and monitoring systems.

**Request**:

```http
GET /health HTTP/1.1
Host: localhost:8000
```

**Response**:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "ok",
  "version": "1.0.0",
  "model": "gpt-4o-mini"
}
```

**Response Schema**:

```typescript
{
  status: "ok",
  version: string,
  model: string
}
```

**Response Codes**:
- `200 OK` - Service is operational
- `503 Service Unavailable` - Service not operational

**Usage**:

```bash
# Docker health check
curl http://localhost:8000/health

# Kubernetes liveness probe
curl http://kubernetes-pod:8000/health

# Load balancer check
curl http://api.example.com/health
```

## Error Handling

### Error Response Format

All errors return appropriate HTTP status codes with error details:

```json
{
  "detail": "Description of what went wrong"
}
```

### Common Error Scenarios

#### 400 Bad Request

Invalid request format, validation error, or missing required field.

```json
{
  "detail": "Invalid input: vulnerability_score must be 0-10"
}
```

**Common causes**:
- Invalid input data type
- Out-of-range numeric values
- Missing required relationships between fields

**Resolution**:
- Check field types match schema
- Verify value ranges and constraints
- Review ARCHITECTURE.md for InputHost field requirements

#### 422 Unprocessable Entity

Pydantic validation failed on request body.

```json
{
  "detail": [
    {
      "loc": ["body", "platform"],
      "msg": "str type expected",
      "type": "type_error.str"
    }
  ]
}
```

**Common causes**:
- Wrong data type (e.g., string instead of array)
- Invalid enum value
- Malformed JSON

**Resolution**:
- Validate JSON syntax
- Check field types against schema
- Use correct data types for arrays, numbers, strings

#### 500 Internal Server Error

Unexpected server error, usually LLM-related.

```json
{
  "detail": "An unexpected error occurred"
}
```

**Common causes**:
- OpenAI API error
- LLM provider unavailable
- Rate limit exceeded
- Malformed prompt generation (internal error)

**Resolution**:
- Check OpenAI API status
- Review server logs for detailed error
- Retry with exponential backoff
- Contact support if persistent

#### 503 Service Unavailable

Service not operational or degraded.

```json
{
  "detail": "Service temporarily unavailable"
}
```

**Common causes**:
- Service shutting down
- Configuration invalid
- API key not found or invalid

**Resolution**:
- Verify service is running
- Check API key configuration
- Review deployment status

## Rate Limiting & Quotas

### Default Limits

- **Requests/minute**: No built-in limit (configure at reverse proxy)
- **Tokens/minute**: Limited by LLM provider (e.g., OpenAI tier)
- **Concurrent requests**: Limited by I/O (typically 3-5 per instance)

### OpenAI Quotas

Varies by account tier:
- **Free tier**: 3 requests/minute
- **Paid tier**: 100,000 tokens/minute
- **Pro tier**: Higher limits

Monitor usage at: https://platform.openai.com/account/usage/overview

### Handling Rate Limits

If you receive `503` or see LLM errors:

1. Implement exponential backoff (wait 1s, 2s, 4s, 8s...)
2. Batch requests during off-peak hours
3. Upgrade LLM provider tier for higher limits
4. Implement request queuing in production

## Testing

### Quick Start

```bash
# Health check
curl http://localhost:8000/health

# Full analysis with example file
curl -X POST "http://localhost:8000/attack-path/main" \
  -H "Content-Type: application/json" \
  -d @examples/requests/linux_web_server_enhanced.json | python3 -m json.tool
```

### Example Requests

Pre-built example requests in `examples/requests/`:
- `linux_web_server_enhanced.json` - Linux web server scenario
- `windows_7_ms17_010_minimal.json` - Windows 7 with MS17-010

### Manual Testing Examples

#### Example 1: Recommended Request (Best Quality)

Include as many context fields as possible for comprehensive analysis:

```bash
curl -X POST "http://localhost:8000/attack-path/main" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "Windows",
    "version_os": "Windows 7",
    "open_ports": [139, 445],
    "services": ["SMB"],
    "vulnerabilities": ["MS17-010"],
    "vulnerability_score": 9.8
  }' | python3 -m json.tool
```

**Result**: All 6 validation checks pass, complete artifact continuity

#### Example 2: Minimal Request (Works but Less Detail)

Absolute minimum required fields:

```bash
curl -X POST "http://localhost:8000/attack-path/main" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "Windows",
    "version_os": "Server 2019",
    "open_ports": [139, 445],
    "vulnerabilities": ["MS17-010"]
  }' | python3 -m json.tool
```

**Result**: Basic analysis works, but validation checks may be limited

#### Example 3: Python Client

```python
import requests
import json
import time

url = "http://localhost:8000/attack-path/main"

# Recommended: Include services field for best quality
payload = {
    "platform": "Linux",
    "version_os": "Ubuntu 20.04",
    "open_ports": [22, 80, 443],
    "services": ["SSH", "Apache", "OpenSSL"],
    "vulnerabilities": ["CVE-2021-41773"],
    "vulnerability_score": 8.5
}

start = time.time()
response = requests.post(url, json=payload, timeout=60)
end = time.time()

if response.status_code == 200:
    result = response.json()
    print(f"✅ Success in {end - start:.1f}s")
    print(f"Request ID: {result['request_id']}")
    print(f"Stages: {result['total_paths']} path(s) with {len(result['primary_path'])} stages")
    print(f"Cost: ${result['estimated_cost']:.4f}")
    print(f"Valid: {result['validation_report']['is_valid']} ({result['validation_report']['total_checks']} checks)")
    
    # Display first stage
    stage = result['primary_path'][0]
    print(f"\nStage 1: {stage['stage_name']}")
    print(f"Techniques: {', '.join(stage['mitre_techniques'])}")
    print(f"Summary: {stage['summary']}")
else:
    print(f"❌ Error {response.status_code}: {response.text}")
```

### Input Quality Impact

**⚠️ Important**: Including optional fields dramatically improves analysis quality:

| Aspect | Without `services` | With `services` |
|--------|-------------------|------------------|
| Validation Checks | 3-4 pass | All 6 pass |
| Artifact Continuity | Partial (stages 2-5) | Complete (all stages) |
| Stage Content | Basic | Rich, detailed |
| Continuity Validation | Weaker | Full validation |
| Execution Time | 15-18s | 18-25s |
| Cost | $0.015-0.025 | $0.025-0.050 |

### Recommended Input Fields

**Critical fields** (affects attack path selection):

- `platform` - Target OS type
- `version_os` - Specific OS version
- `vulnerabilities` - Known CVEs/weaknesses
- `open_ports` - Exposed network services

**Important fields** (affects analysis depth & artifact tracking):

- `services` - **Highly recommended for best quality**
- `vulnerability_score` - CVSS severity
- `security_controls` - Defensive measures

**Optional fields** (enhances evasion techniques):

- `edr_agent` - EDR/XDR products deployed
- `antivirus_status` - AV/antimware status
- `host_based_firewall` - Local firewall rules
- `network_segmentation` - Network isolation level

**Best Practice**:

```json
{
  "platform": "Windows",
  "version_os": "Server 2019",
  "open_ports": [80, 443, 3306],
  "services": ["Apache", "MySQL"],
  "vulnerabilities": ["CVE-2021-44228"],
  "vulnerability_score": 9.0,
  "security_controls": ["WAF"],
  "edr_agent": "CrowdStrike"
}
```

### Common Issues & Solutions

#### Getting 422 Unprocessable Entity

```json
{"detail": [{"loc": ["body", "platform"], "msg": "str type expected"}]}
```

**Causes**:

- Invalid JSON syntax (check brackets, quotes, commas)
- Wrong data type (e.g., string instead of array)
- Malformed request body

**Solution**:

```bash
# Validate JSON before sending
echo '{"platform": "Windows"}' | python3 -m json.tool

# Use proper curl escaping
curl -X POST "http://localhost:8000/attack-path/main" \
  -H "Content-Type: application/json" \
  -d '{"platform": "Windows", "open_ports": [22, 80]}'
```

#### Getting 500 Internal Server Error

**Causes**:

- OpenAI API error or rate limit
- Invalid API key
- LLM provider unavailable

**Solution**:

```bash
# Check API key
echo $OPENAI_API_KEY  # Should show sk-...

# Check OpenAI status: https://status.openai.com/

# Retry with exponential backoff
for i in 1 2 4 8; do
  curl -X POST "http://localhost:8000/attack-path/main" \
    -H "Content-Type: application/json" \
    -d @examples/requests/windows_7_ms17_010_minimal.json && break
  echo "Retry in ${i}s..."
  sleep $i
done
```

#### Requests Timing Out

**Causes**:

- Analysis taking longer than expected (30-40s for complex scenarios)
- LLM provider slow response
- Network connectivity issues

**Solution**:

```bash
# Increase timeout (default 60s)
curl --max-time 120 -X POST "http://localhost:8000/attack-path/main" \
  -H "Content-Type: application/json" \
  -d @examples/requests/linux_web_server_enhanced.json

# In Python
response = requests.post(url, json=payload, timeout=120)
```

#### Analysis Quality is Poor

**Cause**: Insufficient input context

**Solution**: Include `services` and other optional fields:
```bash
# ❌ Poor: Missing services
curl -X POST "http://localhost:8000/attack-path/main" \
  -d '{"platform": "Windows", "vulnerabilities": ["MS17-010"]}'

# ✅ Better: Include services
curl -X POST "http://localhost:8000/attack-path/main" \
  -d '{"platform": "Windows", "vulnerabilities": ["MS17-010"], "services": ["SMB"]}'
```

See **Input Quality Impact** table above for details.

## API Versioning

### Current Version

- **Version**: 1.0.0
- **Release Date**: October 2025
- **Status**: Stable (production ready)

### Backward Compatibility

- All v1.x releases are backward compatible
- No breaking changes planned for v1.x
- Additions will be additive (new optional fields)

### Future Versions

- **v2.0**: Planned improvements (breaking changes announced 6 months ahead)
- **v1.1+**: New features (backward compatible)

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design and InputHost model details
- [DEVELOPMENT.md](DEVELOPMENT.md) - Local setup and testing
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
- [RUNBOOK.md](RUNBOOK.md) - Operational procedures
- [SECURITY.md](../SECURITY.md) - Security best practices

---

Last updated: October 2025
Accurate as of: AI Engine v1.0.0
