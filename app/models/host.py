"""
Host-related data models.
Defines the structure for host input data.
"""
from pydantic import BaseModel, Field


class InputHost(BaseModel):
    """Input model for host exposure data."""
    
    hostname: str = Field(..., description="Target hostname or IP address")
    open_ports: list[int] = Field(
        default=[],
        description="List of open ports detected on the host"
    )
    vulnerabilities: list[str] = Field(
        default=[],
        description="Known vulnerabilities (CVEs, descriptions, etc.)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "hostname": "web-server-01.example.com",
                "open_ports": [22, 80, 443, 3306],
                "vulnerabilities": [
                    "CVE-2023-12345: SQL Injection in web application",
                    "CVE-2023-23456: Outdated SSH version",
                    "CVE-2023-34567: MySQL with default credentials"
                ]
            }
        }
