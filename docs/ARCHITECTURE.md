# Architecture Documentation

## Overview

This document describes the clean architecture implementation of the Attack Path Engine, following modern Python best practices and separation of concerns principles.

## Architecture Principles

### 1. **Separation of Concerns**

Each layer has a single, well-defined responsibility:

- **Presentation Layer**: HTTP routing and request/response handling
- **Business Logic Layer**: Core domain logic and orchestration
- **Infrastructure Layer**: External integrations (LLM API calls)
- **Data Layer**: Data models and validation

### 2. **Dependency Direction**

Dependencies flow inward:

```bash
HTTP Routes → Services → Core Logic
     ↓            ↓           ↓
  Models ←────────────────────┘
```

### 3. **Testability**

Each component can be tested in isolation with clear interfaces and dependencies.

## Project Structure

```bash
app/
├── main.py              # FastAPI routes (Presentation Layer)
├── config.py            # Configuration management
├── models/              # Data models (Data Layer)
│   ├── __init__.py
│   ├── host.py         # InputHost model
│   └── analysis.py     # AttackPathResponse model
├── services/            # Business logic (Business Layer)
│   ├── __init__.py
│   ├── analyzer.py     # Attack path analysis orchestration
│   └── llm_client.py   # LLM API client (Infrastructure)
└── core/                # Domain logic (Core Layer)
    ├── __init__.py
    └── prompts.py      # Prompt building logic
```

## Component Responsibilities

### 1. Presentation Layer (`main.py`)

**Purpose**: Handle HTTP requests and responses

**Responsibilities**:

- Define API endpoints
- Request validation (via Pydantic)
- Response formatting
- Error handling at HTTP level

**Code**: ~45 lines (reduced from 100 lines)

```python
@app.post("/attack-path", response_model=AttackPathResponse)
async def attack_path(host: InputHost):
    try:
        return await analyzer.analyze(host)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
```

### 2. Business Logic Layer (`services/`)

#### `services/analyzer.py`

**Purpose**: Orchestrate the attack path analysis workflow

**Responsibilities**:

- Coordinate between prompt building and LLM calls
- Business logic validation
- Transform LLM responses into domain objects

**Dependencies**: LLMClient, PromptBuilder, Models

#### `services/llm_client.py`

**Purpose**: Abstract LLM API interactions

**Responsibilities**:

- Handle all LiteLLM API calls
- Manage LLM configuration
- Parse LLM responses
- Handle LLM-specific errors

**Dependencies**: LiteLLM library, Configuration

### 3. Core Domain Layer (`core/`)

#### `core/prompts.py`

**Purpose**: Centralize prompt engineering logic

**Responsibilities**:

- Build structured prompts from domain data
- Maintain prompt templates
- Encapsulate domain knowledge

**Dependencies**: Models only (no external services)

### 4. Data Layer (`models/`)

#### `models/host.py`

**Purpose**: Define input data structures

**Responsibilities**:

- Validate host input data
- Provide type safety
- Document expected fields

#### `models/analysis.py`

**Purpose**: Define output data structures

**Responsibilities**:

- Structure analysis results
- Enforce response format
- Provide API contract

### 5. Configuration (`config.py`)

**Purpose**: Centralize all configuration management

**Responsibilities**:

- Load environment variables
- Provide type-safe settings access
- Validate required configuration

## Design Patterns

### 1. **Dependency Injection**

Services are instantiated at application startup and injected where needed:

```python
analyzer = AttackPathAnalyzer()  # Instantiated once

@app.post("/attack-path")
async def attack_path(host: InputHost):
    return await analyzer.analyze(host)  # Injected dependency
```

### 2. **Single Responsibility Principle**

Each class has one reason to change:

- `PromptBuilder`: Prompts change
- `LLMClient`: LLM API changes
- `AttackPathAnalyzer`: Business logic changes
- Route handlers: API contract changes

### 3. **Open/Closed Principle**

Easy to extend without modifying existing code:

- Add new analysis types by creating new analyzers
- Add new LLM providers by configuring LiteLLM
- Add new prompt strategies by extending PromptBuilder

