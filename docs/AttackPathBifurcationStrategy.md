# Attack Path Bifurcation Strategy

**Document Version:** 1.0  
**Date:** October 13, 2025  
**Status:** Planning Phase - Not Yet Implemented

---

## Executive Summary

This document outlines the strategy for implementing **attack path bifurcation analysis** - a feature that identifies alternative attack paths (branches) from intermediate stages of an existing cyber kill chain attack path.

**Key Concept:** After generating a primary attack path (stages 1→2→3→4→5→6→7), analyze each stage to identify decision points where an attacker could pursue alternative techniques, then generate continuation paths from those bifurcation points.

---

## Table of Contents

1. [Core Concept](#core-concept)
2. [Current State vs Future State](#current-state-vs-future-state)
3. [Bifurcation Logic](#bifurcation-logic)
4. [Technical Approach](#technical-approach)
5. [Data Models](#data-models)
6. [LLM Prompting Strategy](#llm-prompting-strategy)
7. [Response Structure](#response-structure)
8. [API Design](#api-design)
9. [Implementation Phases](#implementation-phases)
10. [Cost and Performance Considerations](#cost-and-performance-considerations)
11. [Use Cases](#use-cases)
12. [Example Scenario](#example-scenario)

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
- Structured response with recommendations

**Example Output:**
```json
{
  "attack_path": [
    {
      "stage": "Reconnaissance",
      "technique": "Port scanning",
      "description": "...",
      "mitre_attack_id": "T1046"
    },
    // ... 6 more stages
  ],
  "summary": "Attack path analysis",
  "recommendations": ["Fix Docker API", "..."]
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

### Three-Pass System

#### **Pass 1: Primary Path Generation**
*Uses existing implementation*

```
Input: Host parameters (50+ fields)
Process: Build dynamic prompt → Call LLM → Parse response
Output: Primary attack path (7 stages)
```

**Existing code handles this** - no changes needed.

---

#### **Pass 2: Bifurcation Detection**

```
Input: Primary attack path from Pass 1 + Host parameters
Process: For each stage, analyze context and identify alternatives
Output: List of bifurcation points with decision context
```

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
      "alternatives": [
        {
          "id": "B1",
          "reason": "Jenkins visible and unauthenticated",
          "technique": "Pivot to Jenkins exploitation",
          "probability": "medium"
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

---

#### **Pass 3: Alternative Path Generation**

```
Input: Each bifurcation point from Pass 2 + Host parameters
Process: For each alternative, generate continuation through remaining kill chain
Output: Complete branch paths from bifurcation points
```

**LLM Prompt Strategy (per bifurcation):**
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
  "from_stage": 3,
  "continuation_path": [
    {
      "stage": "Privilege Escalation",
      "technique": "Jenkins Groovy Script Console RCE",
      "description": "Execute arbitrary code via unauthenticated /script endpoint",
      "mitre_attack_id": "T1059.007"
    },
    // ... stages 5-7
  ]
}
```

---

## Data Models

### Enhanced Response Models

```python
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class AttackStage(BaseModel):
    """Single stage in attack path (existing model)"""
    stage: str
    technique: str
    description: str
    mitre_attack_id: Optional[str] = None
    tools: Optional[List[str]] = None
    indicators: Optional[List[str]] = None
    detection_difficulty: Optional[str] = None

class AlternativeBranch(BaseModel):
    """Alternative path from a bifurcation point"""
    branch_id: str = Field(description="Unique identifier for this branch (e.g., 'B1', 'B2')")
    technique: str = Field(description="Alternative technique/target")
    reason: str = Field(description="Why this alternative exists")
    probability: str = Field(description="Likelihood: high/medium/low")
    continuation_path: List[AttackStage] = Field(description="Remaining kill chain stages for this branch")

class Bifurcation(BaseModel):
    """Decision point where attack path can branch"""
    stage_index: int = Field(description="Index in primary path where bifurcation occurs (0-based)")
    stage_name: str = Field(description="Name of the kill chain stage")
    attacker_context: str = Field(description="What the attacker has gained at this point")
    decision_point: str = Field(description="Why multiple paths exist here")
    branches: List[AlternativeBranch] = Field(description="Alternative continuation paths")

class AttackGraph(BaseModel):
    """Visual representation of attack tree"""
    total_paths: int = Field(description="Total number of unique paths (primary + branches)")
    total_stages: int = Field(description="Total stages across all paths")
    bifurcation_count: int = Field(description="Number of decision points")
    graph_ascii: Optional[str] = Field(None, description="ASCII art representation")
    graph_json: Optional[Dict] = Field(None, description="Machine-readable graph structure")

class EnhancedAttackPathResponse(BaseModel):
    """Complete response with bifurcation analysis"""
    
    # Primary path (existing fields)
    primary_path: List[AttackStage] = Field(description="Main attack path through kill chain")
    summary: str = Field(description="Overall attack path summary")
    recommendations: List[str] = Field(description="Security recommendations")
    
    # Bifurcation analysis (new fields)
    bifurcations: Optional[List[Bifurcation]] = Field(None, description="Decision points with alternatives")
    attack_graph: Optional[AttackGraph] = Field(None, description="Visual attack tree representation")
    
    # Metadata
    generated_prompt: Optional[str] = Field(None, description="Primary path prompt (if include_prompt=true)")
    prompt_sections: Optional[int] = Field(None, description="Number of sections in primary prompt")
    analysis_depth: str = Field("standard", description="'standard' or 'bifurcated'")
```

---

## LLM Prompting Strategy

### Pass 1: Primary Path (Existing)

**File:** `app/core/prompts.py` - `build_attack_analysis_prompt()`

**No changes needed** - uses existing dynamic prompt builder.

---

### Pass 2: Bifurcation Detection (New)

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

### Pass 3: Branch Generation (New)

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
  "primary_path": [
    {
      "stage": "Reconnaissance",
      "technique": "Port Scanning",
      "description": "Scan target to identify open ports and services",
      "mitre_attack_id": "T1046",
      "tools": ["nmap", "masscan"],
      "detection_difficulty": "low"
    },
    {
      "stage": "Initial Access",
      "technique": "Exploit Unauthenticated Docker API",
      "description": "Connect to Docker API on port 2375 without authentication",
      "mitre_attack_id": "T1190",
      "tools": ["docker-cli", "metasploit"],
      "detection_difficulty": "medium"
    },
    {
      "stage": "Execution",
      "technique": "Deploy Malicious Container",
      "description": "Create privileged container with host filesystem mounted",
      "mitre_attack_id": "T1610",
      "tools": ["docker"],
      "detection_difficulty": "medium"
    },
    // ... stages 4-7
  ],
  
  "summary": "Attack path exploiting unauthenticated Docker API...",
  
  "recommendations": [
    "Enable Docker TLS authentication",
    "Restrict Docker API to localhost only",
    "Implement network segmentation"
  ],
  
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
            {
              "stage": "Privilege Escalation",
              "technique": "Jenkins Groovy Script Console RCE",
              "description": "Execute arbitrary code via /script endpoint",
              "mitre_attack_id": "T1059.007",
              "tools": ["curl", "jenkins-cli"],
              "detection_difficulty": "low"
            },
            // ... stages 5-7
          ]
        },
        {
          "branch_id": "B2",
          "technique": "Pivot to MySQL Database",
          "reason": "MySQL accessible with default credentials from container",
          "probability": "medium",
          "continuation_path": [
            {
              "stage": "Privilege Escalation",
              "technique": "MySQL UDF Code Execution",
              "description": "Load malicious UDF to execute OS commands",
              "mitre_attack_id": "T1059.004",
              "tools": ["mysql-client", "lib_mysqludf_sys"],
              "detection_difficulty": "high"
            },
            // ... stages 5-7
          ]
        }
      ]
    },
    {
      "stage_index": 4,
      "stage_name": "Persistence",
      "attacker_context": "Attacker has root access on host system",
      "decision_point": "Multiple persistence mechanisms available",
      "branches": [
        {
          "branch_id": "B3",
          "technique": "Alternative Persistence via Service Account",
          "reason": "Multiple service accounts with sudo privileges",
          "probability": "medium",
          "continuation_path": [
            // ... stages 5-7 using service account approach
          ]
        }
      ]
    }
  ],
  
  "attack_graph": {
    "total_paths": 4,
    "total_stages": 28,
    "bifurcation_count": 2,
    "graph_ascii": "
Stage 1: Reconnaissance
   |
Stage 2: Initial Access (Docker)
   |
Stage 3: Execution (Container)
   |
   ├─── [Primary] Stage 4: Privilege Escalation (Container Escape)
   |       |
   |       Stage 5-7: ... (original path)
   |
   ├─── [B1] Stage 4: Privilege Escalation (Jenkins RCE)
   |       |
   |       Stage 5-7: ... (Jenkins branch)
   |
   └─── [B2] Stage 4: Privilege Escalation (MySQL UDF)
           |
           Stage 5-7: ... (MySQL branch)
    ",
    "graph_json": {
      "nodes": [
        {"id": "S1", "stage": "Reconnaissance", "technique": "Port Scanning"},
        {"id": "S2", "stage": "Initial Access", "technique": "Docker API"},
        {"id": "S3", "stage": "Execution", "technique": "Malicious Container", "bifurcation": true},
        {"id": "S4-primary", "stage": "Privilege Escalation", "technique": "Container Escape", "branch": "primary"},
        {"id": "S4-B1", "stage": "Privilege Escalation", "technique": "Jenkins RCE", "branch": "B1"},
        {"id": "S4-B2", "stage": "Privilege Escalation", "technique": "MySQL UDF", "branch": "B2"}
        // ... more nodes
      ],
      "edges": [
        {"from": "S1", "to": "S2"},
        {"from": "S2", "to": "S3"},
        {"from": "S3", "to": "S4-primary", "type": "primary"},
        {"from": "S3", "to": "S4-B1", "type": "branch"},
        {"from": "S3", "to": "S4-B2", "type": "branch"}
        // ... more edges
      ]
    }
  },
  
  "generated_prompt": "...",
  "prompt_sections": 7,
  "analysis_depth": "bifurcated"
}
```

---

## API Design

### Option 1: Query Parameter (Recommended)

**Extend existing endpoint with backward compatibility**

```python
@app.post("/attack-path", response_model=EnhancedAttackPathResponse)
async def generate_attack_path(
    host: InputHost,
    include_prompt: bool = Query(default=True, description="Include generated prompt in response"),
    include_bifurcations: bool = Query(default=False, description="Analyze and include alternative attack paths")
):
    """
    Generate attack path analysis with optional bifurcation detection.
    
    Query Parameters:
    - include_prompt: Return the LLM prompt (debugging/transparency)
    - include_bifurcations: Perform multi-pass analysis to find alternative paths
    
    With bifurcations=false (default):
      - Returns standard single-path analysis
      - Fast response (1 LLM call)
      - Backward compatible with existing clients
    
    With bifurcations=true:
      - Returns enhanced analysis with branches
      - Slower response (1 + 1 + N LLM calls)
      - Provides comprehensive attack coverage
    """
    
    if include_bifurcations:
        # Three-pass analysis
        result = await analyzer.analyze_with_bifurcations(host, include_prompt)
    else:
        # Standard single-path analysis (existing functionality)
        result = await analyzer.analyze(host, include_prompt)
    
    return result
```

**Benefits:**
- ✅ Backward compatible (existing clients unaffected)
- ✅ Single endpoint, easy to discover
- ✅ Progressive enhancement
- ✅ Clear separation of concerns

---

### Option 2: Separate Endpoint

**Add new endpoint for advanced analysis**

```python
@app.post("/attack-path", response_model=AttackPathResponse)
async def generate_attack_path(host: InputHost, include_prompt: bool = True):
    """Standard single-path analysis (existing endpoint)"""
    return await analyzer.analyze(host, include_prompt)

@app.post("/attack-graph", response_model=EnhancedAttackPathResponse)
async def generate_attack_graph(host: InputHost, include_prompt: bool = True):
    """Advanced multi-path analysis with bifurcations"""
    return await analyzer.analyze_with_bifurcations(host, include_prompt)
```

**Benefits:**
- ✅ Clear semantic difference
- ✅ Can have different rate limits/pricing
- ✅ Easier to version independently
- ❌ More endpoints to maintain

---

### Recommended Approach

**Use Option 1 (Query Parameter)** for simplicity and backward compatibility.

**Example API Calls:**

```bash
# Standard analysis (current behavior)
curl -X POST "http://localhost:8000/attack-path?include_bifurcations=false" \
  -H "Content-Type: application/json" \
  -d @example_request_enhanced.json

# Enhanced analysis with bifurcations
curl -X POST "http://localhost:8000/attack-path?include_bifurcations=true" \
  -H "Content-Type: application/json" \
  -d @example_request_enhanced.json
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)

**Goal:** Add data models and basic structure

**Tasks:**
1. Create new Pydantic models in `app/models/analysis.py`:
   - `AlternativeBranch`
   - `Bifurcation`
   - `AttackGraph`
   - `EnhancedAttackPathResponse`

2. Add new prompt builders in `app/core/prompts.py`:
   - `build_bifurcation_analysis_prompt()`
   - `build_branch_continuation_prompt()`

3. Update `app/services/analyzer.py`:
   - Add `analyze_with_bifurcations()` method (stub)

4. Update `app/main.py`:
   - Add `include_bifurcations` query parameter
   - Wire up new analyzer method

**Deliverable:** API accepts `include_bifurcations` parameter (returns empty bifurcations array)

---

### Phase 2: Bifurcation Detection (Week 2)

**Goal:** Implement Pass 2 (identify bifurcation points)

**Tasks:**
1. Implement `build_bifurcation_analysis_prompt()` fully
2. Add LLM call for bifurcation detection in analyzer
3. Parse bifurcation JSON response
4. Return bifurcations in response (without continuation paths yet)

**Testing:**
- Test with `example_request_enhanced.json`
- Verify bifurcations are identified at stages 2-3 (Docker → Jenkins/MySQL)
- Validate JSON parsing

**Deliverable:** API returns identified bifurcation points with alternative descriptions

---

### Phase 3: Branch Generation (Week 3)

**Goal:** Implement Pass 3 (generate continuation paths)

**Tasks:**
1. Implement `build_branch_continuation_prompt()` fully
2. For each bifurcation/alternative, call LLM to generate continuation
3. Parse continuation path responses
4. Attach continuation paths to bifurcation branches
5. Handle LLM errors gracefully (continue with partial results)

**Testing:**
- Test complete three-pass flow
- Verify continuation paths are realistic
- Validate MITRE ATT&CK mappings

**Deliverable:** Full bifurcation analysis with complete branch paths

---

### Phase 4: Graph Visualization (Week 4)

**Goal:** Add attack graph representation

**Tasks:**
1. Implement `AttackGraph` builder:
   - Count total paths
   - Generate ASCII tree representation
   - Build JSON graph structure (nodes/edges)

2. Add graph to response

3. Create helper functions for path traversal

4. Update documentation

**Testing:**
- Generate graphs for various scenarios
- Validate ASCII output renders correctly
- Test JSON structure for frontend consumption

**Deliverable:** Complete bifurcation feature with visualization

---

### Phase 5: Optimization & Polish (Week 5)

**Goal:** Performance and quality improvements

**Tasks:**
1. Add caching for repeated bifurcation analyses
2. Implement parallel LLM calls for branch generation
3. Add probability scoring refinement
4. Optimize prompt token usage
5. Add comprehensive error handling
6. Write unit tests
7. Update all documentation
8. Create example notebooks/scripts

**Deliverable:** Production-ready bifurcation analysis

---

## Cost and Performance Considerations

### LLM Call Analysis

**Standard Analysis (current):**
- 1 LLM call for primary path
- ~2-4K tokens input, ~1-2K tokens output
- Response time: 5-15 seconds
- Cost: ~$0.01-0.03 per request (GPT-4)

**Bifurcated Analysis (new):**
- 1 LLM call for primary path (same as above)
- 1 LLM call for bifurcation detection (~3-5K tokens input, ~1K output)
- N LLM calls for branch generation (N = number of alternatives)
  - Each branch: ~3-5K tokens input, ~1-2K tokens output

**Example with 3 bifurcations (5 total alternatives):**
- Total LLM calls: 1 + 1 + 5 = 7 calls
- Total tokens: ~40-60K tokens
- Response time: 30-90 seconds (sequential) or 15-30 seconds (parallel)
- Cost: ~$0.10-0.25 per request (GPT-4)

### Optimization Strategies

1. **Parallel Branch Generation**: Generate all branches simultaneously
2. **Caching**: Cache bifurcation detection for similar hosts
3. **Streaming**: Stream results as they're generated (primary → bifurcations → branches)
4. **Model Selection**: Use faster/cheaper models for bifurcation detection (GPT-3.5)
5. **Max Branches**: Limit number of branches per bifurcation (e.g., top 3)
6. **Smart Prompting**: Reuse context across branch generation calls

### Performance Targets

- **Standard Analysis**: < 15 seconds, < $0.05
- **Bifurcated Analysis**: < 45 seconds, < $0.20
- **Max Bifurcations**: 5 decision points
- **Max Branches per Bifurcation**: 3 alternatives

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

### Expected Attack Graph

```
Stage 1: Reconnaissance
   |
Stage 2: Initial Access (Docker API)
   |
Stage 3: Execution (Container) *** BIFURCATION ***
   |
   ├─── [Primary Path] Stage 4-7: Container Escape → Root → Exfiltration
   |
   ├─── [Branch B1] Stage 4-7: Jenkins RCE → Plugin Backdoor → Source Code Theft
   |
   └─── [Branch B2] Stage 4-7: MySQL UDF → Trigger Backdoor → Database Dump

Total Paths: 3
Bifurcations: 1 major decision point
Criticality: HIGH - Multiple viable attack vectors from single entry point
```

---

## Success Criteria

### Feature Complete When:

✅ API accepts `include_bifurcations` query parameter  
✅ Primary path generation unchanged (backward compatibility)  
✅ Bifurcation detection identifies 2+ decision points for `example_request_enhanced.json`  
✅ Each bifurcation includes 2-3 viable alternatives  
✅ Continuation paths are complete (cover remaining kill chain stages)  
✅ Attack graph visualization generated (ASCII + JSON)  
✅ Response time < 60 seconds for bifurcated analysis  
✅ All LLM responses properly validated and error-handled  
✅ Documentation updated (README, TECHNICAL_SPECIFICATION, USAGE)  
✅ Test scenarios created for bifurcation analysis  
✅ Unit tests written for new components  

---

## Open Questions

1. **Max Bifurcations**: Should we limit number of bifurcations detected? (Recommendation: max 5)

2. **Max Branches**: Should we limit alternatives per bifurcation? (Recommendation: max 3)

3. **Probability Threshold**: Should we filter out low-probability branches? (Recommendation: include all, let user filter)

4. **Visualization Format**: ASCII sufficient or need Mermaid/DOT output? (Recommendation: start with ASCII + JSON)

5. **Streaming**: Should results stream as generated? (Recommendation: defer to Phase 5)

6. **Caching**: Cache bifurcation analysis by host fingerprint? (Recommendation: yes, in Phase 5)

---

## Next Steps

1. **Review this strategy document** - validate approach with stakeholders
2. **Decide on API design** - confirm Query Parameter approach
3. **Set up development branch** - `feature/bifurcation-analysis`
4. **Begin Phase 1 implementation** - data models and scaffolding
5. **Create tracking issues** - one per phase for project management

---

## References

- MITRE ATT&CK Framework: https://attack.mitre.org/
- Cyber Kill Chain: https://www.lockheedmartin.com/en-us/capabilities/cyber/cyber-kill-chain.html
- Attack Trees: https://en.wikipedia.org/wiki/Attack_tree
- Current codebase: `/home/pyramid/workspace/reveald/ai-engine`

---

**Document Status:** ✅ Ready for Review  
**Next Action:** Stakeholder approval to begin Phase 1 implementation