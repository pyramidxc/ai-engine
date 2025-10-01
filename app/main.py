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
    description="AI-powered attack path analysis engine"
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
    Generate attack path analysis based on host exposure data.
    
    Uses AI to analyze vulnerabilities and open ports to suggest
    potential attack vectors, risk levels, and security recommendations.
    
    Args:
        host: Host data including hostname, ports, and vulnerabilities
        
    Returns:
        Attack path analysis with steps, risk level, and recommendations
        
    Raises:
        HTTPException: If analysis fails
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
