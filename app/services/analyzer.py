"""
Attack path generation service.

This module orchestrates the complete workflow for generating realistic attack
paths from vulnerability and exposure data. It coordinates between the prompt
builder (domain logic) and the LLM client (infrastructure) to produce
structured attack sequences.

Architecture Role:
    - Business Logic Layer component
    - Orchestrates the attack path generation workflow
    - Coordinates between PromptBuilder (core) and LLMClient (infrastructure)
    - Transforms raw LLM responses into structured AttackPathResponse objects

Workflow:
    1. Receive host data from API endpoint
    2. Build dynamic, context-aware prompt
    3. Send prompt to LLM via client
    4. Parse LLM response
    5. Structure response with optional prompt tracking
    6. Return to API layer

Usage:
    >>> analyzer = AttackPathAnalyzer()
    >>> host = InputHost(platform="Linux", version_os="Ubuntu 20.04")
    >>> result = await analyzer.analyze(host, include_prompt=True)
    >>> print(result.risk_level)
    'High'
"""
from app.models.host import InputHost
from app.models.analysis import AttackPathResponse
from app.services.llm_client import LLMClient
from app.core.prompts import PromptBuilder


# =============================================================================
# Attack Path Analyzer Service
# =============================================================================

class AttackPathAnalyzer:
    """
    Service for generating attack paths from host exposure data.
    
    This class serves as the central orchestrator for the attack path generation
    workflow. It combines the domain expertise from PromptBuilder with the
    infrastructure capabilities of LLMClient to produce realistic, context-aware
    attack sequences.
    
    The analyzer follows the Single Responsibility Principle by focusing solely
    on workflow orchestration - it doesn't build prompts or call LLMs directly,
    but coordinates these operations through specialized components.
    
    Design Pattern:
        - Service Layer / Orchestrator pattern
        - Dependency injection (constructor-based)
        - Async/await for non-blocking operations
    
    Attributes:
        llm_client (LLMClient): Client for LLM API interactions
        prompt_builder (PromptBuilder): Builder for dynamic prompt generation
    
    Example:
        >>> analyzer = AttackPathAnalyzer()
        >>> host = InputHost(
        ...     platform="Linux",
        ...     open_ports=[22, 80, 443],
        ...     vulnerabilities=["CVE-2023-12345"]
        ... )
        >>> result = await analyzer.analyze(host)
        >>> print(len(result.attack_path))
        7
    """
    
    def __init__(self):
        """
        Initialize the analyzer with required services.
        
        Creates instances of the LLM client and prompt builder that will be
        used throughout the analyzer's lifetime. These dependencies are
        instantiated here rather than passed in (dependency injection would
        be better for testing, but this is simpler for the current phase).
        
        Dependencies Created:
            - LLMClient: Handles all LLM API communication
            - PromptBuilder: Builds dynamic prompts from host data
        
        Note:
            Future enhancement: Use dependency injection to pass these
            dependencies for better testability and flexibility.
        """
        # Initialize LLM client for AI model interactions
        # This client abstracts away provider-specific details
        self.llm_client = LLMClient()
        
        # Initialize prompt builder for dynamic prompt generation
        # This builder contains all domain knowledge about attack path generation
        self.prompt_builder = PromptBuilder()
    
    async def analyze(self, host: InputHost, include_prompt: bool = True) -> AttackPathResponse:
        """
        Generate attack path for a given host with optional prompt tracking.
        
        This is the main entry point for attack path generation. It orchestrates
        the entire workflow from receiving host data to returning a structured
        attack path response.
        
        The method is async to support non-blocking I/O during LLM API calls,
        allowing the application to handle multiple concurrent requests efficiently.
        
        Workflow Steps:
            1. Build dynamic prompt from host data (adapts to available fields)
            2. Send prompt to LLM with system message and JSON mode
            3. Receive and parse structured JSON response
            4. Count prompt sections (if tracking enabled)
            5. Build and return AttackPathResponse with all data
        
        Args:
            host (InputHost): Host data from external vulnerability collector.
                Contains any combination of 50+ optional parameters including:
                - Core system info (platform, OS version)
                - Network details (ports, services, vulnerabilities)
                - Security controls (EDR, firewall, encryption)
                - Identity & access (accounts, MFA status)
                - Cloud infrastructure (provider, IAM roles)
                - And many more (see INPUT_PARAMETERS.md)
                
            include_prompt (bool, optional): Whether to include the generated
                prompt in the response. Defaults to True.
                
                Use Cases:
                - True: Debugging, auditing, transparency (response includes prompt)
                - False: Production, smaller response size (prompt omitted)
        
        Returns:
            AttackPathResponse: Structured response containing:
                - platform (str | None): Target platform from input
                - version_os (str | None): Target OS version from input
                - attack_path (list[str]): 5-10 sequential attack steps with
                  MITRE ATT&CK technique IDs following Cyber Kill Chain phases
                - risk_level (str): "Critical", "High", "Medium", or "Low"
                - generated_prompt (str | None): Full prompt sent to LLM
                  (only if include_prompt=True)
                - prompt_sections (int | None): Number of dynamic sections
                  included in prompt (only if include_prompt=True)
        
        Raises:
            json.JSONDecodeError: If LLM returns invalid JSON (rare with JSON mode)
            litellm.exceptions.APIError: If LLM API call fails
            Exception: For other unexpected errors during generation
        
        Example:
            >>> # Minimal input (3 parameters)
            >>> host = InputHost(
            ...     platform="Linux",
            ...     version_os="Ubuntu 20.04",
            ...     open_ports=[22, 80, 443]
            ... )
            >>> result = await analyzer.analyze(host, include_prompt=False)
            >>> print(result.risk_level)
            'Medium'
            >>> print(len(result.attack_path))
            6
            
            >>> # Enhanced input (20+ parameters)
            >>> host = InputHost(
            ...     platform="Linux",
            ...     version_os="Ubuntu 20.04",
            ...     asset_criticality="Critical",
            ...     mfa_enabled=False,
            ...     security_controls=["CrowdStrike EDR"],
            ...     vulnerabilities=["CVE-2021-44228: Log4Shell"],
            ...     admin_accounts=["root", "admin"],
            ...     internet_exposed=True
            ... )
            >>> result = await analyzer.analyze(host, include_prompt=True)
            >>> print(result.risk_level)
            'Critical'
            >>> print(result.prompt_sections)
            8
        
        Notes:
            - More input parameters = more accurate and context-aware results
            - Typical execution time: 2-5 seconds (LLM API latency)
            - The dynamic prompt adapts to available data (5-10KB typical)
            - Attack paths follow Cyber Kill Chain phases in order
            - Each step includes MITRE ATT&CK technique IDs for mapping
        """
        # =====================================================================
        # Step 1: Build Dynamic Prompt from Host Data
        # =====================================================================
        
        # The prompt builder analyzes which fields have data and builds
        # a custom prompt with only relevant sections. This keeps prompts
        # concise and focused on available context.
        #
        # Minimal input (3 params) → ~5KB prompt with 3 sections
        # Enhanced input (20+ params) → ~9KB prompt with 11 sections
        user_prompt = self.prompt_builder.build_attack_analysis_prompt(host)
        
        # =====================================================================
        # Step 2: Call LLM with Prompt and System Message
        # =====================================================================
        
        # Send the prompt to the LLM with:
        # - System message: Defines AI's role as MITRE ATT&CK expert
        # - User prompt: Contains the dynamic, context-specific request
        # - JSON mode: Ensures structured response that can be parsed
        #
        # The LLM will generate:
        # - attack_path: Array of sequential attack steps
        # - risk_level: Overall risk assessment
        analysis = await self.llm_client.complete(
            system_message=self.prompt_builder.SYSTEM_MESSAGE,
            user_prompt=user_prompt,
            json_mode=True
        )
        
        # =====================================================================
        # Step 3: Calculate Prompt Sections (Optional, for Debugging)
        # =====================================================================
        
        # Count the number of dynamic sections included in the prompt
        # Each section is delimited by "===" markers
        # This helps users understand how much context was provided to the LLM
        #
        # Example: "=== CORE SYSTEM INFO ===" counts as one section
        # Formula: Total "===" markers divided by 2 (start and end markers)
        prompt_sections = user_prompt.count("===") // 2 if include_prompt else None
        
        # =====================================================================
        # Step 4: Build and Return Structured Response
        # =====================================================================
        
        # Create an AttackPathResponse object with all generated data
        # This ensures type safety and consistent response structure
        #
        # The .get() method provides safe access to LLM response with defaults
        # in case the LLM returns unexpected structure (defensive programming)
        return AttackPathResponse(
            # Echo back the platform and OS from input (may be None if not provided)
            platform=host.platform,
            version_os=host.version_os,
            
            # Extract attack path from LLM response, default to empty list
            # Each item is a string describing one step in the attack sequence
            attack_path=analysis.get("attack_path", []),
            
            # Extract risk level, default to "Unknown" if not provided
            # Should be one of: "Critical", "High", "Medium", "Low"
            risk_level=analysis.get("risk_level", "Unknown"),
            
            # Include full prompt if requested (for debugging/auditing)
            # Otherwise None to keep response smaller
            generated_prompt=user_prompt if include_prompt else None,
            
            # Include section count if prompt tracking is enabled
            # Otherwise None
            prompt_sections=prompt_sections
        )
