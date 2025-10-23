"""
FastAPI application entry point.

This module defines the REST API routes for the Attack Path Engine.
It serves as the Presentation Layer in the clean architecture pattern,
handling HTTP requests/responses and delegating business logic to services.

Routes:
    - GET /health: Health check endpoint for monitoring
    - POST /attack-path/main: Complete 7-stage attack path analysis (PRIMARY)
"""
from fastapi import FastAPI
from app.config import settings
from app.models import InputHost
from app.models.complete_analysis import CompleteAnalysisResponse
from app.services.complete_analyzer import CompleteAnalyzer

# =============================================================================
# FastAPI Application Initialization
# =============================================================================

# Initialize FastAPI app with metadata from configuration
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="AI-powered attack path engine - transforms vulnerability data into attack sequences"
)


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/health")
def health():
    """
    Health check endpoint for monitoring and service discovery.
    
    This endpoint is used by:
    - Docker health checks
    - Kubernetes liveness/readiness probes
    - Load balancers
    - Monitoring systems
    
    Returns:
        dict: Service status, version, and LLM model configuration
        
    Example:
        >>> curl http://localhost:8000/health
        {"status": "ok", "version": "1.0.0", "model": "gpt-4o-mini"}
    """
    return {
        "status": "ok",
        "version": settings.API_VERSION,
        "model": settings.LLM_MODEL
    }


@app.post("/attack-path/main", response_model=CompleteAnalysisResponse)
async def generate_complete_attack_path(host: InputHost) -> CompleteAnalysisResponse:
    """
    Generate complete attack path analysis (returns JSON).
    
    This is the PRIMARY production endpoint. It generates a complete 7-stage
    attack path with stage-level continuity preservation.
    
    Args:
        host (InputHost): Complete host parameters (same as /attack-path endpoint)
    
    Returns:
        CompleteAnalysisResponse (JSON): Contains:
            - request_id: Unique identifier for this analysis
            - primary_path: 7-stage primary attack path
            - bifurcations: Always empty list (no bifurcations)
            - total_paths: Always 1 (primary path only)
            - execution_time_seconds: Total time taken
            - llm_calls: Breakdown of LLM calls made
            - estimated_cost: Estimated cost in USD
    
    Response Time: 15-25 seconds
    Cost: ~$0.015 per request
    
    Example:
        >>> response = requests.post("/attack-path/main", json={
        ...     "platform": "Linux",
        ...     "open_ports": [22, 80, 3306],
        ...     "services": ["SSH", "Apache", "MySQL"]
        ... })
        >>> print(response.json()["primary_path"])
    """
    # Create complete analyzer instance
    complete_analyzer = CompleteAnalyzer()
    
    # Perform complete analysis
    result = await complete_analyzer.analyze(host)
    
    return result



