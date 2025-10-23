# Architecture

## System Overview

The AI Engine is a FastAPI-based service that performs sophisticated cybersecurity analysis through a 7-stage attack path generation system. It uses advanced context threading to maintain logical continuity across all stages while incorporating intelligent continuity validation.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                  FastAPI Application                 │
│                   (Port 8000)                        │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    ┌───▼────┐    ┌───▼────┐    ┌───▼────┐
    │ POST   │    │ GET    │    │ Health │
    │/analyze│    │/status │    │ /ready │
    └────┬───┘    └────────┘    └────────┘
         │
    ┌────▼────────────────────────────┐
    │  CompleteAnalyzer Service        │
    │  (Orchestration & Context)       │
    └────┬────────────────────┬────────┘
         │                    │
    ┌────▼──────────┐   ┌────▼──────────────────┐
    │  LLMClient    │   │ ContinuityValidator   │
    │  (OpenAI API) │   │ (Validation Logic)    │
    └───────────────┘   └──────────────────────┘
         │
    ┌────▼────────────────────────────┐
    │   AttackContext               │
    │   (Shared State Threading)    │
    └───────────────────────────────┘
```

## Core Components

### 1. FastAPI Application (`app/main.py`)

**Purpose**: HTTP request/response handling

**Endpoints**:
- `POST /analyze` - Initiate security analysis
- `GET /status` - System status
- `GET /ready` - Health check

**Configuration**: 
- Loaded from `app/config.py`
- Environment variables via `.env`
- CORS headers for cross-origin requests

### 2. CompleteAnalyzer Service (`app/services/complete_analyzer.py`)

**Purpose**: Orchestrates 7-stage generation with context threading

**Key Methods**:
- `analyze(request)` → CompleteAnalysisResponse
  - Validates input
  - Generates all 7 stages
  - Runs continuity validation
  - Returns comprehensive response

- `_generate_attack_path_with_continuity()` → List[StageAnalysis]
  - Sequential 7-stage LLM generation
  - Accumulates context through AttackContext
  - Parses and validates each stage

- `_extract_artifact_name(content, stage_index)` → Optional[str]
  - 4-priority fallback strategy
  - Code blocks → Explicit → Uploads → References

- `_parse_stage_response(response_text, stage_index)` → StageAnalysis
  - Parses LLM markdown output
  - Extracts all fields (techniques, findings, tools, etc.)
  - Calls artifact extraction

- `_update_stage_artifacts(context, primary_path)`
  - Populates stage_artifacts dict
  - Tracks artifact usage across 7 stages

**Data Flow**:
```
User Request
    ↓
Validate Input
    ↓
Create AttackContext
    ↓
Stage 1: Reconnaissance (context empty)
    ↓
Stage 2: Weaponization (context + stage 1)
    ↓
Stage 3: Delivery (context + stages 1-2)
    ↓
[... stages 4-7 similar pattern ...]
    ↓
Parse all stages
    ↓
Run ContinuityValidator
    ↓
