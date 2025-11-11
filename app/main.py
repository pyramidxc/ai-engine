"""
FastAPI application entry point.

This module defines the REST API routes for the Attack Path Engine.
Uses orchestrator pattern for attack path generation.

Routes:
    - GET /health: Health check endpoint for monitoring
    - POST /attack-path: Attack path generation - Markdown format
"""
import uuid

from fastapi import FastAPI
from fastapi.responses import Response

from app.config import settings
from app.models import InputHost
from app.services.orchestrator import Orchestrator

# =============================================================================
# FastAPI Application Initialization
# =============================================================================

# Initialize FastAPI app with metadata from configuration
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="AI-powered attack path analysis engine"
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


@app.post("/attack-path")
async def generate_attack_tree(host: InputHost) -> Response:
    """
    Generate attack path analysis in Markdown format.
    
    Orchestrator flow:
    1. Validate input parameters
    2. Initialize attack thread via Context Threader
    3. Generate single stage:
       - Build prompt with reconnaissance data
       - Call LLM provider
       - Parse and validate output
       - Reconcile with thread state
    4. Emit telemetry and return result
    
    Args:
        host (InputHost): Target host parameters from collector
    
    Returns:
        Response: Markdown-formatted attack path with thread state
        Content-Type: text/markdown; charset=utf-8
    
    Response Time: 10-60 seconds (multiple LLM calls)
    
    Example:
        >>> curl -X POST http://localhost:8000/attack-path \\
        ...      -H "Content-Type: application/json" \\
        ...      -d @target.json \\
        ...      -o attack_path.md
    """
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    
    # Create orchestrator instance
    orchestrator = Orchestrator()
    
    # Perform orchestrated attack path generation
    result = await orchestrator.generate_attack_path(
        request_id=request_id,
        host=host,
        client_metadata={
            "client_ip": "unknown",  # Would come from FastAPI request in production
            "timestamp": "unknown"
        }
    )
    
    # Check if error occurred
    if result.get("status") == "error":
        # Return error as markdown
        error_content = _format_error_result(result)
        return Response(
            content=error_content,
            media_type="text/markdown; charset=utf-8",
            status_code=400,
            headers={
                "X-Request-ID": request_id
            }
        )
    
    # Format as markdown
    markdown_content = _format_orchestrated_result(result)
    
    # Return as text/markdown response
    return Response(
        content=markdown_content,
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": f'inline; filename="attack_path_{result["thread_id"]}.md"',
            "X-Request-ID": request_id,
            "X-Thread-ID": result["thread_id"]
        }
    )


def _format_orchestrated_result(result: dict) -> str:
    """
    Format orchestrated attack path result as markdown.
    
    Args:
        result: Orchestrator output with stages, thread snapshot, metadata
        
    Returns:
        Formatted markdown document
    """
    sections = [
        "# Attack Path Analysis - STAGE 0",
        "",
        f"**Request ID:** `{result['request_id']}`",
        f"**Thread ID:** `{result['thread_id']}`",
        f"**Status:** {result['status']}",
        "",
        "---",
        "",
        "## STAGE 0",
        "",
        result["raw_content"],
        "",
        "---",
        "",
        "## Metadata",
        "",
        f"- **Execution Time:** {result['metadata']['execution_time_seconds']}s",
        f"- **Tokens Used:** {result['metadata']['tokens_used']}",
        f"- **Model:** `{result['metadata']['model']}`",
        ""
    ]
    
    return "\n".join(sections)


def _format_error_result(result: dict) -> str:
    """
    Format error result as markdown.
    
    Args:
        result: Error response from orchestrator
        
    Returns:
        Formatted markdown error document
    """
    sections = [
        "# Attack Path Generation Error",
        "",
        f"**Request ID:** `{result['request_id']}`",
        f"**Status:** {result['status']}",
        f"**Error Type:** {result.get('error_type', 'unknown')}",
        "",
        "---",
        "",
        "## Error Details",
        "",
        "```",
        f"{result.get('message', 'No error message provided')}",
        "```",
        "",
        f"**Timestamp:** {result.get('timestamp', 'unknown')}",
        ""
    ]
    
    return "\n".join(sections)




