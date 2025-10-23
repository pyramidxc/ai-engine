# Security Policy

## Reporting Security Vulnerabilities

**Please do NOT open public GitHub issues for security vulnerabilities.**

Instead, please report security issues via email to **security@pyramidxc.com** with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge receipt within 48 hours and provide status updates as we investigate.

## Security Best Practices

### API Key Management

**NEVER commit API keys to version control.**

```bash
# ✅ DO: Use environment variables
export OPENAI_API_KEY="sk-..."
python3 -m uvicorn app.main:app

# ❌ DON'T: Hardcode keys in code
OPENAI_API_KEY = "sk-..."  # BAD!
```

### Environment Setup

1. Create `.env` file (never commit):
   ```bash
   cp .env.example .env
   # Edit .env with your actual keys
   ```

2. Use `.env.example` for template:
   ```
   OPENAI_API_KEY=sk-your-key-here
   LLM_MODEL=gpt-4o-mini
   DEBUG=false
   ```

3. Add to `.gitignore`:
   ```
   .env
   .env.local
   *.key
   *.pem
   ```

### Input Validation

All inputs are validated using Pydantic models:

```python
from app.models.host import InputHost

# ✅ Validated automatically
host = InputHost(
    platform="Windows",
    version_os="Windows 7",
    open_ports=[139, 445],
    services=["SMB"],
    vulnerabilities=["MS17-010"]
)
```

Invalid inputs will be rejected with clear error messages.

### Rate Limiting

The API includes built-in rate limiting to prevent abuse:

```python
# Default: 100 requests per hour per IP
# Configure in config.py or via RATE_LIMIT_PER_HOUR
```

### Error Handling

Error responses do not expose:
- Internal stack traces
- Database connection details
- API key information
- System paths or configuration

```json
{
  "detail": "Invalid input: platform must be Windows or Linux",
  "status_code": 422
}
```

### Database Security

- No sensitive data stored in logs
- Token usage logged separately
- Request IDs used for audit trails
- All data encrypted in transit (HTTPS)

### TLS/SSL Requirements

**Production deployment MUST use HTTPS:**

```bash
# ✅ DO: Use HTTPS in production
https://api.example.com/attack-path/main

# ❌ DON'T: Use HTTP in production
http://api.example.com/attack-path/main
```

### Dependency Security

Regular security updates for dependencies:

```bash
# Check for vulnerabilities
pip install safety
safety check

# Update dependencies
pip install --upgrade -r requirements.txt
```

### Authentication & Authorization

Current implementation:
- **Status**: No authentication required (internal use)
- **Future**: Consider JWT tokens for production deployment
- **Recommendation**: Use API Gateway with authentication

### Logging & Monitoring

Log sensitive data minimally:

```python
# ✅ DO: Log safely
logger.info(f"Request ID: {request_id} completed")

# ❌ DON'T: Log sensitive data
logger.info(f"API key: {api_key}")  # BAD!
logger.info(f"Response: {full_response}")  # May contain sensitive data
```

### Container Security

When using Docker:

```dockerfile
# ✅ DO: Use non-root user
USER appuser

# ✅ DO: Scan image for vulnerabilities
docker scan ai-engine:latest

# ❌ DON'T: Run as root
USER root  # BAD!
```

### Compliance & Standards

- **OWASP Top 10**: Follow best practices
- **PCI DSS**: If handling payment data
- **GDPR**: If handling personal data
- **SOC 2**: For enterprise deployments

### Security Testing

```bash
# Run security checks
# Add to CI/CD pipeline:
# - bandit (code security)
# - safety (dependency vulnerabilities)
# - pytest (functionality)
```

### Incident Response

If a security vulnerability is discovered:

1. **Acknowledge** - Respond within 48 hours
2. **Assess** - Evaluate severity and impact
3. **Fix** - Develop and test patch
4. **Patch** - Release security update
5. **Disclose** - Notify users (if necessary)

### Version Support

| Version | Status | Security Updates Until |
|---------|--------|------------------------|
| 1.0.x   | Current | 2026-10-22 |
| 0.9.x   | EOL | 2025-12-22 |

### Support Tiers

- **Critical**: Fixes within 24 hours
- **High**: Fixes within 1 week
- **Medium**: Fixes within 2 weeks
- **Low**: Fixes in next release

### Third-Party Dependencies

Key dependencies and security status:

| Package | Version | Status | Notes |
|---------|---------|--------|-------|
| FastAPI | 0.100+ | ✅ Secure | Regularly updated |
| Pydantic | 2.0+ | ✅ Secure | Type validation |
| Python | 3.10+ | ✅ Secure | Long-term support |
| OpenAI | Latest | ✅ Secure | Official SDK |

### Responsible Disclosure

We appreciate the security research community and follow responsible disclosure:

1. **Private Report** - Email security details privately
2. **Response** - We commit to responding within 48 hours
3. **Fix** - We work on fix in coordination with reporter
4. **Release** - We release patch and public advisory
5. **Credit** - With permission, we credit the researcher

### Security Checklist

Before deployment:

- [ ] API keys stored in environment variables, not in code
- [ ] TLS/SSL certificates installed and valid
- [ ] Input validation enabled for all endpoints
- [ ] Rate limiting configured
- [ ] Logging doesn't expose sensitive data
- [ ] Dependencies updated and scanned for vulnerabilities
- [ ] Error messages don't leak system information
- [ ] Database credentials secured
- [ ] Backups encrypted and tested
- [ ] Access controls implemented

### Additional Resources

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)

---

**Last Updated**: October 22, 2025 | **Status**: Active | **Contact**: security@pyramidxc.com
