# Prompt Tracking Feature

## Overview

The AI Attack Path Engine now includes **prompt tracking** - a transparency feature that allows you to see the exact dynamic prompt generated for each API request. This is useful for:

- **Debugging**: Understanding what context the LLM received
- **Auditing**: Tracking what information was used in attack path generation
- **Transparency**: Seeing how the engine adapts prompts based on available data

## How It Works

The engine dynamically builds prompts based on the input parameters you provide. It only includes sections for which you've supplied data - making prompts shorter for minimal inputs and comprehensive for enhanced inputs.

### Dynamic Sections

The prompt builder includes up to **12 dynamic sections**:
1. Core System Info (platform, OS version)
2. Asset Identification (name, FQDN, IP addresses)
3. Asset Context (criticality, business role, environment)
4. Network Configuration (segment, zone, external IP)
5. Security Controls (EDR, firewall, IPS/IDS, MFA)
6. Identity & Access (domain, user accounts, admin accounts)
7. Installed Software (application inventory)
8. Patch Management (patch level, last update)
9. Configuration Details (custom configurations)
10. Network Services & Exposures (open ports, services, vulnerabilities)
11. Cloud Infrastructure (provider, region, instance details)
12. Backup & DR (backup configuration)

## API Usage

### Include Prompt (Default)

By default, the generated prompt is **included** in the response:

```bash
curl -X POST "http://localhost:8000/attack-path?include_prompt=true" \
  -H "Content-Type: application/json" \
  -d @test_scenarios/scenario1_web_server.json
```

**Response includes:**
```json
{
  "platform": "Linux",
  "version_os": "Ubuntu 20.04.3 LTS",
  "attack_path": [...],
  "risk_level": "Critical",
  "generated_prompt": "Generate a realistic attack path...",
  "prompt_sections": 11
}
```

### Exclude Prompt

To exclude the prompt (smaller response, faster):

```bash
curl -X POST "http://localhost:8000/attack-path?include_prompt=false" \
  -H "Content-Type: application/json" \
  -d @test_scenarios/scenario1_web_server.json
```

**Response:**
```json
{
  "platform": "Linux",
  "version_os": "Ubuntu 20.04.3 LTS",
  "attack_path": [...],
  "risk_level": "Critical",
  "generated_prompt": null,
  "prompt_sections": null
}
```

## Response Fields

### `generated_prompt` (Optional[str])

The complete prompt sent to the LLM, including:
- System instructions
- All dynamic sections based on your input
- Output format requirements

**Size**: Varies based on input
- Minimal (5 params): ~5,500 characters
- Enhanced (20+ params): ~7,500-9,000 characters

### `prompt_sections` (Optional[int])

Number of dynamic sections included in the prompt.

**Examples**:
- Minimal input (platform, OS, ports, services, vulns): 3-5 sections
- Enhanced input (20+ parameters): 10-12 sections

## Examples

### Minimal Input (Few Sections)

**Input:** Only required fields
```json
{
  "platform": "Linux",
  "version_os": "Ubuntu 20.04",
  "open_ports": [22, 80],
  "services": ["ssh", "apache"],
  "vulnerabilities": ["CVE-2021-44228"]
}
```

**Result:**
- `prompt_sections`: 3
- `generated_prompt`: ~5,500 characters
- Includes: Core System, Network Services, Output Format

### Enhanced Input (Many Sections)

**Input:** 20+ parameters
```json
{
  "platform": "Linux",
  "version_os": "Ubuntu 20.04.3 LTS",
  "asset_name": "web-prod-01",
  "fqdn": "www.example.com",
  "ip_addresses": ["203.0.113.50"],
  "asset_criticality": "Critical",
  "business_role": "Public-Facing Web Application",
  "environment": "Production",
  "network_segment": "DMZ",
  "security_zone": "External",
  "has_edr": false,
  "has_firewall": true,
  "mfa_enabled": false,
  "open_ports": [22, 80, 443, 2375, 3306],
  "services": ["ssh", "apache", "docker", "mysql"],
  "vulnerabilities": ["CVE-2021-44228", "CVE-2019-5736"],
  ...
}
```

