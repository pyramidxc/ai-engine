"""
FastAPI application entry point.
Defines API routes and handles HTTP requests.
"""
from fastapi import FastAPI, HTTPException
from app.config import settings
from app.models import InputHost, AttackPathResponse
from app.services import AttackPathAnalyzer

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="AI-powered attack path engine - transforms vulnerability data into attack sequences"
)

# Initialize services
analyzer = AttackPathAnalyzer()


@app.get("/health")
def health():
    """
    Health check endpoint.
    Returns service status and configuration info.
    """
    return {
        "status": "ok",
        "version": settings.API_VERSION,
        "model": settings.LLM_MODEL
    }


@app.post("/attack-path", response_model=AttackPathResponse)
async def attack_path(host: InputHost):
    """
    Generate realistic attack path from host exposure data.
    
    Takes vulnerability and port scan data from external collectors
    and generates a step-by-step attack sequence showing how an
    attacker would exploit the identified vulnerabilities.
    
    Args:
        host: Host data from external collector (hostname, ports, vulnerabilities)
        
    Returns:
        Generated attack path with sequential steps and risk assessment
        
    Raises:
        HTTPException: If generation fails
    """
    try:
        return await analyzer.analyze(host)
    
    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid analysis data: {str(e)}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating attack path: {str(e)}"
        )