## Data Flow

### Request Flow

```bash
1. HTTP Request → FastAPI Route Handler
2. Route Handler → AttackPathAnalyzer.analyze()
3. Analyzer → PromptBuilder.build_prompt()
4. Analyzer → LLMClient.complete()
5. LLMClient → LiteLLM API → External LLM
6. LLM Response → LLMClient (parse JSON)
7. LLMClient → Analyzer (return parsed data)
8. Analyzer → Validate and build AttackPathResponse
9. Route Handler → Return HTTP response
```

### Error Flow

```bash
1. Exception occurs in any layer
2. Exception propagates up to route handler
3. Route handler catches and converts to HTTPException
4. FastAPI converts to proper HTTP error response
```

## Benefits of This Architecture

### 1. **Maintainability**

- Clear file organization
- Easy to locate specific functionality
- Reduced cognitive load

### 2. **Testability**

```python
# Test prompt building without LLM calls
def test_prompt_builder():
    builder = PromptBuilder()
    prompt = builder.build_attack_analysis_prompt(mock_host)
    assert "vulnerability" in prompt.lower()

# Test analyzer with mocked LLM
async def test_analyzer():
    analyzer = AttackPathAnalyzer()
    analyzer.llm_client = MockLLMClient()  # Inject mock
    result = await analyzer.analyze(mock_host)
    assert result.risk_level == "High"
```

### 3. **Extensibility**

Easy to add features:

- New analysis types (compliance, threat modeling)
- Multiple LLM providers
- Caching layer
- Rate limiting
- Background processing

### 4. **Readability**

- Self-documenting structure
- Clear imports show dependencies
- Type hints improve IDE support

## Migration to Async Architecture

This clean architecture makes future async migration straightforward:

### Current (Synchronous)

```python
class AttackPathAnalyzer:
    async def analyze(self, host: InputHost) -> AttackPathResponse:
        # Synchronous orchestration, async LLM call
        return result
```

### Future (Fully Async with SQS)

```python
class AttackPathAnalyzer:
    async def analyze(self, host: InputHost, job_id: str) -> None:
        # Async orchestration
        result = await self._perform_analysis(host)
        
        # Send to SQS
        await self.queue_client.send_result(job_id, result)
        
        # Trigger webhook
        await self.webhook_client.notify(job_id, result)
```

**No changes required to**:

- Prompt building logic
- Data models
- LLM client interface

**Changes required**:

- Add queue client to analyzer
- Add webhook client to analyzer
- Change return type to None (fire-and-forget)
- Add job tracking in routes

## Performance Characteristics

### Current Implementation

- **Latency**: 2-4 seconds (LLM call dominant)
- **Concurrency**: Limited by synchronous orchestration
- **Scalability**: Vertical scaling only

### After Full Async Migration

- **Latency**: <100ms (immediate job queuing)
- **Concurrency**: Unlimited (background processing)
- **Scalability**: Horizontal scaling with SQS workers

## Code Metrics

### Before Refactoring

- **Files**: 1 (main.py)
- **Lines**: 100
- **Concerns**: Mixed (7+ responsibilities)
- **Testability**: Low (hard to mock LLM)

### After Refactoring

- **Files**: 9 (organized by concern)
- **Lines**: ~120 total (more documentation)
- **Concerns**: Separated (1 responsibility per file)
- **Testability**: High (clear interfaces)

## Next Steps

1. **Add Unit Tests**: Test each component in isolation
2. **Add Integration Tests**: Test full flow with real LLM
3. **Add Caching**: Cache LLM responses for identical inputs
4. **Add Monitoring**: Log analysis requests and performance
5. **Implement Async**: Add SQS + Lambda architecture
6. **Add Authentication**: Secure the API endpoints
7. **Add Rate Limiting**: Prevent abuse

## Conclusion

This architecture provides a solid foundation for:

- ✅ Clean, maintainable code
- ✅ Easy testing at all levels
- ✅ Simple extension with new features
- ✅ Straightforward migration to async patterns
- ✅ Professional production-ready structure
