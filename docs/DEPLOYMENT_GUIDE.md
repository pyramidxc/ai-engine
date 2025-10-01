# 🚀 Deployment Guide: Local vs Docker

Complete guide to understanding when and how to use each deployment method.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Phase 1: Local Development](#phase-1-local-development-venv)
- [Phase 2: Docker Deployment](#phase-2-docker-deployment)
- [Comparison Matrix](#comparison-matrix)
- [Migration Guide](#-migration-guide)
- [Best Practices](#-best-practices)

---

## Overview

This project supports **two distinct deployment modes**, each optimized for different stages of the development lifecycle:

```bash
Development Phase          →          Deployment Phase
     (venv)                                (Docker)
       ↓                                      ↓
  Fast iteration                      Production ready
  Easy debugging                      Portable & isolated
  Local environment                   Cloud deployable
```

---

## 🔵 Phase 1: Local Development (venv) {#phase-1-local-development-venv}

### What Is Local Development (venv)?

A **Python virtual environment** that runs directly on your machine. You're running Python code natively with dependencies isolated in a `.venv` folder.

### When to Use

✅ **Active feature development**  
✅ **Debugging and troubleshooting**  
✅ **Rapid testing of changes**  
✅ **Learning the codebase**  
✅ **Writing unit tests**

### Local Setup

```bash
# 1. Create virtual environment
python3 -m venv .venv

# 2. Activate it
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 5. Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Local Development Advantages

| Benefit | Description |
|---------|-------------|
| ⚡ **Lightning Fast** | 2-3 second startup time |
| 🔄 **Hot Reload** | Changes reflect instantly with `--reload` |
| 🐛 **Easy Debugging** | Direct access to Python debugger |
| 💻 **IDE Integration** | Full autocomplete and type hints |
| 📁 **Direct File Access** | Edit files and see changes immediately |
| 🔍 **Clear Error Messages** | Stack traces point to exact code lines |

### Local Development Disadvantages

| Drawback | Description |
|----------|-------------|
| ❌ **OS Dependent** | May work differently on Windows/Mac/Linux |
| ❌ **Setup Required** | Need Python 3.10+, pip, dependencies |
| ❌ **Not Portable** | "Works on my machine" problem |
| ❌ **System Pollution** | Can conflict with other Python projects |

### Docker Workflow

```bash
# Morning: Start development
source .venv/bin/activate
uvicorn app.main:app --reload

# During day: Edit code
# → Changes reflect automatically

# Test your changes
python test_engine.py

# End of day: Deactivate
deactivate
```

---

## 🟢 Phase 2: Docker Deployment {#phase-2-docker-deployment}

### What Is It?

A **containerized environment** that packages your entire application (Python, dependencies, code) into an isolated, portable container that runs the same way everywhere.

### When to Use (Docker)

✅ **Deploying to production servers**  
✅ **Sharing with teammates**  
✅ **CI/CD pipelines**  
✅ **Cloud deployments (AWS, GCP, Azure)**  
✅ **Ensuring consistency across environments**  
✅ **Running on servers without Python**

### Setup

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 2. Start everything
docker-compose up -d

# That's it! No Python installation needed.
```

### Docker Deployment Advantages

| Benefit | Description |
|---------|-------------|
| ✅ **Universal Portability** | Works identically on any OS |
| ✅ **Complete Isolation** | No conflicts with other projects |
| ✅ **Production Ready** | Same environment in dev/staging/prod |
| ✅ **No Setup Required** | Just need Docker installed |
| ✅ **Easy Scaling** | Spin up multiple instances easily |
| ✅ **Version Locked** | Dependencies frozen in container |

### Docker Deployment Disadvantages

| Drawback | Description |
|----------|-------------|
| 🐌 **Slower Startup** | 10-20 seconds to start |
| 🔧 **Rebuild Required** | Code changes need container rebuild |
| 💾 **Larger Footprint** | Images can be 500MB - 1GB |
| 🐛 **Harder Debugging** | Need to exec into container |
| 📦 **Docker Required** | Need Docker/Docker Compose installed |

### Typical Workflow

```bash
# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f

# Make code changes
# (need to rebuild)
docker-compose up -d --build

# Stop when done
docker-compose down
```

---

## 📊 Comparison Matrix {#comparison-matrix}

### Performance

| Metric | Local (venv) | Docker |
|--------|-------------|--------|
| Startup Time | ⚡ 2-3 sec | 🐌 10-20 sec |
| Rebuild Time | N/A (instant) | 🐌 30-60 sec |
| Runtime Performance | ⭐⭐⭐⭐⭐ Native | ⭐⭐⭐⭐ Near-native |
| Memory Usage | ⚡ ~100MB | 💾 ~300MB |

### Developer Experience

| Aspect | Local (venv) | Docker |
|--------|-------------|--------|
| Hot Reload | ⭐⭐⭐⭐⭐ Yes | ⭐⭐ Need mount |
| Debugging | ⭐⭐⭐⭐⭐ Easy | ⭐⭐ Harder |
| IDE Support | ⭐⭐⭐⭐⭐ Full | ⭐⭐⭐ Partial |
| Error Messages | ⭐⭐⭐⭐⭐ Clear | ⭐⭐⭐ Sometimes obscure |

### Deployment

| Factor | Local (venv) | Docker |
|--------|-------------|--------|
| Portability | ⭐⭐ OS-dependent | ⭐⭐⭐⭐⭐ Universal |
| Setup Complexity | ⭐⭐⭐ Medium | ⭐⭐⭐⭐⭐ Simple |
| Production Ready | ⭐⭐ No | ⭐⭐⭐⭐⭐ Yes |
| Team Sharing | ⭐⭐ Difficult | ⭐⭐⭐⭐⭐ Easy |

---

## 🔄 Migration Guide

### From Local to Docker

```bash
# 1. Commit your changes
git add .
git commit -m "Ready for deployment"

# 2. Ensure .env is configured
cat .env  # Check it has your API keys

# 3. Build and run with Docker
docker-compose up -d

# 4. Verify it works
curl http://localhost:8000/health
```

### From Docker to Local

```bash
# 1. Stop Docker containers
docker-compose down

# 2. Activate venv
source .venv/bin/activate

# 3. Run locally
uvicorn app.main:app --reload

# 4. Resume development
```

---

## 🎯 Best Practices

### For Local Development

```bash
# ✅ DO: Always activate venv first
source .venv/bin/activate

# ✅ DO: Use --reload for instant changes
uvicorn app.main:app --reload

# ✅ DO: Keep dependencies updated
pip install --upgrade -r requirements.txt

# ❌ DON'T: Install packages globally
# Use: pip install <package>
# Not: sudo pip install <package>

# ❌ DON'T: Commit .venv/ folder
# It's in .gitignore for a reason
```

### For Docker Deployment

```bash
# ✅ DO: Use docker-compose for orchestration
docker-compose up -d

# ✅ DO: Check logs regularly
docker-compose logs -f

# ✅ DO: Rebuild after dependency changes
docker-compose up -d --build

# ❌ DON'T: Commit .env file
# Use .env.example as template

# ❌ DON'T: Run as root in production
# Use proper user permissions
```

---

## 🌟 Recommended Workflow

### Day-to-Day Development

```bash
┌─────────────────────────────────┐
│  Morning: Start Local Dev       │
├─────────────────────────────────┤
│  source .venv/bin/activate      │
│  uvicorn app.main:app --reload  │
└─────────────────────────────────┘
          ↓
┌─────────────────────────────────┐
│  During Day: Code & Test        │
├─────────────────────────────────┤
│  • Edit code (auto-reload)      │
│  • Run tests                    │
│  • Debug as needed              │
└─────────────────────────────────┘
          ↓
┌─────────────────────────────────┐
│  End of Day: Commit             │
├─────────────────────────────────┤
│  git add .                      │
│  git commit -m "..."            │
│  git push                       │
└─────────────────────────────────┘
```

### Before Deploying

```bash
┌─────────────────────────────────┐
│  1. Test Locally                │
├─────────────────────────────────┤
│  python test_engine.py          │
│  # Ensure everything works      │
└─────────────────────────────────┘
          ↓
┌─────────────────────────────────┐
│  2. Test with Docker            │
├─────────────────────────────────┤
│  docker-compose up --build      │
│  # Verify container works       │
└─────────────────────────────────┘
          ↓
┌─────────────────────────────────┐
│  3. Deploy to Production        │
├─────────────────────────────────┤
│  # On server                    │
│  git pull                       │
│  docker-compose up -d --build   │
└─────────────────────────────────┘
```

---

## 🆘 Troubleshooting

### "Import litellm could not be resolved" (Local)

```bash
# Solution: Reinstall in venv
source .venv/bin/activate
pip install --force-reinstall litellm>=1.40.0
```

### "Cannot connect to Docker daemon" (Docker)

```bash
# Solution: Start Docker service
sudo systemctl start docker  # Linux
# Or start Docker Desktop     # Mac/Windows
```

### "Port 8000 already in use"

```bash
# Solution 1: Stop other process
lsof -ti:8000 | xargs kill -9

# Solution 2: Use different port
uvicorn app.main:app --reload --port 8001
```

---

## 📚 Additional Resources

- **[Project README](../README.md)** - Project overview
- **[Quick Start Guide](QUICKSTART.md)** - Quick reference
- **[Usage Guide](USAGE.md)** - Detailed usage guide
- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)** - Technical details

---

**Remember**:

- 🔵 **Local = Development** (Use daily)
- 🟢 **Docker = Deployment** (Use when ready)

Choose the right tool for the job! 🚀
