# API Examples

This directory contains canonical examples for the Attack Path Analysis API.

## Structure

```bash
examples/
├── requests/          # Example input payloads for POST /attack-path/main
│   ├── windows_7_ms17_010_minimal.json      # Minimal Windows 7 with MS17-010
│   └── linux_web_server_enhanced.json       # Comprehensive Linux DMZ scenario
└── responses/         # Example output responses from the API
    └── complete_analysis_response.json      # Complete 7-stage analysis response
```

## Quick Start

### Using Minimal Request

Perfect for quick testing:

```bash
curl -X POST "http://localhost:8000/attack-path/main" \
  -H "Content-Type: application/json" \
  -d @examples/requests/windows_7_ms17_010_minimal.json | python3 -m json.tool
```

### Using Enhanced Request

For comprehensive analysis:

```bash
curl -X POST "http://localhost:8000/attack-path/main" \
  -H "Content-Type: application/json" \
  -d @examples/requests/linux_web_server_enhanced.json | python3 -m json.tool
```

### Saving Response to File

```bash
curl -s -X POST "http://localhost:8000/attack-path/main" \
  -H "Content-Type: application/json" \
  -d @examples/requests/windows_7_ms17_010_minimal.json > response.json
```

## Example Files

### Request Examples

#### `windows_7_ms17_010_minimal.json`

- **Scenario**: Windows 7 system vulnerable to EternalBlue
- **Size**: 5 fields (minimal)
- **Purpose**: Quick testing and validation
- **Typical Response Time**: 15-25 seconds
- **Typical Cost**: ~$0.015

```json
{
  "platform": "Windows",
  "version_os": "Windows 7",
  "open_ports": [139, 445],
  "services": ["SMB"],
  "vulnerabilities": ["MS17-010"]
}
```

#### `linux_web_server_enhanced.json`

- **Scenario**: Ubuntu 20.04 web server in DMZ with multiple vulnerabilities
- **Size**: 20+ fields (detailed)
- **Purpose**: Production-like analysis
- **Typical Response Time**: 15-25 seconds
- **Typical Cost**: ~$0.015

Key fields included:

- Asset information (name, FQDN, IP)
- Network configuration (segment, internet exposure)
- Services and vulnerabilities
- Security controls status
- User accounts and authentication
- Database exposure

### Response Example

#### `complete_analysis_response.json`

- **Type**: `CompleteAnalysisResponse`
- **Contains**: 7-stage attack path with structured data
- **Size**: ~15KB
- **Structure**:
  - `request_id`: Unique identifier
  - `primary_path`: Array of 7 `StageAnalysis` objects
  - `total_paths`: Always 1
  - `execution_time_seconds`: Actual execution time
  - `llm_calls`: Breakdown of LLM calls
  - `estimated_cost`: Cost in USD

#### Response Structure Per Stage

Each stage in `primary_path` contains:

```json
{
  "stage_index": 1,
  "stage_name": "Reconnaissance",
  "phase": "Information Gathering",
  "mitre_techniques": ["T1595", "T1592", "T1598"],
  "summary": "One-line summary of stage activity",
  "key_findings": ["Finding 1", "Finding 2", ...],
  "tools_used": ["nmap", "shodan"],
  "artifact_name": "payload_name_if_applicable.exe",
  "artifact_type": "Windows PE Executable",
  "commands": ["command1", "command2"],
  "content": "Full detailed narrative content describing the stage..."
}
```

## Response Fields Reference

### Per-Stage Fields (StageAnalysis)

| Field | Type | Description |
|-------|------|-------------|
| `stage_index` | int (1-7) | Position in the kill chain |
| `stage_name` | string | Kill chain stage name |
| `phase` | string | Phase description |
| `mitre_techniques` | string[] | Applicable MITRE ATT&CK IDs |
| `summary` | string | One-line activity summary |
| `key_findings` | string[] | Bulleted findings |
| `tools_used` | string[] | Tools employed |
| `artifact_name` | string\|null | Payload name if deployed |
| `artifact_type` | string\|null | Artifact type/category |
| `commands` | string[] | Commands executed |
| `content` | string | Full narrative description |

### Top-Level Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `request_id` | UUID | Unique analysis identifier |
| `primary_path` | StageAnalysis[] | 7 stages (fixed length) |
| `total_paths` | int | Always 1 |
| `execution_time_seconds` | float | Total execution time |
| `llm_calls` | {total: int} | LLM call breakdown |
| `estimated_cost` | float | Cost in USD |

## Integration Examples

### Python

```python
import requests
import json

# Minimal request
with open("examples/requests/windows_7_ms17_010_minimal.json") as f:
    payload = json.load(f)

response = requests.post(
    "http://localhost:8000/attack-path/main",
    json=payload
)

analysis = response.json()
for stage in analysis["primary_path"]:
    print(f"Stage {stage['stage_index']}: {stage['stage_name']}")
    print(f"  MITRE: {', '.join(stage['mitre_techniques'])}")
    print(f"  Tools: {', '.join(stage['tools_used'])}")
```

### cURL + jq

```bash
# Pretty-print response
curl -s -X POST "http://localhost:8000/attack-path/main" \
  -H "Content-Type: application/json" \
  -d @examples/requests/windows_7_ms17_010_minimal.json | \
  jq '.primary_path[] | {stage: .stage_index, name: .stage_name, techniques: .mitre_techniques}'
```

### Node.js

```javascript
const fs = require('fs');
const payload = JSON.parse(
  fs.readFileSync('examples/requests/windows_7_ms17_010_minimal.json')
);

fetch('http://localhost:8000/attack-path/main', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload)
})
.then(r => r.json())
.then(data => {
  data.primary_path.forEach(stage => {
    console.log(`Stage ${stage.stage_index}: ${stage.stage_name}`);
  });
});
```

## Testing Workflow

1. **Start the service**

   ```bash
   python3 -m uvicorn app.main:app --reload
   ```

2. **Test health endpoint**

   ```bash
   curl http://localhost:8000/health
   ```

3. **Test with minimal request**

   ```bash
   curl -X POST "http://localhost:8000/attack-path/main" \
     -H "Content-Type: application/json" \
     -d @examples/requests/windows_7_ms17_010_minimal.json
   ```

4. **Compare with expected output**
   - Check that response matches structure in `complete_analysis_response.json`
   - Verify all 7 stages are present
   - Check MITRE techniques are populated
   - Verify cost is ~$0.015

## Source of Truth

This directory serves as the **canonical reference** for:

- ✅ Expected request format and fields
- ✅ Expected response structure
- ✅ Data types and field formats
- ✅ Field constraints (min_length, max_length, etc.)
- ✅ Example values and realistic scenarios

When making API changes, these examples should be updated to reflect the new structure.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-22 | Initial examples with 2 request scenarios and 1 response example |

## Related Documentation

- [`docs/03-api-usage/INPUT_PARAMETERS.md`](../docs/03-api-usage/INPUT_PARAMETERS.md) - Complete input field reference
- [`docs/03-api-usage/PROMPT_PIPELINE_SPECIFICATION.md`](../docs/03-api-usage/PROMPT_PIPELINE_SPECIFICATION.md) - How requests are processed
- [`docs/02-architecture/ARCHITECTURE.md`](../docs/02-architecture/ARCHITECTURE.md) - System architecture overview
