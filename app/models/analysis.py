"""
Analysis result data models.
Defines the structure for attack path analysis responses.
"""
from pydantic import BaseModel, Field


class AttackPathResponse(BaseModel):
    """Response model for attack path analysis."""
    
    hostname: str = Field(..., description="Analyzed hostname")
    attack_path: list[str] = Field(
        ...,
        description="Step-by-step attack path sequence"
    )
    risk_level: str = Field(
        ...,
        description="Overall risk level: Critical, High, Medium, or Low"
    )
    recommendations: list[str] = Field(
        ...,
        description="Security recommendations to mitigate risks"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "hostname": "web-server-01.example.com",
                "attack_path": [
                    "Step 1: Reconnaissance via port scanning",
                    "Step 2: Identify SQL injection vulnerability",
                    "Step 3: Exploit SQLi to access database",
                    "Step 4: Escalate privileges using MySQL credentials"
                ],
                "risk_level": "Critical",
                "recommendations": [
                    "Patch SQL injection vulnerability immediately",
                    "Update SSH to latest version",
                    "Change default MySQL credentials"
                ]
            }
        }
