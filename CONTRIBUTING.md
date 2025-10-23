# Contributing Guide

Thank you for your interest in contributing to the AI Engine project! This guide outlines the process for contributing code, documentation, and improvements.

## Code of Conduct

By participating in this project, you agree to uphold our [Code of Conduct](CODE_OF_CONDUCT.md). We are committed to providing a welcoming and inclusive environment for all contributors.

## Getting Started

### Prerequisites
- Python 3.10+
- Git
- OpenAI API key for testing
- Familiarity with FastAPI, Pydantic, and async Python

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/pyramidxc/ai-engine.git
cd ai-engine

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Copy example environment
cp .env.example .env
# Edit .env with your OpenAI API key
```

## Development Workflow

### 1. Create Feature Branch

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name
# Or for bug fixes:
git checkout -b bugfix/issue-number
```

Branch naming conventions:
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test improvements

### 2. Make Changes

Follow these guidelines:

#### Code Style

- **PEP 8**: Follow Python Enhancement Proposal 8
- **Black**: Format code with Black (line length: 100)
- **Docstrings**: Use Google-style docstrings

```python
def _extract_artifact_name(self, content: str, stage_index: int) -> Optional[str]:
    """
    Extract artifact names with priority-based fallback.
    
    Multi-strategy extraction: code blocks (most reliable) → explicit naming →
    uploads/transfers → references to prior stage artifacts.
    
    Args:
        content: Stage content to extract from
        stage_index: Which stage (1-7) for context
        
    Returns:
        Artifact name if found, else None
    """
    # Implementation
```

#### Type Hints

Always use type hints:

```python
# ✅ DO
def process_data(data: Dict[str, Any], count: int) -> List[str]:
    pass

# ❌ DON'T
def process_data(data, count):
    pass
```

#### Comments

Write clear, concise comments:

```python
# ✅ DO - Explains why, not what
# Use Priority 1 first because code blocks are most reliable
pattern = re.compile(r"msfvenom.*-o\s+(\S+)")

# ❌ DON'T - Obvious from code
# Find the output file
pattern = re.compile(r"msfvenom.*-o\s+(\S+)")
```

#### Testing

Write tests for new functionality:

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_analyzer.py::test_artifact_extraction
```

Create tests in `tests/` directory:

```python
# tests/test_analyzer.py
import pytest
from app.services.complete_analyzer import CompleteAnalyzer

@pytest.mark.asyncio
async def test_artifact_extraction():
    analyzer = CompleteAnalyzer()
    artifact_name = analyzer._extract_artifact_name(
        'msfvenom -o payload.exe',
        stage_index=2
    )
    assert artifact_name == "payload.exe"
```

### 3. Commit Changes

```bash
# Stage changes
git add .

# Commit with clear message
git commit -m "feat: add artifact extraction priority levels

- Implement 4-priority fallback strategy
- Add support for Windows and Linux artifacts
- Increase detection accuracy to 95%

Fixes #123"
```

Commit message format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Code style
- `refactor` - Code refactoring
- `test` - Tests
- `chore` - Build, CI, dependencies

### 4. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create PR on GitHub
# Use template provided
```

Pull request template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #123

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] No new warnings

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added
- [ ] No breaking changes
```

## Code Review Process

1. **Automated Checks**
   - Tests must pass
   - Code coverage maintained
   - Linting checks pass
   - No security issues

2. **Code Review**
   - Maintainer reviews for functionality
   - Checks adherence to guidelines
   - Tests logic and edge cases
   - Requests changes if needed

3. **Approval**
   - Requires 1+ approval from maintainers
   - All conversations resolved
   - Ready to merge

## Project Structure Guidelines

### Adding New Features

Follow existing patterns:

```python
# app/services/new_feature.py
class NewFeatureService:
    """Service for new feature."""
    
    def __init__(self):
        """Initialize service."""
        pass
    
    async def execute(self, data: InputModel) -> OutputModel:
        """Execute new feature."""
        pass

# app/models/new_models.py
from pydantic import BaseModel

class NewInputModel(BaseModel):
    """Input for new feature."""
    field1: str
    field2: int

class NewOutputModel(BaseModel):
    """Output from new feature."""
    result: str
```

### Adding New Endpoints

```python
# app/main.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/endpoint")
async def new_endpoint(request: RequestModel) -> ResponseModel:
    """New endpoint description."""
    service = NewFeatureService()
    result = await service.execute(request)
    return result
```

### Adding New Tests

```python
# tests/test_new_feature.py
import pytest
from app.services.new_feature import NewFeatureService

@pytest.fixture
def service():
    return NewFeatureService()

@pytest.mark.asyncio
async def test_new_feature_success(service):
    """Test successful execution."""
    input_data = NewInputModel(field1="test", field2=42)
    result = await service.execute(input_data)
    assert result.result == "expected_value"

@pytest.mark.asyncio
async def test_new_feature_error(service):
    """Test error handling."""
    input_data = NewInputModel(field1="", field2=-1)
    with pytest.raises(ValueError):
        await service.execute(input_data)
```

## Documentation Updates

When adding features, update documentation:

1. **README.md** - Update features list if applicable
2. **docs/API.md** - Document new endpoints
3. **docs/ARCHITECTURE.md** - Update if architecture changes
4. **CHANGELOG.md** - Add entry under [Unreleased]

## Performance Considerations

- Keep LLM calls minimal
- Cache expensive operations
- Use async/await for I/O operations
- Profile before optimizing

```python
# ✅ DO - Use async
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()

# ❌ DON'T - Blocking I/O
import requests
def fetch_data():
    return requests.get(url).json()
```

## Security Considerations

- Never hardcode API keys
- Validate all inputs
- Don't expose internal errors
- Log securely
- Use environment variables for config

See [SECURITY.md](SECURITY.md) for detailed guidelines.

## Documentation Style

Use clear, concise language:

```markdown
# Good
This validates that the artifact created in Stage 2 is referenced in Stage 5.

# Bad
This validates stuff across stages.
```

## Release Process

1. Update version in relevant files
2. Update CHANGELOG.md
3. Create release notes
4. Tag release in Git
5. Deploy to production

## Communication

- **Issues** - Use for bugs and features
- **Discussions** - Use for questions
- **PRs** - Use for code changes
- **Email** - security@pyramidxc.com for security issues

## Questions?

- Check [SUPPORT.md](SUPPORT.md) for common questions
- Read [ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design
- Review existing code for patterns

## Attribution

All contributors will be recognized in:
- CHANGELOG.md
- GitHub contributors page
- Release notes

Thank you for contributing! 🎉
