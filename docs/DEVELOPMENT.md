# Development Guide

Guide for setting up a local development environment and contributing code to AI Engine.

## Prerequisites

Before starting, ensure you have:
- Python 3.10 or higher
- Git 2.30+
- pip (Python package manager)
- A code editor (VS Code recommended)
- OpenAI API key (for testing)
- ~2GB disk space

Verify prerequisites:

```bash
python3 --version  # Should be 3.10+
git --version      # Should be 2.30+
pip --version      # Should be pip 21.0+
```

## Initial Setup

### 1. Clone Repository

```bash
git clone https://github.com/pyramidxc/ai-engine.git
cd ai-engine
```

### 2. Create Virtual Environment

Create isolated Python environment:

```bash
# Create venv
python3 -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

You should see `(venv)` prefix in terminal.

### 3. Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install base requirements
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### 4. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env with your OpenAI API key
nano .env
```

Your `.env` should contain:

```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
DEBUG=true
LOG_LEVEL=DEBUG
```

### 5. Verify Installation

```bash
# Run import test
python -c "from app.main import app; print('✓ Imports successful')"

# Run quick start
python -m app.main &
sleep 2

# Test endpoint
curl http://localhost:8000/ready
# Should return: {"ready":true}

# Stop server (if running)
pkill -f "python -m app.main"
```

## Running the Application

### Local Server

```bash
# Start development server
python -m app.main

# With auto-reload
uvicorn app.main:app --reload --port 8000

# With custom port
python -m app.main --port 8001
```

Server runs at: http://localhost:8000

### Docker

```bash
# Build image
docker build -t ai-engine:dev .

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-your-key \
  ai-engine:dev

# Using docker-compose
docker-compose up
```

## Project Structure

```
ai-engine/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── config.py               # Configuration
│   ├── core/
│   │   ├── __init__.py
│   │   └── prompts.py          # LLM prompts
│   ├── models/
│   │   ├── __init__.py
│   │   ├── attack_context.py   # Context object
│   │   ├── complete_analysis.py # Response models
│   │   └── host.py             # Host model
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_client.py       # OpenAI integration
│   │   └── complete_analyzer.py # Main orchestrator
│   └── utils/
│       ├── __init__.py
│       ├── continuity_validator.py # Validation logic
│       └── token_logger.py     # Token tracking
├── tests/
│   ├── __init__.py
│   ├── test_analyzer.py
│   ├── test_llm_client.py
│   └── conftest.py
├── docs/                        # Documentation
├── examples/                    # Sample requests/responses
├── logs/                        # Application logs
├── requirements.txt             # Core dependencies
├── requirements-dev.txt         # Development dependencies
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Development Workflow

### 1. Create Feature Branch

```bash
# Update main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/my-feature

# Push to remote
git push origin feature/my-feature
```

### 2. Make Changes

See [CONTRIBUTING.md](../CONTRIBUTING.md) for code style guidelines.

Key practices:
- Write code following PEP 8
- Add type hints
- Include docstrings
- Write tests

### 3. Test Changes

#### Run All Tests

```bash
pytest

# With coverage
pytest --cov=app --cov-report=html

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

#### Run Specific Tests

```bash
# Single file
pytest tests/test_analyzer.py

# Single test
pytest tests/test_analyzer.py::test_artifact_extraction

# By marker
pytest -m slow
```

#### Test During Development

```bash
# Auto-run on file changes
pytest-watch

# Watch specific path
ptw tests/
```

### 4. Format and Lint Code

```bash
# Format with Black
black app/ tests/

# Check linting
ruff check app/ tests/

# Fix linting issues
ruff check --fix app/ tests/

# Type checking (optional)
mypy app/
```

### 5. Manual Testing

Test with sample requests:

```bash
# Test with example file
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d @examples/requests/linux_web_server_enhanced.json

# Test with inline request
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "target_description": "Test target",
    "context": "Test context"
  }'
```

### 6. Debug Code

#### Debug with Print Statements

```python
# In your code
from app.utils.token_logger import logger

logger.debug(f"Processing stage: {stage_index}")
logger.info(f"Artifact found: {artifact_name}")
logger.warning(f"Validation failed: {check_name}")
logger.error(f"Error occurred: {error_msg}")
```

#### Debug with Python Debugger

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use breakpoint() in Python 3.7+
breakpoint()

# Within debugger:
# n - next line
# s - step into
# c - continue
# p variable - print variable
# h - help
# q - quit
```

#### Debug with IDE

Set breakpoint in VS Code and run with debugger.

### 7. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add artifact extraction priority levels

- Implement 4-priority fallback strategy
- Add support for Windows and Linux artifacts
- Increase detection accuracy to 95%

Fixes #123"

# View commit
git log --oneline
```

### 8. Push and Create Pull Request

```bash
# Push changes
git push origin feature/my-feature

# Create PR on GitHub
# Use provided template
# Link related issues
```

## Testing Guidelines

### Writing Tests

Create tests in `tests/` directory:

