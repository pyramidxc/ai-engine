# AI Attack Path Engine - Technical Specification

## Document Purpose

This document provides detailed technical specifications for integration with the main architecture. It defines all inputs, outputs, data structures, APIs, and technical requirements for the Attack Path Engine microservice.

**Version**: 1.0.0  
**Last Updated**: October 1, 2025  
**Status**: Phase 1

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [API Specification](#2-api-specification)
3. [Data Models](#3-data-models)
4. [Integration Points](#4-integration-points)
5. [Technical Architecture](#5-technical-architecture)
6. [Deployment Specifications](#6-deployment-specifications)
7. [Security Requirements](#7-security-requirements)
8. [Performance Specifications](#8-performance-specifications)

---

## 1. System Overview

### 1.1 Service Description

The **Attack Path Engine** is a FastAPI-based microservice that generates realistic attack sequences from vulnerability and exposure data collected by external systems. It leverages AI (via LiteLLM) to transform raw security data into step-by-step attack paths with risk assessments.

**Key Characteristics**:

- **Type**: Stateless REST API microservice
- **Framework**: FastAPI (Python 3.10+)
- **AI Backend**: LiteLLM (supports 100+ LLM providers)
- **Deployment**: Docker container (8000/tcp)
- **Architecture**: Clean Architecture with separation of concerns
- **Phase**: Phase 1 (Attack Path Generation only)

### 1.2 System Boundaries

#### What the System Does ✅

- Receives vulnerability data from external collectors
- Generates realistic attack sequences using AI
- Maps attacks to MITRE ATT&CK framework
- Structures attacks using Cyber Kill Chain methodology
- Provides risk assessment (Critical/High/Medium/Low)
- Returns structured JSON responses

#### What the System Does NOT Do ❌

- Vulnerability scanning or data collection
- Security recommendations (Phase 2)
- Compliance framework mapping (Phase 2)
- Threat intelligence integration (Phase 2)
- Attack simulation execution

### 1.3 Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Runtime** | Python | 3.10+ | Application runtime |
| **Web Framework** | FastAPI | 0.112+ | REST API server |
| **ASGI Server** | Uvicorn | 0.30+ | Production server |
| **Data Validation** | Pydantic | 2.7+ | Schema validation |
| **LLM Client** | LiteLLM | 1.40.0+ | Universal LLM interface |
| **HTTP Client** | httpx | 0.27+ | Async HTTP requests |
| **Configuration** | python-dotenv | 1.0+ | Environment management |
| **Container** | Docker | 20.10+ | Containerization |
| **Orchestration** | Docker Compose | 2.0+ | Multi-container management |

---

## 2. API Specification

### 2.1 Base Configuration

```yaml
Base URL: http://localhost:8000
Protocol: HTTP/HTTPS
Content-Type: application/json
API Version: 1.0.0
```

### 2.2 Endpoints

#### 2.2.1 Health Check

**Endpoint**: `GET /health`

**Purpose**: Service health monitoring and configuration verification

**Request**: None

**Response**: `200 OK`

```json
{
  "status": "ok",
  "version": "1.0.0",
  "model": "gpt-4o-mini"
}
```

**Response Fields**:

- `status` (string): Service status (`"ok"` or `"error"`)
- `version` (string): API version
- `model` (string): Currently configured LLM model

**Use Cases**:

- Container health checks
- Load balancer health probes
- Service discovery validation
- Monitoring system integration

---

#### 2.2.2 Generate Attack Path

**Endpoint**: `POST /attack-path`

**Purpose**: Generate realistic attack sequence from collector data

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `include_prompt` | boolean | No | `true` | Include generated prompt in response for debugging/auditing |

**Request Headers**:

```http
Content-Type: application/json
```

**Request Body**:

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

**Success Response**: `200 OK`

```json
{
  "platform": "Linux",
  "version_os": "Ubuntu 20.04.3 LTS",
  "attack_path": [
    "Reconnaissance: Active network scanning using nmap (MITRE T1595.002) identifies Linux host with SSH (22), HTTP (80), HTTPS (443), MySQL (3306)",
    "Weaponization: Prepare SQL injection exploit for CVE-2023-12345 targeting Apache/MySQL stack",
    "Delivery: Direct exploitation via HTTP POST to vulnerable endpoint (MITRE T1190)",
    "Exploitation: SQL injection successful - extracting database credentials using UNION-based technique",
    "Installation: Establish persistence via cron job backdoor on Linux system (MITRE T1053.003)",
    "Command and Control: Setup reverse shell over HTTPS using Metasploit (MITRE T1071.001)",
    "Actions on Objectives: Credential dumping, lateral movement via SSH, data exfiltration (MITRE T1003, T1021.004, T1048)"
  ],
  "risk_level": "Critical",
  "generated_prompt": "Generate a realistic attack path...\\n\\n=== CORE SYSTEM INFO ===\\n- Platform: Linux\\n...[full prompt, ~5000-9000 characters]",
  "prompt_sections": 5
}
```

**Note**: `generated_prompt` and `prompt_sections` are included when `include_prompt=true` (default). Set `include_prompt=false` to omit them.

**Error Responses**:

| Status Code | Scenario | Response Body |
|-------------|----------|---------------|
| `422 Unprocessable Entity` | Invalid input data | `{"detail": "Invalid analysis data: <error>"}` |
| `500 Internal Server Error` | LLM failure or system error | `{"detail": "Error generating attack path: <error>"}` |
| `503 Service Unavailable` | LLM API unavailable | `{"detail": "LLM service unavailable"}` |

---

### 2.3 API Contract Details

#### Request Validation Rules

| Field | Type | Required | Constraints | Default |
|-------|------|----------|-------------|---------|
| `platform` | string | ✅ Yes | Non-empty, max 100 chars | - |
| `version_os` | string | ✅ Yes | Non-empty, max 200 chars | - |
| `open_ports` | array[int] | ❌ No | Valid port numbers (1-65535) | `[]` |
| `services` | array[string] | ❌ No | Each max 500 chars | `[]` |
| `vulnerabilities` | array[string] | ❌ No | Each max 1000 chars | `[]` |

#### Response Guarantees

| Field | Type | Guarantee |
|-------|------|-----------|
| `platform` | string | Always matches input `platform` |
| `version_os` | string | Always matches input `version_os` |
| `attack_path` | array[string] | Always 5-10 sequential steps |
| `risk_level` | string | Always one of: `Critical`, `High`, `Medium`, `Low` |

#### Attack Path Structure

Each step in `attack_path` follows this format:

```bash
<Kill Chain Phase>: <Action Description> (<MITRE Technique ID>)
```

**Example**:

```bash
"Exploitation: SQL injection successful - UNION-based technique (MITRE T1190)"
```

**Kill Chain Phases** (in order):

1. Reconnaissance
2. Weaponization
3. Delivery
4. Exploitation
5. Installation
6. Command and Control
7. Actions on Objectives

---

## 3. Data Models

### 3.1 Input Data Model

#### 3.1.1 InputHost Schema

**Purpose**: Represents host vulnerability and exposure data from external collectors

**Source**: `/app/models/host.py`

```python
class InputHost(BaseModel):
    """Input model for host exposure data from external collectors."""
    
    platform: str
    version_os: str
    open_ports: list[int] = []
    services: list[str] = []
    vulnerabilities: list[str] = []
```

**Field Specifications**:

| Field | Type | Description | Example Values |
|-------|------|-------------|----------------|
| `platform` | `string` | Operating system platform | `"Linux"`, `"Windows"`, `"macOS"`, `"BSD"` |
| `version_os` | `string` | Specific OS version and distribution | `"Ubuntu 20.04.3 LTS"`, `"Windows Server 2019"`, `"macOS 12.6 Monterey"` |
| `open_ports` | `array[integer]` | List of accessible network ports | `[22, 80, 443, 3306, 8080]` |
| `services` | `array[string]` | Services with versions on ports | `["OpenSSH 8.2p1 on port 22", "Apache 2.4.41 on port 80"]` |
| `vulnerabilities` | `array[string]` | CVEs and vulnerability descriptions | `["CVE-2023-12345: SQL Injection", "Weak credentials"]` |

**Validation Rules**:

- `platform`: Required, non-empty string
- `version_os`: Required, non-empty string
- `open_ports`: Optional, valid port range (1-65535)
- `services`: Optional, reasonable string lengths
- `vulnerabilities`: Optional, descriptive entries

**JSON Schema**:

```json
{
  "type": "object",
  "required": ["platform", "version_os"],
  "properties": {
    "platform": {
      "type": "string",
      "minLength": 1,
      "maxLength": 100
    },
    "version_os": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "open_ports": {
      "type": "array",
      "items": {
        "type": "integer",
        "minimum": 1,
        "maximum": 65535
      },
      "default": []
    },
    "services": {
      "type": "array",
      "items": {
        "type": "string",
        "maxLength": 500
      },
      "default": []
    },
    "vulnerabilities": {
      "type": "array",
      "items": {
        "type": "string",
        "maxLength": 1000
      },
      "default": []
    }
  }
}
```

---

### 3.2 Output Data Model

#### 3.2.1 AttackPathResponse Schema

**Purpose**: Represents generated attack path with risk assessment

**Source**: `/app/models/analysis.py`

```python
class AttackPathResponse(BaseModel):
    """Response model for attack path generation."""
    
    platform: str
    version_os: str
    attack_path: list[str]
    risk_level: str
```

**Field Specifications**:

| Field | Type | Description | Valid Values |
|-------|------|-------------|--------------|
| `platform` | `string` | Target system platform (echoed from input) | Any string from input |
| `version_os` | `string` | Target OS version (echoed from input) | Any string from input |
| `attack_path` | `array[string]` | Ordered attack sequence steps | 5-10 sequential steps |
| `risk_level` | `string` | Overall risk classification | `"Critical"`, `"High"`, `"Medium"`, `"Low"` |

**Attack Path Format**:
Each step follows Cyber Kill Chain phases with MITRE ATT&CK mappings:

```bash
"<Phase>: <Technical Action> (MITRE <Technique ID>)"
```

**Risk Level Definitions**:

| Level | Criteria | Impact |
|-------|----------|--------|
| `Critical` | Remote code execution, full system compromise, data breach | Immediate action required |
| `High` | Privilege escalation, significant data access, persistent access | Urgent remediation needed |
| `Medium` | Limited access, credential exposure, requires additional exploitation | Planned remediation |
| `Low` | Information disclosure, minimal impact, complex exploitation chain | Monitor and patch |

**JSON Schema**:

```json
{
  "type": "object",
  "required": ["platform", "version_os", "attack_path", "risk_level"],
  "properties": {
    "platform": {
      "type": "string"
    },
    "version_os": {
      "type": "string"
    },
    "attack_path": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "minItems": 5,
      "maxItems": 10
    },
    "risk_level": {
      "type": "string",
      "enum": ["Critical", "High", "Medium", "Low"]
    }
  }
}
```

---

## 4. Integration Points

### 4.1 Upstream Dependencies (External Systems)

#### 4.1.1 External Vulnerability Collectors

**Purpose**: Provide vulnerability and exposure data

**Integration Method**: HTTP POST to `/attack-path` endpoint

**Data Format**: JSON (InputHost schema)

**Examples of Compatible Systems**:

- Nmap with custom scripts
- OpenVAS
- Nessus Professional
- Qualys VMDR
- Custom vulnerability scanners
- SIEM systems with vulnerability data

**Integration Pattern**:

```python
import requests

# Collector system
scan_results = perform_vulnerability_scan(target)

# Transform to InputHost format
payload = {
    "platform": scan_results.os_type,
    "version_os": scan_results.os_version,
    "open_ports": scan_results.ports,
    "services": scan_results.detected_services,
    "vulnerabilities": scan_results.cves
}

# Call Attack Path Engine
response = requests.post(
    "http://attack-path-engine:8000/attack-path",
    json=payload
)

attack_path = response.json()
```

---

#### 4.1.2 LLM Providers (via LiteLLM)

**Purpose**: Generate attack path content using AI

**Integration Method**: LiteLLM universal client

**Supported Providers**:

| Provider | Model Examples | Configuration |
|----------|----------------|---------------|
| **OpenAI** | `gpt-4o-mini`, `gpt-4o`, `gpt-4-turbo` | `OPENAI_API_KEY` |
| **Anthropic** | `claude-3-opus`, `claude-3-sonnet` | `ANTHROPIC_API_KEY` |
| **Google** | `gemini-pro`, `gemini-1.5-pro` | `GOOGLE_API_KEY` |
| **Azure OpenAI** | `azure/gpt-4` | `AZURE_API_KEY`, `AZURE_API_BASE` |
| **AWS Bedrock** | `bedrock/claude-v2` | AWS credentials |
| **Cohere** | `command`, `command-light` | `COHERE_API_KEY` |
| **Ollama** | `llama2`, `mistral` | Local deployment |

**Configuration**:

```bash
# Environment variables
LLM_MODEL=gpt-4o-mini              # Model name
LLM_TEMPERATURE=0.7                # Creativity (0.0-1.0)
OPENAI_API_KEY=sk-...              # Provider API key
```

**Provider Switching**:

```bash
# Switch to Anthropic
LLM_MODEL=claude-3-sonnet-20240229
ANTHROPIC_API_KEY=sk-ant-...

# Switch to Ollama (local)
LLM_MODEL=ollama/llama2
OLLAMA_API_BASE=http://localhost:11434
```

**Error Handling**:

- LLM API failures return HTTP 500
- Timeout after 60 seconds
- Automatic retry not implemented (caller responsibility)

---

### 4.2 Downstream Consumers

#### 4.2.1 Security Dashboards

**Integration Pattern**: Poll or webhook-triggered requests

**Use Case**: Display attack paths in security operations center (SOC)

**Example**:

```javascript
// Dashboard integration
async function loadAttackPath(targetHost) {
  const response = await fetch('/attack-path', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(targetHost)
  });
  
  const attackPath = await response.json();
  displayAttackVisualization(attackPath);
}
```

---

#### 4.2.2 Report Generation Systems

**Integration Pattern**: Batch processing of multiple hosts

**Use Case**: Generate executive reports with attack scenarios

**Example**:

```python
# Report generation
import asyncio
import aiohttp

async def generate_report(targets):
    async with aiohttp.ClientSession() as session:
        tasks = [
            generate_attack_path(session, target)
            for target in targets
        ]
        attack_paths = await asyncio.gather(*tasks)
    
    return create_pdf_report(attack_paths)

async def generate_attack_path(session, target):
    async with session.post(
        'http://attack-path-engine:8000/attack-path',
        json=target
    ) as resp:
        return await resp.json()
```

---

#### 4.2.3 Incident Response Platforms

**Integration Pattern**: Real-time API calls during incidents

**Use Case**: Generate attack scenarios for active incidents

**Example**:

```python
# SOAR platform integration
def enrich_incident(incident_id):
    incident = get_incident(incident_id)
    
    # Get attack path
    attack_path = requests.post(
        'http://attack-path-engine:8000/attack-path',
        json=incident.host_data
    ).json()
    
    # Enrich incident
    incident.attack_scenario = attack_path['attack_path']
    incident.risk_level = attack_path['risk_level']
    incident.save()
```

---

### 4.3 Configuration Dependencies

#### 4.3.1 Environment Variables

**Required**:

```bash
OPENAI_API_KEY=sk-...              # LLM provider API key (required)
```

**Optional**:

```bash
LLM_MODEL=gpt-4o-mini              # Default: gpt-4o-mini
LLM_TEMPERATURE=0.7                # Default: 0.7
```

**Provider-Specific**:

```bash
# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Google
GOOGLE_API_KEY=...

# Azure OpenAI
AZURE_API_KEY=...
AZURE_API_BASE=https://...openai.azure.com/
AZURE_API_VERSION=2023-05-15

# AWS Bedrock
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION_NAME=us-east-1
```

---

## 5. Technical Architecture

### 5.1 System Architecture Diagram

```bash
┌─────────────────────────────────────────────────────────────┐
│                  External Vulnerability Collectors          │
│              (Nmap, OpenVAS, Nessus, Custom Scanners)       │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP POST
                      │ /attack-path
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Attack Path Engine API                     │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Presentation Layer (main.py)                 │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │  │
│  │  │ /health    │  │/attack-path│  │ Error      │    │  │
│  │  │ Endpoint   │  │ Endpoint   │  │ Handlers   │    │  │
│  │  └──────┬─────┘  └──────┬─────┘  └─────┬──────┘    │  │
│  └─────────┼────────────────┼──────────────┼───────────┘  │
│            │                │              │              │
│  ┌─────────▼────────────────▼──────────────▼───────────┐  │
│  │      Business Logic Layer (services/)               │  │
│  │  ┌──────────────────────────────────────────────┐  │  │
│  │  │  AttackPathAnalyzer                          │  │  │
│  │  │  - Orchestrates analysis workflow            │  │  │
│  │  │  - Coordinates prompt building & LLM calls   │  │  │
│  │  │  - Validates and structures responses        │  │  │
│  │  └──────────┬────────────────────────┬──────────┘  │  │
│  └─────────────┼────────────────────────┼─────────────┘  │
│                │                        │                │
│  ┌─────────────▼────────┐    ┌──────────▼──────────┐   │
│  │  Core Layer (core/)  │    │ Infrastructure       │   │
│  │  ┌────────────────┐  │    │ (services/)          │   │
│  │  │ PromptBuilder  │  │    │ ┌────────────────┐  │   │
│  │  │ - Build prompts│  │    │ │ LLMClient      │  │   │
│  │  │ - MITRE ATT&CK │  │    │ │ - LiteLLM API  │  │   │
│  │  │ - Kill Chain   │  │    │ │ - JSON parsing │  │   │
│  │  └────────────────┘  │    │ └────────┬───────┘  │   │
│  └──────────────────────┘    └───────────┼──────────┘   │
│                                           │              │
│  ┌────────────────────────────────────────▼───────────┐  │
│  │         Data Layer (models/)                       │  │
│  │  ┌──────────────┐         ┌──────────────────┐    │  │
│  │  │  InputHost   │         │ AttackPathResponse│   │  │
│  │  │  - Pydantic  │         │ - Pydantic        │   │  │
│  │  └──────────────┘         └──────────────────┘    │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────┘
                            │ HTTPS/API Call
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              LLM Providers (via LiteLLM)                    │
│  OpenAI │ Anthropic │ Google │ Azure │ AWS │ Ollama        │
└─────────────────────────────────────────────────────────────┘
```

---

### 5.2 Component Details

#### 5.2.1 Presentation Layer

**File**: `app/main.py`

**Responsibilities**:

- Define FastAPI routes and endpoints
- Handle HTTP request/response cycle
- Validate requests using Pydantic
- Format error responses
- Implement health checks

**Key Components**:

```python
app = FastAPI(...)              # FastAPI application
analyzer = AttackPathAnalyzer() # Service instance
@app.post("/attack-path")       # Route handler
```

---

#### 5.2.2 Business Logic Layer

**File**: `app/services/analyzer.py`

**Responsibilities**:

- Orchestrate attack path generation workflow
- Coordinate between prompt building and LLM calls
- Transform collector data into structured prompts
- Parse and validate LLM responses
- Build AttackPathResponse objects

**Dependencies**:

- `LLMClient` (infrastructure)
- `PromptBuilder` (core)
- `InputHost`, `AttackPathResponse` (data models)

---

#### 5.2.3 Core Domain Layer

**File**: `app/core/prompts.py`

**Responsibilities**:

- Centralize prompt engineering logic
- Build structured prompts from host data
- Maintain MITRE ATT&CK and Cyber Kill Chain templates
- Encapsulate offensive security domain knowledge
- Define attack path generation guidelines

**Key Functions**:

```python
def build_attack_analysis_prompt(host: InputHost) -> str
    """Build AI prompt from host data"""
```

---

#### 5.2.4 Infrastructure Layer

**File**: `app/services/llm_client.py`

**Responsibilities**:

- Abstract all LLM API interactions
- Handle LiteLLM client configuration
- Parse LLM JSON responses
- Manage errors from LLM providers
- Support multiple LLM providers

**Key Functions**:

```python
async def complete(prompt: str) -> dict
    """Call LLM and return parsed JSON"""
```

---

#### 5.2.5 Data Layer

**Files**:

- `app/models/host.py` (input)
- `app/models/analysis.py` (output)

**Responsibilities**:

- Define data structures with Pydantic
- Enforce type safety and validation
- Document field schemas with examples
- Provide serialization/deserialization

---

### 5.3 Data Flow Sequence

```bash
1. External Collector → POST /attack-path
   ├─ Request: InputHost JSON
   └─ Headers: Content-Type: application/json

2. FastAPI Route Handler (main.py)
   ├─ Validate request with Pydantic
   ├─ Extract InputHost model
   └─ Call analyzer.analyze(host)

3. AttackPathAnalyzer (services/analyzer.py)
   ├─ Receive InputHost
   ├─ Call prompt_builder.build_prompt(host)
   └─ Get formatted prompt string

4. PromptBuilder (core/prompts.py)
   ├─ Extract platform, version_os, ports, services, vulns
   ├─ Build system message (MITRE ATT&CK + Kill Chain)
   ├─ Build user message (host details)
   └─ Return complete prompt

5. AttackPathAnalyzer → LLMClient
   ├─ Call llm_client.complete(prompt)
   └─ Wait for LLM response

6. LLMClient (services/llm_client.py)
   ├─ Initialize LiteLLM client
   ├─ Call LiteLLM API with JSON mode
   ├─ Wait for provider response (OpenAI/Anthropic/etc)
   └─ Parse JSON response

7. LLM Provider (OpenAI/Anthropic/Google/etc)
   ├─ Process prompt
   ├─ Generate attack path with MITRE mappings
   └─ Return JSON response

8. LLMClient → AttackPathAnalyzer
   ├─ Return parsed dict
   └─ Handle errors if any

9. AttackPathAnalyzer
   ├─ Validate response structure
   ├─ Build AttackPathResponse model
   └─ Return to route handler

10. Route Handler → HTTP Response
    ├─ Serialize AttackPathResponse to JSON
    ├─ Return 200 OK
    └─ Send to external collector
```

---

## 6. Deployment Specifications

### 6.1 Container Specifications

#### 6.1.1 Docker Image

**Base Image**: `python:3.10-slim`

**Image Size**: ~150 MB (after optimization)

**Dockerfile**: `/Dockerfile`

**Build Command**:

```bash
docker build -t attack-path-engine:1.0.0 .
```

**Image Layers**:

1. Python 3.10 slim base
2. System dependencies (curl)
3. Python packages (FastAPI, LiteLLM, etc.)
4. Application code
5. Non-root user creation

**Security Features**:

- Non-root user (`appuser`, UID 1000)
- Minimal system packages
- No unnecessary dependencies
- Health check built-in

---

#### 6.1.2 Container Runtime

**Resource Requirements**:

| Resource | Minimum | Recommended | Maximum |
|----------|---------|-------------|---------|
| **CPU** | 0.5 cores | 1 core | 2 cores |
| **Memory** | 256 MB | 512 MB | 1 GB |
| **Disk** | 200 MB | 500 MB | 1 GB |
| **Network** | 100 Mbps | 1 Gbps | 10 Gbps |

**Port Mappings**:

```yaml
Container Port 8000 → Host Port 8000
Protocol: TCP
```

**Environment Variables** (runtime):

```bash
OPENAI_API_KEY=<required>
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
```

---

### 6.2 Docker Compose Deployment

**File**: `/docker-compose.yml`

**Start Service**:

```bash
docker-compose up -d
```

**Stop Service**:

```bash
docker-compose down
```

**View Logs**:

```bash
docker-compose logs -f attack-path-engine
```

**Configuration**:

```yaml
version: '3.8'

services:
  attack-path-engine:
    build: .
    container_name: attack-path-engine
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LLM_MODEL=${LLM_MODEL:-gpt-4o-mini}
      - LLM_TEMPERATURE=${LLM_TEMPERATURE:-0.7}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
```

---

### 6.3 Kubernetes Deployment

**Deployment YAML** (example):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: attack-path-engine
  labels:
    app: attack-path-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: attack-path-engine
  template:
    metadata:
      labels:
        app: attack-path-engine
    spec:
      containers:
      - name: attack-path-engine
        image: attack-path-engine:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-credentials
              key: openai-api-key
        - name: LLM_MODEL
          value: "gpt-4o-mini"
        - name: LLM_TEMPERATURE
          value: "0.7"
        resources:
          requests:
            memory: "256Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: attack-path-engine
spec:
  selector:
    app: attack-path-engine
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: ClusterIP
```

**Service Mesh Considerations**:

- Compatible with Istio, Linkerd
- Supports mTLS for inter-service communication
- Can integrate with service mesh observability

---

### 6.4 Cloud Provider Deployments

#### 6.4.1 AWS Deployment Options

**Option 1: ECS Fargate**:

```json
{
  "family": "attack-path-engine",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [{
    "name": "attack-path-engine",
    "image": "attack-path-engine:1.0.0",
    "portMappings": [{
      "containerPort": 8000,
      "protocol": "tcp"
    }],
    "environment": [
      {"name": "LLM_MODEL", "value": "gpt-4o-mini"},
      {"name": "LLM_TEMPERATURE", "value": "0.7"}
    ],
    "secrets": [{
      "name": "OPENAI_API_KEY",
      "valueFrom": "arn:aws:secretsmanager:region:account:secret:openai-key"
    }],
    "healthCheck": {
      "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
      "interval": 30,
      "timeout": 5,
      "retries": 3
    }
  }]
}
```

**Option 2: Lambda + API Gateway**:

- Use AWS Lambda Adapter for FastAPI
- Cold start: ~2-3 seconds
- Suitable for low-traffic scenarios

**Option 3: EKS (Kubernetes)**:

- Use Kubernetes manifests from section 6.3
- Integrate with AWS Load Balancer Controller

---

#### 6.4.2 Azure Deployment Options

**Azure Container Instances**:

```bash
az container create \
  --resource-group attack-path-rg \
  --name attack-path-engine \
  --image attack-path-engine:1.0.0 \
  --cpu 1 \
  --memory 1 \
  --ports 8000 \
  --environment-variables \
    LLM_MODEL=gpt-4o-mini \
    LLM_TEMPERATURE=0.7 \
  --secure-environment-variables \
    OPENAI_API_KEY=$OPENAI_API_KEY
```

**Azure Kubernetes Service (AKS)**:

- Use Kubernetes manifests from section 6.3
- Integrate with Azure Application Gateway

---

#### 6.4.3 Google Cloud Deployment Options

**Cloud Run**:

```bash
gcloud run deploy attack-path-engine \
  --image attack-path-engine:1.0.0 \
  --platform managed \
  --region us-central1 \
  --port 8000 \
  --memory 1Gi \
  --cpu 1 \
  --set-env-vars LLM_MODEL=gpt-4o-mini,LLM_TEMPERATURE=0.7 \
  --set-secrets OPENAI_API_KEY=openai-key:latest
```

**GKE (Kubernetes)**:

- Use Kubernetes manifests from section 6.3
- Integrate with Google Cloud Load Balancing

---

### 6.5 Development Setup

**Local Development**:

```bash
# Clone repository
git clone <repo-url>
cd ai-engine

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Hot Reload**: Enabled with `--reload` flag (development only)

---

## 7. Security Requirements

### 7.1 Authentication & Authorization

**Current State**: ⚠️ No authentication (Phase 1)

**Phase 2 Recommendations**:

- API key authentication
- JWT tokens for service-to-service
- OAuth 2.0 for user-facing applications
- Rate limiting per API key

**Example Implementation** (Phase 2):

```python
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/attack-path")
async def attack_path(
    host: InputHost,
    token: str = Security(security)
):
    validate_api_key(token.credentials)
    return await analyzer.analyze(host)
```

---

### 7.2 Data Security

#### 7.2.1 Data in Transit

**Requirements**:

- ✅ HTTPS/TLS 1.2+ for production deployments
- ✅ Certificate validation enabled
- ✅ Secure headers (HSTS, CSP)

**Implementation**:

```bash
# Production deployment with TLS
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --ssl-keyfile /path/to/key.pem \
  --ssl-certfile /path/to/cert.pem
```

**Reverse Proxy** (recommended):

```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;
    
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    location / {
        proxy_pass http://attack-path-engine:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

#### 7.2.2 Data at Rest

**Input Data**: Not persisted (stateless service)

**LLM Responses**: Not cached (Phase 1)

**Logs**:

- ✅ Sanitize sensitive data (API keys, credentials)
- ✅ Rotate logs daily
- ✅ Encrypt log storage

---

#### 7.2.3 Secrets Management

**Current Implementation**: Environment variables via `.env`

**Production Recommendations**:

| Platform | Solution |
|----------|----------|
| **AWS** | AWS Secrets Manager, Parameter Store |
| **Azure** | Azure Key Vault |
| **Google Cloud** | Secret Manager |
| **Kubernetes** | Kubernetes Secrets, External Secrets Operator |
| **Docker** | Docker Secrets |
| **Vault** | HashiCorp Vault |

**Example** (AWS Secrets Manager):

```python
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

# Load API key from Secrets Manager
OPENAI_API_KEY = get_secret('prod/openai/api-key')
```

---

### 7.3 Input Validation

**Implemented**:

- ✅ Pydantic schema validation
- ✅ Type checking on all inputs
- ✅ Field length constraints
- ✅ Port number range validation (1-65535)

**Protections**:

- Prevents injection attacks
- Validates data types
- Enforces required fields
- Rejects malformed JSON

---

### 7.4 Rate Limiting

**Current State**: ⚠️ Not implemented (Phase 1)

**Phase 2 Recommendation**:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/attack-path")
@limiter.limit("10/minute")
async def attack_path(host: InputHost):
    return await analyzer.analyze(host)
```

---

### 7.5 Security Headers

**Recommended Headers** (via reverse proxy or middleware)

```python
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

---

### 7.6 Dependency Security

**Requirements**:

- ✅ Pin all dependency versions (`requirements.txt`)
- ✅ Regular security updates
- ✅ Vulnerability scanning

**Tools**:

```bash
# Scan for vulnerabilities
pip install safety
safety check -r requirements.txt

# Update dependencies
pip install --upgrade -r requirements.txt
```

---

## 8. Performance Specifications

### 8.1 Response Time Targets

| Metric | Target | Measurement Point |
|--------|--------|-------------------|
| **Health Check** | < 50ms | 95th percentile |
| **Attack Path Generation** | < 5s | 95th percentile |
| **P50 (Median)** | < 2s | Attack path endpoint |
| **P90** | < 4s | Attack path endpoint |
| **P99** | < 8s | Attack path endpoint |
| **Timeout** | 60s | Hard limit |

**Note**: LLM API latency is the dominant factor (1.5-4s typical)

---

### 8.2 Throughput

| Metric | Target | Notes |
|--------|--------|-------|
| **Concurrent Requests** | 100+ | With proper scaling |
| **Requests per Second** | 20-50 | Limited by LLM provider |
| **Daily Requests** | 50,000+ | With rate limiting |

**Bottleneck**: LLM provider rate limits (e.g., OpenAI TPM limits)

---

### 8.3 Resource Utilization

**Single Container**:

- **CPU**: ~30-50% utilization under load (1 core)
- **Memory**: ~200-400 MB steady state
- **Network**: ~100 KB per request (input + output)
- **Disk**: Minimal (logs only)

**Scaling Formula**:

```bash
Containers Needed = (Target RPS × Avg Response Time) / Concurrency per Container

Example:
- Target: 100 RPS
- Avg Response: 3s
- Concurrency: 10 per container
- Containers: (100 × 3) / 10 = 30 containers
```

---

### 8.4 Scalability

#### 8.4.1 Horizontal Scaling

**Stateless Design**: ✅ Fully supports horizontal scaling

**Load Balancing**:

```yaml
# Kubernetes HPA (Horizontal Pod Autoscaler)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: attack-path-engine-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: attack-path-engine
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**AWS ECS Autoscaling**:

```json
{
  "ServiceName": "attack-path-engine",
  "MinCapacity": 3,
  "MaxCapacity": 20,
  "TargetValue": 70,
  "ScaleInCooldown": 300,
  "ScaleOutCooldown": 60
}
```

---

#### 8.4.2 Vertical Scaling

**Resource Adjustments**:

- Increase CPU: Better concurrency handling
- Increase Memory: Support larger prompts/responses
- Not recommended as primary scaling strategy

---

### 8.5 Caching Strategy (Phase 2)

**Current State**: ⚠️ No caching (Phase 1)

**Phase 2 Recommendations**:

**Cache Key**: Hash of input data

```python
import hashlib
import json

def cache_key(host: InputHost) -> str:
    data = json.dumps(host.dict(), sort_keys=True)
    return hashlib.sha256(data.encode()).hexdigest()
```

**Cache Implementation** (Redis):

```python
import redis

redis_client = redis.Redis(host='redis', port=6379, db=0)

async def get_cached_attack_path(host: InputHost):
    key = cache_key(host)
    cached = redis_client.get(key)
    
    if cached:
        return json.loads(cached)
    
    # Generate new attack path
    result = await analyzer.analyze(host)
    
    # Cache for 24 hours
    redis_client.setex(key, 86400, json.dumps(result.dict()))
    
    return result
```

**Cache Invalidation**: Time-based (TTL: 24 hours recommended)

---

### 8.6 Monitoring & Observability

#### 8.6.1 Metrics to Track

**Application Metrics**:

- Request count (total, success, failure)
- Response time (p50, p90, p95, p99)
- Error rate (4xx, 5xx)
- LLM API latency
- LLM token usage

**System Metrics**:

- CPU utilization
- Memory utilization
- Network I/O
- Disk I/O (logs)

**Business Metrics**:

- Attack paths generated per day
- Risk level distribution (Critical/High/Medium/Low)
- Average attack path steps
- LLM model usage

---

#### 8.6.2 Prometheus Integration

**Metrics Endpoint** (Phase 2):

```python
from prometheus_fastapi_instrumentator import Instrumentator

# Add metrics endpoint
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Custom metrics
from prometheus_client import Counter, Histogram

attack_paths_generated = Counter(
    'attack_paths_generated_total',
    'Total number of attack paths generated',
    ['risk_level']
)

generation_duration = Histogram(
    'attack_path_generation_duration_seconds',
    'Time spent generating attack paths'
)
```

---

#### 8.6.3 Logging

**Current Implementation**: Python `logging` module

**Log Format**: JSON structured logs (recommended)

**Log Levels**:

- `INFO`: Request received, attack path generated
- `WARNING`: Slow LLM response, partial data
- `ERROR`: LLM failure, validation errors
- `DEBUG`: Detailed prompt/response data (dev only)

**Example**:

```python
import logging
import json

logger = logging.getLogger("attack-path-engine")

# Structured logging
logger.info(json.dumps({
    "event": "attack_path_generated",
    "platform": host.platform,
    "risk_level": result.risk_level,
    "duration_ms": duration,
    "llm_model": settings.LLM_MODEL
}))
```

**Log Aggregation**:

- ELK Stack (Elasticsearch, Logstash, Kibana)
- Grafana Loki
- CloudWatch Logs (AWS)
- Azure Monitor
- Google Cloud Logging

---

#### 8.6.4 Distributed Tracing

**OpenTelemetry Integration** (Phase 2):

```python
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

tracer = trace.get_tracer(__name__)

FastAPIInstrumentor.instrument_app(app)

@app.post("/attack-path")
async def attack_path(host: InputHost):
    with tracer.start_as_current_span("generate_attack_path"):
        result = await analyzer.analyze(host)
        return result
```

---

### 8.7 Disaster Recovery

#### 8.7.1 Backup Strategy

**No Data to Back Up**: Stateless service

**Configuration Backup**:

- Store `.env.example` in version control
- Backup actual secrets in secrets manager
- Document environment variables

#### 8.7.2 Service Recovery

**Recovery Time Objective (RTO)**: < 5 minutes

**Recovery Point Objective (RPO)**: N/A (stateless)

**Recovery Steps**:

1. Deploy new container from image
2. Load secrets from secrets manager
3. Health check passes
4. Route traffic to new instance

**Multi-Region Deployment** (high availability):

- Deploy to multiple cloud regions
- Use global load balancer
- Automatic failover on region failure

---

## Appendix

### A. Example Integration Code

#### A.1 Python Client

```python
import requests

class AttackPathClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def generate_attack_path(self, host_data):
        """Generate attack path from collector data"""
        response = requests.post(
            f"{self.base_url}/attack-path",
            json=host_data,
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    
    def health_check(self):
        """Check service health"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

# Usage
client = AttackPathClient()

host = {
    "platform": "Linux",
    "version_os": "Ubuntu 20.04.3 LTS",
    "open_ports": [22, 80, 443, 3306],
    "services": [
        "OpenSSH 8.2p1 on port 22",
        "Apache httpd 2.4.41 on port 80",
        "MySQL 5.7.33 on port 3306"
    ],
    "vulnerabilities": [
        "CVE-2023-12345: SQL Injection",
        "CVE-2023-23456: Weak SSH configuration"
    ]
}

result = client.generate_attack_path(host)
print(f"Risk Level: {result['risk_level']}")
for step in result['attack_path']:
    print(f"- {step}")
```

#### A.2 JavaScript/Node.js Client

```javascript
const axios = require('axios');

class AttackPathClient {
  constructor(baseURL = 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
      timeout: 60000,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  async generateAttackPath(hostData) {
    const response = await this.client.post('/attack-path', hostData);
    return response.data;
  }

  async healthCheck() {
    const response = await this.client.get('/health');
    return response.data;
  }
}

// Usage
(async () => {
  const client = new AttackPathClient();
  
  const host = {
    platform: "Linux",
    version_os: "Ubuntu 20.04.3 LTS",
    open_ports: [22, 80, 443, 3306],
    services: [
      "OpenSSH 8.2p1 on port 22",
      "Apache httpd 2.4.41 on port 80"
    ],
    vulnerabilities: [
      "CVE-2023-12345: SQL Injection"
    ]
  };
  
  const result = await client.generateAttackPath(host);
  console.log(`Risk Level: ${result.risk_level}`);
  result.attack_path.forEach(step => console.log(`- ${step}`));
})();
```

#### A.3 cURL Examples

```bash
# Health check
curl -X GET http://localhost:8000/health

# Generate attack path
curl -X POST http://localhost:8000/attack-path \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "Linux",
    "version_os": "Ubuntu 20.04.3 LTS",
    "open_ports": [22, 80, 443, 3306],
    "services": [
      "OpenSSH 8.2p1 on port 22",
      "Apache httpd 2.4.41 on port 80"
    ],
    "vulnerabilities": [
      "CVE-2023-12345: SQL Injection"
    ]
  }'

# Pretty print response
curl -X POST http://localhost:8000/attack-path \
  -H "Content-Type: application/json" \
  -d @example_request.json | jq .
```

---

### B. Environment Configuration Reference

```bash
# ====================
# REQUIRED VARIABLES
# ====================

# LLM Provider API Key (at least one required)
OPENAI_API_KEY=sk-...                   # OpenAI API key

# ====================
# OPTIONAL VARIABLES
# ====================

# LLM Configuration
LLM_MODEL=gpt-4o-mini                   # Default: gpt-4o-mini
LLM_TEMPERATURE=0.7                     # Default: 0.7 (0.0-1.0)

# Alternative LLM Providers
ANTHROPIC_API_KEY=sk-ant-...            # Anthropic Claude
GOOGLE_API_KEY=...                      # Google Gemini
COHERE_API_KEY=...                      # Cohere

# Azure OpenAI
AZURE_API_KEY=...
AZURE_API_BASE=https://....openai.azure.com/
AZURE_API_VERSION=2023-05-15

# AWS Bedrock
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION_NAME=us-east-1

# Local Ollama
OLLAMA_API_BASE=http://localhost:11434

# ====================
# PHASE 2 VARIABLES
# ====================

# Redis Cache (future)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=...

# Authentication (future)
API_KEY_ENABLED=true
API_KEYS=key1,key2,key3

# Rate Limiting (future)
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=10

# Monitoring (future)
PROMETHEUS_ENABLED=true
METRICS_PORT=9090
```

---

### C. Glossary

| Term | Definition |
|------|------------|
| **Attack Path** | Sequential steps showing how an attacker exploits vulnerabilities |
| **Cyber Kill Chain** | 7-phase attack methodology (Lockheed Martin) |
| **LiteLLM** | Universal LLM client supporting 100+ providers |
| **MITRE ATT&CK** | Knowledge base of adversary tactics and techniques |
| **Pydantic** | Python data validation library using type hints |
| **Risk Level** | Classification of attack severity (Critical/High/Medium/Low) |
| **Stateless** | No data persistence between requests |
| **Vulnerability Collector** | External system that scans and identifies vulnerabilities |

---

### D. Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-01 | Initial technical specification |

---

### E. Support & Contact

**Documentation**: See `/docs` folder for additional guides

- `ARCHITECTURE.md` - System architecture details
- `DEPLOYMENT_GUIDE.md` - Deployment instructions
- `USAGE.md` - API usage examples
- `QUICKSTART.md` - Quick start guide
- `PHASE1_SCOPE.md` - Project scope and vision

**Repository**: [GitHub/pyramidxc/ai-engine](https://github.com/pyramidxc/ai-engine)

**Issues**: Report bugs and feature requests via GitHub Issues

---
