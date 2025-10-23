# Support

Welcome! We're here to help you get the most out of the AI Engine. This guide covers common questions, troubleshooting, and how to get support.

## Getting Help

### Before You Ask
1. **Check the documentation**
   - [README.md](README.md) - Quick start and overview
   - [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design
   - [docs/API.md](docs/API.md) - API reference
   - [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) - Development setup

2. **Search existing issues**
   - Browse [GitHub Issues](https://github.com/pyramidxc/ai-engine/issues)
   - Look for similar problems with solutions
   - Check closed issues for historical context

3. **Review CHANGELOG**
   - [CHANGELOG.md](CHANGELOG.md) - Recent changes and fixes
   - Check if your issue was addressed in latest version

### How to Get Help

**For Questions**
- Create a [Discussion](https://github.com/pyramidxc/ai-engine/discussions)
- Tag with appropriate category (Q&A, Ideas, etc.)
- Include details about your setup and what you're trying to do

**For Bug Reports**
- Create an [Issue](https://github.com/pyramidxc/ai-engine/issues)
- Use the bug report template
- Provide reproduction steps and environment details

**For Security Issues**
- Email: security@pyramidxc.com
- Do NOT create public GitHub issue
- Include severity and affected versions
- See [SECURITY.md](SECURITY.md) for details

**For Other Inquiries**
- Email: support@pyramidxc.com
- Include your question and any relevant context
- Response time: 1-2 business days

## Frequently Asked Questions

### Installation & Setup

**Q: Python version requirements?**
A: Python 3.10 or higher. We recommend 3.11+ for best performance.

**Q: How do I install the project?**
A: See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for detailed setup instructions:
```bash
git clone https://github.com/pyramidxc/ai-engine.git
cd ai-engine
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Q: How do I configure the OpenAI API key?**
A: Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```
Never commit `.env` to version control. See [SECURITY.md](SECURITY.md) for details.

**Q: Can I use different LLM providers?**
A: Currently, OpenAI is the primary provider. For other providers, see the [CONTRIBUTING.md](CONTRIBUTING.md) guide for feature requests.

### API Usage

**Q: What endpoints are available?**
A: See [docs/API.md](docs/API.md) for complete API reference with examples.

**Q: How do I make a request?**
A: Use POST to `/analyze` with a request JSON:
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d @examples/requests/linux_web_server_enhanced.json
```

**Q: How long does analysis take?**
A: Typically 10-20 seconds depending on complexity. LLM processing accounts for ~80% of time.

**Q: Why is my analysis taking longer?**
A: Possible causes:
- High OpenAI API latency
- Large input requiring more tokens
- LLM rate limiting (slow down requests)
- Network issues
- Check logs: `tail -f logs/token_usage.jsonl`

**Q: Can I customize the analysis stages?**
A: Yes, modify prompts in `app/core/prompts.py` and stage logic in `app/services/complete_analyzer.py`.

**Q: What's the maximum input size?**
A: Current limit is determined by OpenAI token limits (~128k tokens). Individual requests should stay under 50k tokens.

### Context Threading & Validation

**Q: What is context threading?**
A: Each of 7 stages receives outputs from previous stages, maintaining logical continuity. The `AttackContext` object threads through the entire analysis.

**Q: What is continuity validation?**
A: Phase 3 enhancement validates cross-stage consistency:
- Artifact continuity (same files referenced across stages)
- Vulnerability continuity (CVE flows logically)
- Technique alignment (MITRE ATT&CK alignment)
- Tool consistency (compatible tool usage)

**Q: What should `is_valid: true` mean?**
A: All validation checks passed, indicating high-quality analysis with strong logical continuity.

**Q: Why is `is_valid: false`?**
A: One or more validation checks failed. See `validation_report` field for details on what needs investigation.

### Performance & Optimization

**Q: How can I improve performance?**
A:
1. Use GPT-4o-mini (faster than GPT-4)
2. Reduce input complexity
3. Batch requests efficiently
4. Enable caching (if using Docker)
5. See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for production optimization

**Q: Can I run locally without Docker?**
A: Yes, follow [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md). Docker is recommended for production.

**Q: What are token usage patterns?**
A: Check `logs/token_usage.jsonl` for per-request metrics. Monitor to catch unexpected increases.

### Artifact Extraction

**Q: How does artifact extraction work?**
A: 4-priority fallback strategy:
1. **Priority 1**: Code blocks (msfvenom, curl, wget, PowerShell)
2. **Priority 2**: Explicit naming (named:, created:, called:)
3. **Priority 3**: Upload/transfer (upload, scp, copy)
4. **Priority 4**: Prior stage references

**Q: Why is my artifact not detected?**
A: Check if it matches one of the 4 priority patterns. Extend patterns in `complete_analyzer.py` if needed. See [CONTRIBUTING.md](CONTRIBUTING.md) for modification guidelines.

**Q: How are artifacts tracked?**
A: `stage_artifacts` dict in `AttackContext` maps each stage (1-7) to artifact name. Auto-populated during response parsing.

## Troubleshooting

### Common Issues

#### "OPENAI_API_KEY not found"
**Problem**: Missing or invalid API key configuration

**Solution**:
1. Create `.env` file: `cp .env.example .env`
2. Add your key: `OPENAI_API_KEY=sk-...`
3. Restart application
4. Verify: `echo $OPENAI_API_KEY`

#### "Connection refused"
**Problem**: Service not running or wrong URL

**Solution**:
1. Verify service is running: `ps aux | grep python`
2. Check port: `lsof -i :8000`
3. Try different port: `python -m app.main --port 8001`
4. Check firewall: `sudo ufw status`

#### "Request timeout"
**Problem**: Analysis taking too long

**Solution**:
1. Check OpenAI status: https://status.openai.com
2. Reduce input complexity
3. Increase timeout in `app/config.py`
4. Check logs: `tail -f logs/*.log`

#### "Token limit exceeded"
**Problem**: Input too large for model

**Solution**:
1. Reduce input size
2. Use more concise descriptions
3. Split into multiple requests
4. Monitor `logs/token_usage.jsonl`

#### "Validation failed: is_valid = false"
**Problem**: Analysis has continuity issues

**Solution**:
1. Check `validation_report` for specific failures
2. Review stage_artifacts for missing items
3. Try simpler input scenario
4. Create issue with reproduction case

#### "Module not found"
**Problem**: Missing dependencies

**Solution**:
1. Verify virtual environment activated: `which python`
2. Reinstall requirements: `pip install -r requirements.txt`
3. Check for conflicts: `pip check`
4. Update pip: `pip install --upgrade pip`

### Debug Mode

Enable debug logging:

```python
# In app/config.py
DEBUG = True
LOG_LEVEL = "DEBUG"
```

Or set environment variable:
```bash
export LOG_LEVEL=DEBUG
python -m app.main
```

### Getting Debug Information

**Collect logs for bug report**:
```bash
# Application logs
tail -100 logs/*.log > debug.log

# Token usage
cat logs/token_usage.jsonl > tokens.json

# System info
echo "=== Python ===" >> debug.log
python --version >> debug.log
pip freeze >> debug.log

# Create issue with these files attached
```

## Known Limitations

- **Model variations**: Responses vary based on OpenAI model updates
- **Artifact extraction**: Cannot detect artifacts in very unusual formats
- **Context limit**: Stage outputs truncated if exceeding token limits
- **Real-time updates**: Analysis reflects training data at model release time
- **Rate limits**: OpenAI applies account-based rate limiting

## Contributing Help

Found a bug? Want to improve documentation? See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Creating quality issue reports
- Writing documentation improvements
- Submitting code fixes
- Development workflow

## Reporting Issues

When reporting issues, please include:

```markdown
## Environment
- Python version: 3.11
- OS: Ubuntu 22.04
- AI Engine version: 1.0.0

## Expected behavior
Description of what should happen

## Actual behavior
Description of what actually happened

## Steps to reproduce
1. ...
2. ...
3. ...

## Relevant logs
```<logs>```
...
```

## Additional context
Any other relevant information
```

## Feature Requests

Want a new feature? Create a [Discussion](https://github.com/pyramidxc/ai-engine/discussions) with:
- Clear description of desired feature
- Use cases or examples
- Proposed implementation (if you have ideas)
- Willingness to contribute (optional)

## Response Times

- **Security issues**: 24-48 hours
- **Critical bugs**: 24-72 hours
- **Bug reports**: 3-7 days
- **Feature requests**: 1-2 weeks
- **Questions**: Best effort, typically 1-3 days

*Response times are estimates. For urgent matters, email support@pyramidxc.com*

## Community Resources

- **GitHub Discussions**: Ask questions, share ideas
- **GitHub Issues**: Report bugs, request features
- **Documentation**: Detailed guides in `/docs`
- **Examples**: Sample requests/responses in `/examples`
- **Email**: support@pyramidxc.com

## Additional Help

- **Architecture Deep Dive**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **API Documentation**: [docs/API.md](docs/API.md)
- **Development Guide**: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- **Deployment Guide**: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- **Runbook**: [docs/RUNBOOK.md](docs/RUNBOOK.md)
- **Security**: [SECURITY.md](SECURITY.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

Last updated: 2024
Support email: support@pyramidxc.com