```python
# tests/test_example.py
import pytest
from app.services.complete_analyzer import CompleteAnalyzer

@pytest.fixture
def analyzer():
    """Provide analyzer instance for testing."""
    return CompleteAnalyzer()

@pytest.mark.asyncio
async def test_artifact_extraction_success(analyzer):
    """Test artifact extraction with valid input."""
    content = "msfvenom -p linux/x86/shell -f elf -o payload.elf"
    artifact = analyzer._extract_artifact_name(content, stage_index=2)
    assert artifact == "payload.elf"

@pytest.mark.asyncio
async def test_artifact_extraction_no_match(analyzer):
    """Test artifact extraction with no matching pattern."""
    content = "This is some text without artifacts"
    artifact = analyzer._extract_artifact_name(content, stage_index=1)
    assert artifact is None

def test_error_handling(analyzer):
    """Test error handling in artifact extraction."""
    with pytest.raises(ValueError):
        analyzer._extract_artifact_name(None, stage_index=1)
```

### Running Tests

```bash
# All tests
pytest

# Tests matching pattern
pytest -k artifact

# Tests in file
pytest tests/test_analyzer.py

# With output
pytest -s

# With coverage
pytest --cov=app --cov-report=html
```

## Debugging Common Issues

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
```bash
# Ensure you're in project root
pwd  # Should show /path/to/ai-engine

# Ensure venv is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### OPENAI_API_KEY Not Found

**Problem**: `RuntimeError: OPENAI_API_KEY environment variable not set`

**Solution**:
```bash
# Check .env exists
ls -la .env

# Check it contains your key
grep OPENAI_API_KEY .env

# Source .env manually
export OPENAI_API_KEY=sk-your-key-here
```

### Port Already in Use

**Problem**: `Address already in use: ('127.0.0.1', 8000)`

**Solution**:
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
python -m app.main --port 8001
```

### Tests Failing

**Problem**: Test failures with async code

**Solution**:
```python
# Ensure pytest-asyncio installed
pip install pytest-asyncio

# Use @pytest.mark.asyncio decorator
@pytest.mark.asyncio
async def test_function():
    result = await some_async_function()
    assert result
```

## Performance Profiling

### Profile Code Execution

```python
import cProfile
import pstats
from io import StringIO

# Profile a function
profiler = cProfile.Profile()
profiler.enable()

# Your code here
result = analyzer.analyze(request)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 functions
```

### Measure Token Usage

Check `logs/token_usage.jsonl`:

```bash
# View recent token usage
tail -20 logs/token_usage.jsonl | jq .

# Analyze patterns
cat logs/token_usage.jsonl | jq '.total_tokens' | awk '{sum+=$1} END {print "Total:", sum}'
```

## Database Setup (Future)

When database support is added:

```bash
# Install database dependencies
pip install -r requirements-db.txt

# Run migrations
python -m alembic upgrade head

# Create test fixtures
python scripts/seed_db.py
```

## Documentation

### Building Documentation

```bash
# Install doc dependencies
pip install -r requirements-docs.txt

# Build HTML docs
make docs

# View docs
open docs/_build/html/index.html
```

### Documentation Standards

- Use Google-style docstrings
- Include type hints
- Add examples for complex functions
- Link to related documentation

```python
def analyze(self, request: AnalysisRequest) -> CompleteAnalysisResponse:
    """
    Analyze attack path for target system.
    
    Performs 7-stage attack path analysis with context threading and
    continuity validation. Results are returned with validation report.
    
    Args:
        request: Analysis request with target and context
        
    Returns:
        Comprehensive analysis with all 7 stages and validation results
        
    Raises:
        ValueError: If request validation fails
        TimeoutError: If analysis exceeds timeout
        
    Example:
        >>> request = AnalysisRequest(
        ...     target_description="Apache 2.4.41 on Ubuntu",
        ...     context="Authorized test"
        ... )
        >>> response = analyzer.analyze(request)
        >>> print(response.validation_report.is_valid)
        True
    """
```

## Release Process

### Version Bumping

```bash
# Update version in app/config.py
# Update CHANGELOG.md
# Commit and tag

git tag v1.0.1
git push origin v1.0.1
```

### Building Release

```bash
# Build Docker image
docker build -t pyramidxc/ai-engine:1.0.1 .

# Push to registry
docker push pyramidxc/ai-engine:1.0.1
```

## IDE Setup

### VS Code

1. Install Python extension (Microsoft)
2. Install Pylance extension
3. Install Black Formatter extension
4. Configure in `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.black-formatter"
  }
}
```

### PyCharm

1. Open project
2. Configure Python interpreter: Settings → Project → Python Interpreter
3. Select venv created earlier
4. Enable code inspections

## Useful Commands Cheat Sheet

```bash
# Activate environment
source venv/bin/activate

# Run app
python -m app.main

# Run tests
pytest

# Format code
black app/ tests/

# Check linting
ruff check app/ tests/

# Check types
mypy app/

# View logs
tail -f logs/token_usage.jsonl

# Clean cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Deactivate venv
deactivate
```

## Getting Help

- Check [SUPPORT.md](../SUPPORT.md) for FAQs
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines
- Open GitHub issue for problems

---

Last updated: 2024