**Result:**
- `prompt_sections`: 11
- `generated_prompt`: ~7,686 characters
- Includes: All 12 possible sections (based on available data)

## Use Cases

### 1. Development & Testing

When building integrations, use `include_prompt=true` to verify:
- Correct parameters are being sent
- Dynamic sections are generated properly
- Data is formatted correctly in the prompt

### 2. Auditing & Compliance

For security audits:
- Log the `generated_prompt` field for each request
- Review what context was provided to the LLM
- Ensure no sensitive data leakage in prompts

### 3. Optimization

Compare prompt sizes to optimize API calls:
- Identify which parameters add the most value
- Remove unnecessary parameters to reduce prompt size
- Balance between detail and token usage

### 4. Debugging Issues

If attack paths seem incorrect:
- Check the `generated_prompt` to see what context was provided
- Verify all expected sections are included
- Ensure data is properly formatted in the prompt

## Performance Considerations

### Response Size

- **With prompt**: +5-9KB per response
- **Without prompt**: Standard response size

### Token Usage

The `generated_prompt` field is included in the **response** but does NOT affect:
- LLM input token count (same regardless)
- LLM processing time (same regardless)
- API request size (query param only)

It only affects the response payload size sent back to you.

## Best Practices

1. **During Development**: Use `include_prompt=true` to verify correct behavior
2. **In Production**: Use `include_prompt=false` for efficiency (unless logging needed)
3. **For Auditing**: Use `include_prompt=true` and log the prompts for compliance
4. **For Debugging**: Always include prompts when troubleshooting issues

## Implementation Details

### Code Structure

The prompt tracking feature is implemented across three files:

1. **`app/models/analysis.py`** - Added response fields:
   ```python
   generated_prompt: Optional[str] = Field(None, ...)
   prompt_sections: Optional[int] = Field(None, ...)
   ```

2. **`app/services/analyzer.py`** - Added tracking logic:
   ```python
   async def analyze(self, host: InputHost, include_prompt: bool = True):
       user_prompt = self.prompt_builder.build_attack_analysis_prompt(host)
       prompt_sections = user_prompt.count("===") // 2 if include_prompt else None
       return AttackPathResponse(
           ...,
           generated_prompt=user_prompt if include_prompt else None,
           prompt_sections=prompt_sections
       )
   ```

3. **`app/main.py`** - Added query parameter:
   ```python
   async def generate_attack_path(
       host: InputHost,
       include_prompt: bool = Query(default=True, ...)
   ):
       return await analyzer.analyze(host, include_prompt)
   ```

## Testing

Test the feature with the provided scenarios:

```bash
# Test with prompt included (default)
curl -X POST "http://localhost:8000/attack-path?include_prompt=true" \
  -H "Content-Type: application/json" \
  -d @test_scenarios/scenario1_web_server.json

# Test without prompt
curl -X POST "http://localhost:8000/attack-path?include_prompt=false" \
  -H "Content-Type: application/json" \
  -d @test_scenarios/scenario1_web_server.json

# Compare sizes
curl -X POST "http://localhost:8000/attack-path?include_prompt=true" \
  -H "Content-Type: application/json" \
  -d @test_scenarios/scenario1_web_server.json | wc -c

curl -X POST "http://localhost:8000/attack-path?include_prompt=false" \
  -H "Content-Type: application/json" \
  -d @test_scenarios/scenario1_web_server.json | wc -c
```

## Summary

The prompt tracking feature provides transparency into the AI engine's dynamic prompt generation. Use it to:

- ✅ Debug and verify correct behavior
- ✅ Audit what context is provided to the LLM
- ✅ Optimize your input parameters
- ✅ Understand how prompts adapt to available data

The feature is **enabled by default** but can be easily disabled for production efficiency.
