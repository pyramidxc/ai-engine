# ADR 0002: Continuity Validation Design

Date: 2024-01-15

## Status

Accepted

## Context

The AI Engine performs 7-stage attack path analysis with context threading, where each stage receives outputs from previous stages to maintain logical continuity. However, without validation, there's no way to verify that the generated analysis maintains coherence across all stages.

Problems observed:
- Artifact names inconsistent across stages
- Vulnerability exploitation doesn't match initial reconnaissance
- MITRE ATT&CK techniques don't follow logical progression
- Tools referenced are incompatible with target environment

This impacts:
- User trust in analysis quality
- Ability to catch LLM hallucinations
- Confidence in generated attack paths
- Consistency across different runs

## Decision

Implement a multi-check continuity validation system (`ContinuityValidator`) that performs 4 independent validation checks on generated analysis:

1. **Artifact Continuity**: Verify Stage 2 payload is referenced consistently in Stages 3-5
2. **Vulnerability Continuity**: Verify CVE from Stage 1 is properly exploited in Stages 2-4
3. **Technique Alignment**: Verify MITRE ATT&CK techniques follow logical cyber kill chain progression
4. **Tool Consistency**: Verify tools used across stages are compatible and appropriate

The validator returns a structured report including:
- Overall validity status (true/false)
- Individual check results
- List of warnings found
- Complete artifact tracking

## Consequences

### Positive
- **Quality Assurance**: Catches inconsistencies automatically
- **Transparency**: Users see exactly what was validated
- **Debugging**: Warnings help identify LLM hallucinations
- **Confidence**: Valid reports indicate high-quality analysis
- **Extensible**: Easy to add new validation checks
- **Reusable**: Validator can be used in other projects
- **Pluggable**: Validation runs independently of generation

### Negative
- **Latency**: Adds 500ms-1s per request for validation
- **Complexity**: Additional code to maintain
- **False Positives**: May flag valid but unusual attack paths
- **Configuration**: Validation rules may need tuning per domain

### Mitigation
- Cache validation results for identical inputs
- Design checks to minimize false positives
- Document validation rules for users
- Allow disabling validation if needed

## Alternatives

### Alternative 1: No Validation
- **Pros**: Lower latency, simpler code
- **Cons**: No quality assurance, users can't trust results
- **Rejected**: Quality is critical for production use

### Alternative 2: Manual Review
- **Pros**: Most accurate validation
- **Cons**: Doesn't scale, too expensive
- **Rejected**: Can't review every request in real-time

### Alternative 3: Separate Validation Service
- **Pros**: Decoupled from main service
- **Cons**: Added latency, operational complexity
- **Rejected**: Built-in validation is simpler for MVP

### Alternative 4: LLM-Based Validation
- **Pros**: More sophisticated checking
- **Cons**: Another LLM call = double cost and latency
- **Rejected**: Rule-based validation is more cost-effective

## Implementation Details

### ContinuityValidator Class

```python
class ContinuityValidator:
    def __init__(self, context: AttackContext, stages: List[StageAnalysis]):
        self.context = context
        self.stages = stages
        
    def validate(self) -> Dict[str, Any]:
        """Run all validation checks."""
        passes = []
        warnings = []
        
        # Run all checks
        artifact_result = self._check_artifact_continuity()
        vuln_result = self._check_vulnerability_continuity()
        tech_result = self._check_technique_alignment()
        tool_result = self._check_tool_consistency()
        
        # Aggregate results
        is_valid = all([
            artifact_result["valid"],
            vuln_result["valid"],
            tech_result["valid"],
            tool_result["valid"]
        ])
        
        return {
            "is_valid": is_valid,
            "total_checks": 4,
            "passes": passes,
            "warnings": warnings,
            "stage_artifacts": self.context.stage_artifacts
        }
```

### Check Implementations

Each check is independent and returns pass/warning/fail:

**Artifact Continuity**
- Extract artifact from Stage 2 (weaponization)
- Verify same artifact referenced in Stages 3-5
- Ensure naming is consistent
- Result: Pass if artifact consistent, Warning if ambiguous

**Vulnerability Continuity**
- Extract CVE from Stage 1 findings
- Verify exploitation tool matches CVE
- Verify target vulnerability in Stage 4
- Result: Pass if CVE flows logically, Warning if unclear

**Technique Alignment**
- Extract MITRE techniques from all stages
- Verify techniques follow cyber kill chain order
- Check technique applicability to stages
- Result: Pass if progression logical, Warning if unusual

**Tool Consistency**
- Extract tools from all stages
- Verify tool compatibility with target OS
- Verify tool dependencies are met
- Result: Pass if tools compatible, Warning if unusual

## Integration

Validation integrates into `CompleteAnalyzer.analyze()`:

```python
async def analyze(self, host: InputHost) -> CompleteAnalysisResponse:
    # Generate stages (existing logic)
    stages = await self._generate_attack_path_with_continuity()
    
    # Run validation (new)
    validator = ContinuityValidator(self.context, stages)
    validation_report = validator.validate()
    
    # Include in response
    return CompleteAnalysisResponse(
        primary_path=stages,
        validation_report=validation_report,
        model_used=self.model,
        total_tokens=self.total_tokens
    )
```

## Validation Output Example

```json
{
  "is_valid": true,
  "total_checks": 4,
  "passes": [
    "Artifact continuity: Stage 2 payload referenced in stages 3-5",
    "Vulnerability continuity: CVE-2021-41773 flows through exploitation",
    "Technique alignment: MITRE ATT&CK progression logical",
    "Tool consistency: Metasploit ecosystem tools compatible"
  ],
  "warnings": [],
  "stage_artifacts": {
    "1": null,
    "2": "apache_rce_shell.elf",
    "3": "apache_rce_shell.elf",
    "4": "apache_rce_shell.elf",
    "5": "apache_rce_shell.elf",
    "6": null,
    "7": null
  }
}
```

## Performance Impact

- **Validation Time**: 500ms-1000ms per request
- **Memory Overhead**: ~5MB for validator instance
- **Token Cost**: No additional tokens (rule-based, not LLM)
- **Scalability**: Validation time increases linearly with stage count

## Future Enhancements

1. **Caching**: Cache validation results for identical inputs
2. **Configuration**: Allow enabling/disabling individual checks
3. **Custom Rules**: Let users define domain-specific validation rules
4. **Analytics**: Track validation pass/fail rates by scenario type
5. **LLM Validation**: Optional secondary LLM-based validation for complex cases

## Related ADRs

- [ADR-0001: Record Architecture Decisions](./0001-record-architecture-decisions.md)

## References

- [Cyber Kill Chain](https://www.lockheedmartin.com/en-us/capabilities/cyber/cyber-kill-chain.html)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [Implementation: app/utils/continuity_validator.py](../../app/utils/continuity_validator.py)

---

Accepted: 2024-01-15
Author: AI Engine Team
Reviewers: Technical Lead
