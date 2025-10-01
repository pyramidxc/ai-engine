import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import litellm

# Load environment variables
load_dotenv()

app = FastAPI(title="Attack Path Engine")

# LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

class InputHost(BaseModel):
    hostname: str
    open_ports: list[int] = []
    vulnerabilities: list[str] = []

class AttackPathResponse(BaseModel):
    hostname: str
    attack_path: list[str]
    risk_level: str
    recommendations: list[str]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/attack-path", response_model=AttackPathResponse)
async def attack_path(host: InputHost):
    """
    Generate an attack path analysis based on host exposure data.
    Uses LLM to analyze vulnerabilities and open ports to suggest potential attack vectors.
    """
    try:
        # Build the prompt for the LLM
        prompt = f"""You are a cybersecurity expert analyzing a host for potential attack paths.

Host Information:
- Hostname: {host.hostname}
- Open Ports: {', '.join(map(str, host.open_ports)) if host.open_ports else 'None detected'}
- Known Vulnerabilities: {', '.join(host.vulnerabilities) if host.vulnerabilities else 'None detected'}

Based on this information, provide:
1. A step-by-step attack path that an attacker might follow
2. The overall risk level (Critical, High, Medium, Low)
3. Security recommendations to mitigate the risks

Format your response as JSON with the following structure:
{{
    "attack_path": ["step 1", "step 2", "step 3", ...],
    "risk_level": "High|Medium|Low|Critical",
    "recommendations": ["recommendation 1", "recommendation 2", ...]
}}

Be specific and technical. Each attack path step should describe what an attacker would do.
"""

        # Call LLM using litellm
        response = await litellm.acompletion(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a cybersecurity expert specializing in attack path analysis and penetration testing."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=LLM_TEMPERATURE,
            response_format={"type": "json_object"}
        )

        # Extract and parse the response
        llm_response = response.choices[0].message.content
        analysis = json.loads(llm_response)

        # Build the response
        return AttackPathResponse(
            hostname=host.hostname,
            attack_path=analysis.get("attack_path", []),
            risk_level=analysis.get("risk_level", "Unknown"),
            recommendations=analysis.get("recommendations", [])
        )

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse LLM response: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating attack path: {str(e)}"
        )