Return CompleteAnalysisResponse
```

### 3. LLMClient (`app/services/llm_client.py`)

**Purpose**: OpenAI API integration

**Methods**:
- `generate(prompt, temperature, max_tokens)` → str
  - Sends requests to OpenAI
  - Handles retries and errors
  - Logs token usage

**Configuration**:
- Model: `OPENAI_MODEL` (default: gpt-4o-mini)
- Temperature: 0.7 (balanced creativity/consistency)
- Max tokens: Per-stage limit
- Timeout: 30s per request

### 4. ContinuityValidator (`app/utils/continuity_validator.py`)

**Purpose**: Cross-stage coherence validation

**Validation Checks**:

1. **Artifact Continuity** (`_check_artifact_continuity`)
   - Validates Stage 2 payload referenced in Stages 3-7
   - Ensures weapon remains consistent
   - Returns: pass/warning/fail

2. **Vulnerability Continuity** (`_check_vulnerability_continuity`)
   - Validates CVE from Stage 1 flows through Stages 2-4
   - Ensures exploitation aligns with vuln
   - Returns: pass/warning/fail

3. **Technique Alignment** (`_check_technique_alignment`)
   - Validates MITRE ATT&CK techniques logical progression
   - Ensures techniques align with cyber kill chain
   - Returns: pass/warning/fail

4. **Tool Consistency** (`_check_tool_consistency`)
   - Validates compatible tool usage across stages
   - Ensures tool chains make sense
   - Returns: pass/warning/fail

**Output**:
```python
{
    "is_valid": bool,
    "total_checks": int,
    "passes": List[str],
    "warnings": List[str],
    "stage_artifacts": Dict[int, Optional[str]]
}
```

### 5. Data Models (`app/models/`)

**AttackContext** (`attack_context.py`)
- Shared state threaded through all 7 stages
- Accumulates outputs for context
- Tracks artifact names per stage
- Properties:
  - `initial_target` - Starting input
  - `stage_outputs` - Dict[int, StageAnalysis]
  - `stage_artifacts` - Dict[int, Optional[str]]

**CompleteAnalysisResponse** (`complete_analysis.py`)
- Final API response structure
- Contains all 7 stage analyses
- Includes validation_report
- Properties:
  - `primary_path` - Ordered stages 1-7
  - `validation_report` - Continuity validation results
  - `model_used` - Which GPT model processed request
  - `total_tokens` - Token usage summary

### 6. Core Prompts (`app/core/prompts.py`)

**Purpose**: Stage-specific LLM prompts

**Stages** (with example prompts):
1. **Reconnaissance** - Target analysis, vulnerability research
2. **Weaponization** - Exploit creation, payload development
3. **Delivery** - Distribution method planning
4. **Exploitation** - Attack execution strategy
5. **Installation** - Persistence mechanisms
6. **Command & Control** - C2 communication setup
7. **Actions on Objectives** - Post-exploitation goals

Each prompt:
- References prior stages in context
- Specifies output format (markdown)
- Includes constraints and guidelines
- Optimized for consistency

### 7. Configuration (`app/config.py`)

**Settings**:
- `DEBUG` - Debug mode (bool)
- `LOG_LEVEL` - Logging level (DEBUG/INFO/WARNING/ERROR)
- `OPENAI_API_KEY` - API authentication
- `OPENAI_MODEL` - Model selection
- `REQUEST_TIMEOUT_SECONDS` - Request timeout
- `MAX_TOKENS_PER_STAGE` - Token limits
- `TEMPERATURE` - LLM temperature (creativity)

## Data Flow

### Request Processing

```
1. User sends POST /analyze
   ├─ Headers: Content-Type: application/json
   └─ Body: { target: "...", context: "..." }

2. FastAPI validates request
   ├─ Pydantic validation
   └─ Rejects if schema invalid

3. CompleteAnalyzer.analyze()
   ├─ Creates AttackContext
   ├─ Builds 7 stage prompts
   ├─ Calls LLMClient 7 times
   │  ├─ Stage 1 (no context)
   │  ├─ Stage 2 (+ stage 1)
   │  ├─ Stage 3 (+ stages 1-2)
   │  └─ ... stages 4-7 similar
   ├─ Parses all responses
   ├─ Extracts artifacts
   ├─ Runs validation
   └─ Returns response

4. Response delivered to client
   ├─ Headers: Content-Type: application/json
   └─ Body: CompleteAnalysisResponse (JSON)
```

### Context Threading

Each stage LLM call receives accumulated context:

```
Stage 1 Prompt
├─ Input: target description
└─ Output: reconnaissance findings

Stage 2 Prompt
├─ Input: target + stage 1 findings
└─ Output: weaponization strategy

Stage 3 Prompt
├─ Input: target + stages 1-2 findings
└─ Output: delivery method

[Pattern continues through Stage 7]

Final Output: Coherent 7-stage attack path
```

## Artifact Extraction Strategy

4-priority fallback ensures high accuracy:

```
Priority 1: Code Blocks (Highest Confidence)
├─ msfvenom -o <filename>
├─ curl -O <filename>
├─ wget <filename>
├─ PowerShell -O <filename>
└─ Common exploit frameworks

Priority 2: Explicit Naming (High Confidence)
├─ "named: <filename>"
├─ "created: <filename>"
├─ "called: <filename>"
└─ Explicit mention patterns

Priority 3: Upload/Transfer (Medium Confidence)
├─ "upload <filename>"
├─ "scp <filename>"
├─ "copy <filename>"
└─ Transfer patterns

Priority 4: Prior References (Lower Confidence)
├─ "from stage <n>"
├─ "the payload created earlier"
├─ "using <artifact-from-prior>"
└─ Reference patterns
```

## Validation Pipeline

```
Parsed Stages
    ↓
Artifact Continuity
├─ Stage 2 artifact exists?
├─ Referenced in stages 3+?
└─ Consistent naming?
    ↓
