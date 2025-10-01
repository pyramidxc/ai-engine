# 🚀 Quick Start Guide

Fast reference for getting up and running with the Attack Path Engine.

---

## 🎯 Which Mode Should I Use?

### 🔵 Local Development Mode (venv)

**Choose this if you are:**

- 👨‍💻 Actively developing features
- 🐛 Debugging code
- 🧪 Testing changes quickly
- 📝 Writing new functionality

### 🟢 Docker Mode

**Choose this if you are:**

- 🚀 Deploying to a server
- 👥 Sharing with teammates
- ☁️ Running in production
- 🔄 Setting up CI/CD

---

## 🔵 Local Development Setup (Recommended for Development)

### Step 1: Create Virtual Environment

```bash
python3 -m venv .venv
```

### Step 2: Activate Virtual Environment

```bash
# Linux/Mac
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
cp .env.example .env
nano .env  # or use your favorite editor
```

Add your API key:

```bash
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
```

### Step 5: Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ **Server running at**: `http://localhost:8000`  
✅ **Docs available at**: `http://localhost:8000/docs`  
✅ **Hot reload enabled** - changes reflect immediately!

---

## 🟢 Docker Setup (For Deployment)

### Step 1: Configure Environment

```bash
cp .env.example .env
nano .env  # Add your API key
```

### Step 2: Start with Docker Compose

```bash
docker-compose up -d
```

### Step 3: Check Logs (Optional)

```bash
docker-compose logs -f
```

### Step 4: Stop When Done

```bash
docker-compose down
```

✅ **Server running at**: `http://localhost:8000`  
✅ **Containerized** - works the same everywhere!

---

## 📊 Quick Comparison Table

| Feature | 🔵 Local (venv) | 🟢 Docker |
|---------|----------------|-----------|
| **Startup Time** | ⚡ 2-3 seconds | 🐌 10-20 seconds |
| **Code Changes** | Instant (--reload) | Need rebuild |
| **Setup Required** | Python + pip | Just Docker |
| **Debugging** | ⭐⭐⭐⭐⭐ Easy | ⭐⭐ Harder |
| **Portability** | ⭐⭐ OS-dependent | ⭐⭐⭐⭐⭐ Universal |
| **Production Ready** | ⭐⭐ No | ⭐⭐⭐⭐⭐ Yes |
| **Use When** | **Developing NOW** | **Deploying LATER** |

---

## 🧪 Test the API

```bash
# Health check
curl http://localhost:8000/health

# Analyze a host
curl -X POST http://localhost:8000/attack-path \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "example.com",
    "open_ports": [22, 80, 443],
    "vulnerabilities": ["CVE-2023-12345: SQL Injection"]
  }'

# Or use the example file
curl -X POST http://localhost:8000/attack-path \
  -H "Content-Type: application/json" \
  -d @example_request.json
```

## Run Test Script

```bash
python3 test_engine.py
```

## LLM Provider Configuration

Edit `.env` file:

### OpenAI (Default)

```bash
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
```

### Anthropic Claude

```bash
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-3-5-sonnet-20241022
```

### Google Gemini

```bash
GEMINI_API_KEY=...
LLM_MODEL=gemini/gemini-pro
```

### Azure OpenAI

```bash
AZURE_API_KEY=...
AZURE_API_BASE=https://your-resource.openai.azure.com
AZURE_API_VERSION=2024-02-15-preview
LLM_MODEL=azure/gpt-4
```

### Local Ollama

```bash
LLM_MODEL=ollama/llama2
# No API key needed, requires Ollama running locally
```

---

## 🔄 Switching Between Modes

### Currently in Local Development? ✅

```bash
# Just keep working!
# Your changes apply instantly with --reload
```

### Need to Deploy?

```bash
# Commit your changes
git add .
git commit -m "Ready for deployment"

# Switch to Docker
docker-compose up -d

# That's it! Now it's production-ready
```

### Going Back to Development?

```bash
# Stop Docker
docker-compose down

# Activate venv
source .venv/bin/activate

# Resume development
uvicorn app.main:app --reload
```

---

## 📚 API Documentation

Once running, visit:

- Swagger UI: [Swagger UI](http://localhost:8000/docs)
- ReDoc: [ReDoc](http://localhost:8000/redoc)

## Common Models

| Provider | Model | Cost | Quality |
|----------|-------|------|---------|
| OpenAI | gpt-4o-mini | $ | Good |
| OpenAI | gpt-4o | $$$ | Best |
| Anthropic | claude-3-5-sonnet | $$$ | Best |
| Google | gemini-pro | $$ | Good |
| Ollama | llama2 | Free | Good |

## Troubleshooting

### Import Error

```bash
pip install litellm>=1.40.0
```

### API Key Error

Check `.env` file has correct key for your provider

### Slow Responses

- Use faster models (gpt-4o-mini vs gpt-4o)
- Lower temperature in .env
- Check your internet connection

## File Structure

```bash
ai-engine/
├── app/main.py              # Main application
├── .env                     # Configuration
├── requirements.txt         # Dependencies
├── test_engine.py          # Test script
├── example_request.json    # Sample data
├── Dockerfile              # Container
├── docker-compose.yml      # Deployment
└── docs/
    ├── README.md           # Quick start
    ├── USAGE.md            # Full guide
    └── IMPLEMENTATION_SUMMARY.md
```

---

## 💡 Pro Tips

### For Development (Local)

```bash
# Always activate venv first
source .venv/bin/activate

# Use --reload for instant changes
uvicorn app.main:app --reload

# Keep a terminal open for logs
```

### For Production (Docker)

```bash
# Run in detached mode
docker-compose up -d

# Check logs when needed
docker-compose logs -f

# Update and restart
git pull && docker-compose up -d --build
```

---

## 📚 Next Steps

1. ✅ Choose your mode (Local vs Docker)
2. ✅ Start the server
3. ✅ Test with `curl` or `test_engine.py`
4. 📖 Read [Usage Guide](USAGE.md) for advanced features
5. � Check [Deployment Guide](DEPLOYMENT_GUIDE.md) for deployment options
6. 🔍 See [Implementation Summary](IMPLEMENTATION_SUMMARY.md) for technical details

---

## 🆘 Support

- 📖 Full Documentation: See [USAGE.md](USAGE.md)
- 🚀 Deployment Guide: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- ✅ Implementation Details: See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- 🏠 Back to main [README](../README.md)

---

**Remember:**

- 🔵 **Local = Development** (Use daily)
- 🟢 **Docker = Deployment** (Use when ready)
