# AI Attack Path Engine 🔒

FastAPI microservice that generates realistic attack paths from host exposure data collected by external systems. Uses AI to transform vulnerability and port scan data into step-by-step attack sequences.

## ✨ Features

- 🤖 **LLM-Powered Generation**: Uses AI to generate realistic, sequential attack paths
- 📊 **50+ Optional Parameters**: Accepts comprehensive host data for context-aware analysis
- 🔍 **Prompt Tracking**: Optional transparency feature to see generated prompts for debugging
- 🔄 **Multi-Provider Support**: Works with OpenAI, Anthropic, Google Gemini, Azure, and 100+ providers via LiteLLM
- 🏗️ **Clean Architecture**: Professional separation of concerns for maintainability
- 🚀 **Production-Ready**: Designed for scalability and async migration
- 🎯 **Risk Assessment**: Automatic risk level classification (Critical, High, Medium, Low)
- ⚡ **Fast & Modern**: Built with FastAPI and async support

---

## 🚀 Two Ways to Run This Project

### 🔵 Phase 1: Local Development (venv) - **For Active Development**

**Use this when**: Building features, debugging, testing changes quickly

```bash
# 1. Create & activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add your API key

# 4. Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Pros**: ⚡ Fast, 🔄 Hot reload, 🐛 Easy debugging  
**Cons**: Requires Python installed, OS-dependent

---

### 🟢 Phase 2: Docker Deployment - **For Production/Sharing**

**Use this when**: Deploying to servers, sharing with team, production environment

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env and add your API key

# 2. Start with Docker Compose
docker-compose up -d

# That's it! Everything is containerized and running
```

**Pros**: ✅ Works anywhere, ✅ No Python setup needed, ✅ Production-ready  
**Cons**: Slower rebuild, more complex debugging

---

## 📊 Quick Comparison

| Aspect | 🔵 Local Development (venv) | 🟢 Docker Deployment |
|--------|---------------------------|----------------------|
| **Speed** | ⚡ Fast startup | 🐌 Slower startup |
| **Use Case** | Active development | Production/Deployment |
| **Setup** | Need Python + pip | Just need Docker |
| **Code Changes** | Instant with --reload | Need container rebuild |
| **Portability** | OS-dependent | Works everywhere |
| **When to Use** | **RIGHT NOW** (building) | **LATER** (deploying) |

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Set your API key in `.env`:

```bash
OPENAI_API_KEY=your-api-key-here
LLM_MODEL=gpt-4o-mini
```

### 3. Run the Server

```bash
uvicorn app.main:app --reload
```

### 4. Test the API

```bash
curl -X POST http://localhost:8000/attack-path \
  -H "Content-Type: application/json" \
  -d @example_request.json
```

**Example Request Format** (using a few of the 50+ optional parameters):

```json
{
  "platform": "Linux",
  "version_os": "Ubuntu 20.04.3 LTS",
  "asset_name": "web-prod-01",
  "open_ports": [22, 80, 443, 3306],
  "services": [
    "OpenSSH 8.2p1 on port 22",
    "Apache httpd 2.4.41 on port 80",
    "MySQL 5.7.33 on port 3306"
  ],
  "vulnerabilities": [
    "CVE-2023-12345: SQL Injection"
  ],
  "mfa_enabled": false,
  "security_controls": ["CrowdStrike EDR"],
  "asset_criticality": "High"
}

_**Note**: All parameters are optional. Send any combination of the 50+ available parameters. See [INPUT_PARAMETERS.md](docs/INPUT_PARAMETERS.md) for the complete list._
```

Or run the test script:

```bash
python test_engine.py
```

## API Endpoints

- **GET** `/health` - Health check
- **POST** `/attack-path?include_prompt=true` - Generate attack path analysis
  - Query parameter `include_prompt` (default: `true`): Include generated prompt in response for debugging

## 📚 Documentation

### 📖 Guides & References

| Document | Description |
|----------|-------------|
| **[Quick Start Guide](docs/QUICKSTART.md)** | ⚡ Fast setup and basic usage |
| **[Architecture](docs/ARCHITECTURE.md)** | 🏛️ Clean architecture implementation details |
| **[Input Parameters](docs/INPUT_PARAMETERS.md)** | 📊 Complete list of 50+ optional parameters |
| **[Prompt Tracking](docs/PROMPT_TRACKING.md)** | 🔍 Transparency feature for debugging prompts |
| **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** | 🚀 Local vs Docker - choosing the right mode |
| **[Usage Guide](docs/USAGE.md)** | 📘 Complete API documentation and examples |
| **[Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md)** | 🔧 Technical architecture and design |

### 🔗 Live Documentation

- **Interactive API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)

> **💡 New to the project?** Start with the [Quick Start Guide](docs/QUICKSTART.md)!

## 🏗️ Project Structure

```bash
ai-engine/
├── app/
│   ├── main.py                    # FastAPI routes (Presentation Layer)
│   ├── config.py                  # Configuration management
│   ├── models/                    # Data models (Data Layer)
│   │   ├── host.py               # Input models
│   │   └── analysis.py           # Output models
│   ├── services/                  # Business logic (Business Layer)
│   │   ├── analyzer.py           # Attack path analysis orchestration
│   │   └── llm_client.py         # LLM API client
│   └── core/                      # Domain logic (Core Layer)
│       └── prompts.py            # Prompt building logic
├── docs/                          # 📚 Documentation
│   ├── QUICKSTART.md             # Quick reference guide
│   ├── ARCHITECTURE.md           # Clean architecture details
│   ├── REFACTORING_SUMMARY.md    # Refactoring documentation
│   ├── DEPLOYMENT_GUIDE.md       # Local vs Docker guide
│   ├── USAGE.md                  # Comprehensive usage
│   └── IMPLEMENTATION_SUMMARY.md # Technical details
├── .env                          # Environment variables (API keys)
├── .env.example                  # Template for configuration
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker container definition
├── docker-compose.yml            # Docker Compose orchestration
├── test_engine.py                # Test script
└── example_request.json          # Sample API request
```

### Architecture Highlights

The codebase follows **clean architecture** principles:

- **Presentation Layer** (`main.py`): HTTP routing only (~45 lines)
- **Business Logic** (`services/`): Orchestration and business rules
- **Core Domain** (`core/`): Domain-specific logic (prompts)
- **Data Layer** (`models/`): Data structures and validation
- **Infrastructure** (`config.py`): Configuration and external dependencies

**Benefits**:

- ✅ Easy to test (mockable components)
- ✅ Easy to maintain (single responsibility per file)
- ✅ Easy to extend (open/closed principle)
- ✅ Ready for async migration (clear interfaces)

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed design documentation.

## 🛠️ Tech Stack

- **FastAPI** - Modern Python web framework
- **LiteLLM** - Universal LLM API (supports 100+ providers)
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

## 🔒 Security Notes

- ⚠️ **Never commit `.env` file** - it contains sensitive API keys
- ✅ Use `.env.example` as a template
- 🔄 Rotate API keys regularly
- 🛡️ Implement rate limiting in production

## 🤝 Contributing

1. Use **local development (venv)** for development
2. Test your changes with `python test_engine.py`
3. Ensure Docker builds: `docker-compose build`
4. Update documentation if needed
5. Submit a pull request

## 📄 License

MIT

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/pyramidxc/ai-engine/issues)
- **Documentation**: See [docs/](docs/) folder
- **Email**: [your-email@example.com]

---

## **Built with ❤️ using FastAPI and LiteLLM**
