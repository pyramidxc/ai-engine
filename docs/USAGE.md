# Attack Path Engine - Usage Guide

## Overview

The Attack Path Engine is a FastAPI microservice that generates realistic attack paths from host exposure data collected by external systems. It uses AI (via LiteLLM) to transform vulnerability and port scan data into sequential attack scenarios that demonstrate how an attacker would exploit identified weaknesses.

## Features

- **Multi-Provider LLM Support**: Use OpenAI, Anthropic, Google Gemini, Azure, and more
- **Realistic Attack Path Generation**: AI-powered sequences showing attacker progression
- **Risk Assessment**: Automatic risk level classification (Critical, High, Medium, Low)
- **Collector Integration**: Designed to work with external vulnerability scanners and assessment tools
- **JSON API**: Easy integration with security platforms and orchestration systems
- **Phase 2 Ready**: Architecture supports future remediation and compliance features

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Edit the `.env` file with your API keys:

```properties
# For OpenAI (default)
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini

# For Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-3-5-sonnet-20241022

# For Google Gemini
GEMINI_API_KEY=...
LLM_MODEL=gemini/gemini-pro

# For Azure OpenAI
AZURE_API_KEY=...
AZURE_API_BASE=https://your-resource.openai.azure.com
AZURE_API_VERSION=2024-02-15-preview
LLM_MODEL=azure/gpt-4

# Optional settings
LLM_TEMPERATURE=0.7  # 0.0 = deterministic, 2.0 = creative
```

### 3. Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check

**GET** `/health`

Check if the service is running.

**Response:**

```json
{
  "status": "ok"
}
```

### Generate Attack Path

**POST** `/attack-path?include_prompt=true`

Generate a realistic attack path from host exposure data collected by external systems.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_prompt` | boolean | `true` | Include the generated prompt in response for debugging/auditing |

**Request Body (from external collector):**

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
    "CVE-2023-23456: Outdated SSH version with known exploits",
    "CVE-2023-34567: MySQL running with default credentials"
  ]
}
```

**Response (with `include_prompt=true`):**

```json
{
  "platform": "Linux",
  "version_os": "Ubuntu 20.04.3 LTS",
  "attack_path": [
    "Reconnaissance: Active network scanning using nmap (MITRE T1595.002) identifies Linux Ubuntu server with SSH, Apache, and MySQL services exposed",
    "Weaponization: Prepare SQL injection exploit framework targeting Apache/MySQL stack. Tool: sqlmap with custom tamper scripts",
    "Delivery: Direct HTTP POST exploitation to vulnerable /login.php endpoint (MITRE T1190 - Exploit Public-Facing Application)",
    "Exploitation: SQL injection successful - UNION-based attack extracts MySQL credentials. Payload: admin' UNION SELECT user,password FROM mysql.user--",
    "Installation: Deploy persistence mechanism via MySQL UDF backdoor (MITRE T1546). Command: CREATE FUNCTION sys_exec RETURNS int SONAME 'lib_mysqludf_sys.so'",
    "Command and Control: Establish reverse HTTPS shell using Metasploit (MITRE T1071.001). Listener on attacker.com:443 with SSL encryption",
    "Actions on Objectives: Credential dumping from /etc/shadow (T1003.008), lateral movement via SSH keys (T1021.004), database exfiltration (T1048.002)"
  ],
  "risk_level": "Critical",
  "generated_prompt": "Generate a realistic attack path for the following target...\\n\\n=== CORE SYSTEM INFO ===\\n- Platform: Linux\\n- OS Version: Ubuntu 20.04.3 LTS\\n\\n=== NETWORK SERVICES & EXPOSURES ===\\n...[full prompt text]",
  "prompt_sections": 3
}
```

**Response (with `include_prompt=false`):**

```json
{
  "platform": "Linux",
  "version_os": "Ubuntu 20.04.3 LTS",
  "attack_path": [...],
  "risk_level": "Critical",
  "generated_prompt": null,
  "prompt_sections": null
}
```

## Usage Examples

### Using cURL

```bash
# Test health endpoint
curl http://localhost:8000/health

# Analyze a host (with prompt tracking - default)
curl -X POST "http://localhost:8000/attack-path?include_prompt=true" \
  -H "Content-Type: application/json" \
  -d @example_request.json

# Analyze without prompt (smaller response)
curl -X POST "http://localhost:8000/attack-path?include_prompt=false" \
  -H "Content-Type: application/json" \
  -d @example_request.json
```