Vulnerability Continuity
├─ CVE from stage 1?
├─ Exploited in stage 4?
├─ Logically sound?
└─ Tool matches?
    ↓
Technique Alignment
├─ Valid MITRE ATT&CK?
├─ Progression logical?
├─ Kill chain aligned?
└─ Stage appropriate?
    ↓
Tool Consistency
├─ Tools compatible?
├─ Environment match?
├─ Availability correct?
└─ Version compatible?
    ↓
Validation Report
└─ is_valid: true/false
```

## Technology Stack

### Core Framework
- **FastAPI 0.100+**: Modern async web framework
- **Pydantic 2.0+**: Data validation with Python types
- **Python 3.10+**: Runtime with async/await

### External Services
- **OpenAI API**: GPT-4o-mini LLM model
- **OpenAI Python Client**: SDK for API integration

### Development Tools
- **Pytest**: Testing framework
- **Black**: Code formatter
- **Ruff**: Linter
- **Mypy**: Type checker (optional)

### Deployment
- **Docker**: Container orchestration
- **Docker Compose**: Multi-container management
- **Gunicorn**: Production WSGI server

## Performance Characteristics

### Typical Request Timeline
- Input validation: 10ms
- LLM generation (7 stages): 10-20s (90% of total time)
- Parsing & validation: 500ms
- Response serialization: 10ms
- **Total: 10-20 seconds**

### Token Usage
- Per-request: 5-15k tokens typically
- Per-stage average: 1-2k tokens
- Input tokens: 30-40% of total
- Output tokens: 60-70% of total

### Scalability
- Single instance: ~3-5 concurrent requests
- CPU: Minimal (mostly I/O waiting)
- Memory: ~300MB base + 100MB per request
- Network: Limited by OpenAI rate limits

## Security Architecture

### API Key Management
- Stored in `.env` file (never committed)
- Loaded into environment at runtime
- Never logged or exposed in errors
- See [SECURITY.md](../SECURITY.md)

### Input Validation
- Pydantic models enforce schema
- Max length limits on all fields
- Type checking on all inputs
- Sanitization before LLM calls

### Output Handling
- No sensitive data in logs
- Error messages generic (no internal details)
- Response includes only necessary data
- No PII preserved between requests

### Rate Limiting
- Implement at API gateway level
- Per-IP rate limits (recommended)
- Per-key limits (future)
- Graceful degradation on limits

## Extension Points

### Adding New Stages
1. Add stage prompt in `app/core/prompts.py`
2. Extend `_generate_attack_path_with_continuity()` loop
3. Update context threading logic
4. Extend `StageAnalysis` if needed
5. Add validation rule in `ContinuityValidator`

### Changing LLM Models
1. Update `OPENAI_MODEL` in config
2. Adjust token limits if needed
3. Test prompt effectiveness
4. Update documentation

### Custom Validation Rules
1. Extend `ContinuityValidator` with new `_check_*` method
2. Call from `validate()` orchestrator
3. Add results to report dict
4. Document in validation section

### Alternative LLM Providers
1. Create new service: `LlamaClient`, `AnthropicClient`, etc.
2. Implement same interface as `LLMClient`
3. Update `CompleteAnalyzer` to use new provider
4. Test prompt compatibility
5. Document configuration

## Future Roadmap

### Planned Improvements
- [ ] Multi-provider LLM support (Anthropic, Llama)
- [ ] Prompt optimization pipeline
- [ ] Response caching layer
- [ ] Database persistence
- [ ] Web UI frontend
- [ ] Advanced analytics dashboard
- [ ] Batch analysis mode
- [ ] Custom validation rules engine

### Scalability Enhancements
- [ ] Horizontal scaling with load balancer
- [ ] Request queuing system
- [ ] Cache layer (Redis)
- [ ] Async job processing
- [ ] Database integration

### Operational Features
- [ ] Monitoring/alerting integration
- [ ] Audit logging
- [ ] Usage analytics
- [ ] Cost tracking
- [ ] Performance metrics

## Related Documentation

- [API Reference](API.md) - Endpoint documentation
- [Development Guide](DEVELOPMENT.md) - Local setup
- [Deployment Guide](DEPLOYMENT.md) - Production procedures
- [Operational Runbook](RUNBOOK.md) - Day-to-day operations
- [Architecture Decisions](adr/0002-continuity-validation-design.md)

---

Last updated: 2024
Maintained by: AI Engine Team
