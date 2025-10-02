"""
Host-related data models.
Defines the structure for host input data.
"""
from pydantic import BaseModel, Field


class InputHost(BaseModel):
    """Input model for host exposure data from external collectors."""
    
    platform: str = Field(..., description="Operating system platform (e.g., Linux, Windows, macOS)")
    version_os: str = Field(..., description="Operating system version (e.g., Ubuntu 20.04, Windows Server 2019)")
    open_ports: list[int] = Field(
        default=[],
        description="List of open ports detected on the host"
    )
    services: list[str] = Field(
        default=[],
        description="Services running on open ports (e.g., 'SSH on port 22', 'Apache 2.4.41 on port 80')"
    )
    vulnerabilities: list[str] = Field(
        default=[],
        description="Known vulnerabilities (CVEs, descriptions, etc.)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
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
                    "CVE-2023-23456: Outdated SSH version",
                    "CVE-2023-34567: MySQL with default credentials"
                ]
            }
        }