### Using Python

```python
import httpx

# Create a client
client = httpx.Client(base_url="http://localhost:8000")

# Check health
response = client.get("/health")
print(response.json())

# Generate attack path
host_data = {
    "platform": "Linux",
    "version_os": "Debian 11 (Bullseye)",
    "open_ports": [22, 5432],
    "services": [
        "OpenSSH 8.4p1 on port 22",
        "PostgreSQL 13.7 on port 5432"
    ],
    "vulnerabilities": [
        "CVE-2023-45678: PostgreSQL privilege escalation"
    ]
}

response = client.post("/attack-path", json=host_data)
result = response.json()

print(f"Platform: {result['platform']} {result['version_os']}")
print(f"Risk Level: {result['risk_level']}")
print(f"\nAttack Path:")
for step in result['attack_path']:
    print(f"  • {step}")
```

### Using JavaScript/TypeScript

```javascript
const response = await fetch('http://localhost:8000/attack-path', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    platform: 'Linux',
    version_os: 'CentOS 8',
    open_ports: [443, 8080],
    services: [
      'nginx 1.18.0 on port 443',
      'Tomcat 9.0.54 on port 8080'
    ],
    vulnerabilities: [
      'CVE-2023-99999: Unpatched API gateway vulnerability'
    ]
  })
});

const result = await response.json();
console.log(`Platform: ${result.platform} ${result.version_os}`);
console.log(`Risk: ${result.risk_level}`);
console.log('Attack Path:', result.attack_path);
```

## LiteLLM Provider Support

The engine uses LiteLLM, which supports 100+ LLM providers. Just change the `LLM_MODEL` in your `.env` file:

| Provider | Model Example | Required Env Vars |
|----------|--------------|-------------------|
| OpenAI | `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo` | `OPENAI_API_KEY` |
| Anthropic | `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229` | `ANTHROPIC_API_KEY` |
| Google | `gemini/gemini-pro`, `gemini/gemini-1.5-pro` | `GEMINI_API_KEY` |
| Azure OpenAI | `azure/gpt-4`, `azure/gpt-35-turbo` | `AZURE_API_KEY`, `AZURE_API_BASE`, `AZURE_API_VERSION` |
| AWS Bedrock | `bedrock/anthropic.claude-v2` | AWS credentials |
| Cohere | `command-nightly`, `command` | `COHERE_API_KEY` |
| Hugging Face | `huggingface/model-name` | `HUGGINGFACE_API_KEY` |
| Ollama (local) | `ollama/llama2`, `ollama/mistral` | None (local) |

## API Documentation

Once the server is running, visit:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Successful analysis
- `422 Unprocessable Entity`: Invalid input data
- `500 Internal Server Error`: LLM or processing error

Error response format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Best Practices

1. **API Key Security**: Never commit API keys to version control
2. **Rate Limiting**: Implement rate limiting for production use
3. **Caching**: Cache results for similar vulnerability patterns to save costs
4. **Model Selection**: Use `gpt-4o-mini` for cost-effective generation, `gpt-4o` or `claude-3-5-sonnet` for more sophisticated attack sequences
5. **Temperature**: Lower temperature (0.3-0.5) for consistent attack paths, higher (0.7-1.0) for varied scenarios
6. **Monitoring**: Log all generation requests and responses for audit trails
7. **Collector Integration**: Ensure data format from collectors matches InputHost schema

## Development

### Running Tests

```bash
pytest
```

### Running in Development Mode

```bash
uvicorn app.main:app --reload --log-level debug
```

### Docker Support

```bash
docker build -t attack-path-engine .
docker run -p 8000:8000 --env-file .env attack-path-engine
```

## Troubleshooting

### "Import litellm could not be resolved"

```bash
pip install litellm>=1.40.0
```

### "Failed to parse LLM response"

- Some models may not support `response_format` parameter
- Try removing the `response_format` parameter or using a different model

### "Authentication error"

- Check that your API key is correctly set in `.env`
- Verify the API key is valid and has sufficient credits

### High response times

- LLM calls can take 5-30 seconds depending on the model
- Consider implementing async processing and webhooks for better UX

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions:

- GitHub Issues: [https://github.com/pyramidxc/ai-engine/issues](https://github.com/pyramidxc/ai-engine/issues)
- Email: [Your Email]
