# Attack Path Engine - Usage Guide

## Overview

The Attack Path Engine is a FastAPI microservice that analyzes host exposure data and generates potential attack paths using LLM (Large Language Model) analysis. It uses LiteLLM to support multiple AI providers without code changes.

## Features

- **Multi-Provider LLM Support**: Use OpenAI, Anthropic, Google Gemini, Azure, and more
- **Attack Path Generation**: AI-powered analysis of potential security vulnerabilities
- **Risk Assessment**: Automatic risk level classification
- **Security Recommendations**: Actionable mitigation strategies
- **JSON API**: Easy integration with other security tools

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

**POST** `/attack-path`

Analyze a host and generate potential attack paths.

**Request Body:**

```json
{
  "hostname": "web-server-01.example.com",
  "open_ports": [22, 80, 443, 3306],
  "vulnerabilities": [
    "CVE-2023-12345: SQL Injection in web application",
    "CVE-2023-23456: Outdated SSH version",
    "CVE-2023-34567: MySQL with default credentials"
  ]
}
```

**Response:**

```json
{
  "hostname": "web-server-01.example.com",
  "attack_path": [
    "1. Scan open ports and identify MySQL on port 3306",
    "2. Attempt default credential login to MySQL database",
    "3. Extract sensitive data and database credentials",
    "4. Use extracted credentials to access web application",
    "5. Exploit SQL injection vulnerability to gain admin access",
    "6. Upload web shell through compromised admin panel",
    "7. Escalate privileges using local exploits",
    "8. Establish persistent SSH access on port 22"
  ],
  "risk_level": "Critical",
  "recommendations": [
    "Immediately change MySQL default credentials and disable remote access",
    "Update SSH to latest version and implement key-based authentication only",
    "Patch SQL injection vulnerability in web application",
    "Implement Web Application Firewall (WAF) to protect against injection attacks",
    "Close unnecessary ports - MySQL should not be exposed to internet",
    "Enable database query logging and monitoring for suspicious activity",
    "Implement multi-factor authentication for administrative access",
    "Conduct regular security audits and penetration testing"
  ]
}
```

## Usage Examples

### Using cURL

```bash
# Test health endpoint
curl http://localhost:8000/health

# Analyze a host
curl -X POST http://localhost:8000/attack-path \
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

# Analyze a host
host_data = {
    "hostname": "db-server-02.internal",
    "open_ports": [22, 5432],
    "vulnerabilities": [
        "CVE-2023-45678: PostgreSQL privilege escalation"
    ]
}

response = client.post("/attack-path", json=host_data)
result = response.json()

print(f"Risk Level: {result['risk_level']}")
print(f"\nAttack Path:")
for step in result['attack_path']:
    print(f"  - {step}")

print(f"\nRecommendations:")
for rec in result['recommendations']:
    print(f"  - {rec}")
```

### Using JavaScript/TypeScript

```javascript
const response = await fetch('http://localhost:8000/attack-path', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    hostname: 'api-server.example.com',
    open_ports: [443, 8080],
    vulnerabilities: [
      'CVE-2023-99999: Unpatched API gateway'
    ]
  })
});

const result = await response.json();
console.log(result);
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
3. **Caching**: Cache results for identical requests to save costs
4. **Model Selection**: Use `gpt-4o-mini` for cost-effective analysis, `gpt-4o` or `claude-3-5-sonnet` for more detailed analysis
5. **Temperature**: Lower temperature (0.3-0.5) for consistent results, higher (0.7-1.0) for creative analysis
6. **Monitoring**: Log all requests and responses for audit trails

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
