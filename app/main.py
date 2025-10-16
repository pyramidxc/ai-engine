"""
FastAPI application entry point.

This module defines the REST API routes for the Attack Path Engine.
It serves as the Presentation Layer in the clean architecture pattern,
handling HTTP requests/responses and delegating business logic to services.

Routes:
    - GET /health: Health check endpoint for monitoring
    - POST /attack-path: Generate attack path from vulnerability data
"""
from fastapi import FastAPI, HTTPException, Query
from app.config import settings
from app.models import InputHost, AttackPathResponse
from app.services import AttackPathAnalyzer

# =============================================================================
# FastAPI Application Initialization
# =============================================================================

# Initialize FastAPI app with metadata from configuration
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="AI-powered attack path engine - transforms vulnerability data into attack sequences"
)

# Initialize the attack path analyzer service
# This service orchestrates the attack path generation workflow
analyzer = AttackPathAnalyzer()


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


@app.post("/attack-path", response_model=AttackPathResponse)
async def generate_attack_path(
    host: InputHost,
    include_prompt: bool = Query(
        default=True,
        description="Include the generated prompt in the response for debugging/auditing"
    )
) -> AttackPathResponse:
    """
    Generate AI-powered attack path for a given host.
    
    This endpoint accepts vulnerability and exposure data from external collectors
    (Nmap, OpenVAS, Nessus, etc.) and generates a realistic, step-by-step attack
    sequence using AI. The attack path follows the Cyber Kill Chain methodology
    and maps techniques to the MITRE ATT&CK framework.
    
    The engine accepts 50+ optional parameters to build context-aware prompts.
    Only the parameters you provide are used - the prompt adapts dynamically
    to available data.
    
    Args:
        host (InputHost): Host data from external vulnerability collector.
            Supports 50+ optional parameters including:
            - Core system info (platform, OS version)
            - Network details (ports, services, vulnerabilities)
            - Security controls (EDR, firewall, encryption)
            - Identity & access (accounts, MFA, password policy)
            - Cloud infrastructure (provider, IAM roles)
            - And many more (see INPUT_PARAMETERS.md)
            
        include_prompt (bool, optional): Whether to include the generated prompt
            in the response. Defaults to True.
            - True: Response includes full prompt text (~5KB-9KB) for debugging
            - False: Smaller response, omits prompt (better for production)
        
    Returns:
        AttackPathResponse: Contains:
            - platform (str | None): Target platform from input
            - version_os (str | None): Target OS version from input
            - attack_path (list[str]): 5-10 sequential attack steps with MITRE techniques
            - risk_level (str): "Critical", "High", "Medium", or "Low"
            - generated_prompt (str | None): Full prompt sent to LLM (if include_prompt=True)
            - prompt_sections (int | None): Number of dynamic sections (if include_prompt=True)
    
    Raises:
        HTTPException: 422 if input validation fails
        HTTPException: 500 if LLM generation fails
        
    Example:
        >>> # Minimal request with 3 parameters
        >>> curl -X POST "http://localhost:8000/attack-path?include_prompt=false" \\
        ...   -H "Content-Type: application/json" \\
        ...   -d '{"platform": "Linux", "version_os": "Ubuntu 20.04", "open_ports": [22, 80]}'
        
        >>> # Enhanced request with 20+ parameters
        >>> curl -X POST "http://localhost:8000/attack-path?include_prompt=true" \\
        ...   -H "Content-Type: application/json" \\
        ...   -d @test_scenarios/scenario1_web_server.json
    
    Notes:
        - All 50+ input parameters are optional
        - More parameters = more accurate and context-aware attack paths
        - The dynamic prompt builder only includes sections with data
        - LLM call typically takes 2-5 seconds depending on model
        - Response includes MITRE ATT&CK technique IDs for mapping
    """
    # Create a new analyzer instance for this request
    # (In future: consider dependency injection for better testability)
    analyzer = AttackPathAnalyzer()
    
    # Delegate business logic to the analyzer service
    # The analyzer will:
    # 1. Build a dynamic prompt based on available host data
    # 2. Call the LLM with the custom prompt
    # 3. Parse and structure the response
    # 4. Return the attack path with optional prompt tracking
    return await analyzer.analyze(host, include_prompt)
