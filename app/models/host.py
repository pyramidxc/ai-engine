"""
Host-related data models.

This module defines the input data structure for the Attack Path Engine.
It uses Pydantic for data validation and type safety, ensuring that all
incoming data from external vulnerability collectors is properly validated.

The InputHost model accepts Active Directory and infrastructure parameters
organized into 13 categories, focused on domain security and configuration analysis.

Design Philosophy:
    - All fields are optional (no required fields)
    - More context = better attack path generation
    - Supports partial data from any AD collector
    - Backward compatible with any subset of parameters

Architecture Role:
    - Data Layer component
    - Defines API contract for input data
    - Provides validation and type safety
    - Self-documenting via Field descriptions

Usage:
    >>> # Minimal input
    >>> host = InputHost(OperatingSystem="Windows Server 2019", DNSHostName="dc01.corp.local")
    
    >>> # Rich input
    >>> host = InputHost(
    ...     OperatingSystem="Windows Server 2019",
    ...     DNSHostName="dc01.corp.local",
    ...     adminCount=1,
    ...     TrustedForDelegation=True,
    ...     MemberOf=["CN=Domain Admins,CN=Users,DC=corp,DC=local"]
    ... )
"""
from typing import Optional

from pydantic import BaseModel, Field

# =============================================================================
# Input Host Model
# =============================================================================

class InputHost(BaseModel):
    """
    Input model for Active Directory and infrastructure data from external collectors.
    
    This model defines the complete data structure accepted by the Attack Path
    Engine, focused on Active Directory security analysis. It supports 40+ optional
    parameters organized into 13 logical categories.
    
    Key Features:
        - All fields are optional for maximum flexibility
        - Organized into logical categories for clarity
        - Self-documenting with detailed Field descriptions
        - Supports any combination of parameters
        - Example included for API documentation
    
    Design Rationale:
        The optional nature of all fields allows the engine to work with:
        - Minimal AD scanner output
        - Rich CMDB/AD data
        - Partial data from multiple sources
        - Any combination in between
    
    Integration Examples:
        - BloodHound: SamAccountName, MemberOf, adminCount, SPNs
        - Active Directory: DistinguishedName, objectSid, GPO links
        - Security Tools: nTSecurityDescriptor, delegation settings
    
    Parameter Categories:
        1. Core System Info (6 params)
        2. Network & Services (6 params)
        3. Asset Identification (6 params)
        4. Network Context (8 params)
        5. Security Controls (6 params)
        6. Identity & Access (6 params)
        7. Software & Applications (4 params)
        8. Patch & Vulnerability Management (3 params)
        9. Configuration & Compliance (4 params)
        10. Asset Context & Risk (3 params)
        11. Cloud & Containers (0 params - reserved)
        12. Backup & Storage (2 params)
        13. Threat Intelligence (5 params)
    
    Total Parameters: 40+
    
    Example:
        >>> # Create minimal input
        >>> minimal = InputHost(OperatingSystem="Windows Server 2019", DNSHostName="dc01.corp.local")
        >>> print(minimal.OperatingSystem)
        'Windows Server 2019'
        
        >>> # Create comprehensive input
        >>> comprehensive = InputHost(
        ...     OperatingSystem="Windows Server 2019 Standard",
        ...     OperatingSystemVersion="10.0.17763",
        ...     DNSHostName="dc01.corp.local",
        ...     IPv4Address="10.0.10.50",
        ...     SamAccountName="administrator",
        ...     DomainName="corp.local",
        ...     adminCount=1,
        ...     TrustedForDelegation=True,
        ...     MemberOf=["CN=Domain Admins,CN=Users,DC=corp,DC=local"]
        ... )
        >>> print(comprehensive.adminCount)
        1
    
    See Also:
        - docs/input_parameters_new.md: Complete parameter reference
        - examples/: Example JSON files with various parameter combinations
    """
    
    # =============================================================================
    # CATEGORY 1: CORE SYSTEM INFO
    # =============================================================================
    # Sistema operativo y versiones - información fundamental del host
    
    OperatingSystem: Optional[str] = Field(
        None,
        description="Sistema operativo detectado en el equipo"
        # Examples: "Windows Server 2019 Standard", "Windows Server 2016", "Windows 10"
        # Source: Active Directory, WMI queries
    )
    OperatingSystemVersion: Optional[str] = Field(
        None,
        description="Versión del sistema operativo"
        # Examples: "10.0.17763", "10.0.14393", "6.1.7601"
        # Used for: Identifying version-specific vulnerabilities
    )
    OperatingSystemServicePack: Optional[str] = Field(
        None,
        description="Service Pack instalado en el sistema"
        # Examples: "Service Pack 2", "Service Pack 1", ""
        # Source: System configuration queries
    )
    OperatingSystemHotfix: Optional[list[str]] = Field(
        default=None,
        description="Lista de actualizaciones o KB instaladas"
        # Examples: ["KB5021234", "KB5030015", "KB5037764"]
        # Source: WSUS, SCCM, WMI
        # Critical for: Identifying missing patches
    )
    SysvolVersion: Optional[int] = Field(
        None,
        description="Versión de la política replicada en SYSVOL"
        # Examples: 655, 720, 801
        # Source: GPO version queries
        # Used for: GPO synchronization validation
    )
    DSVersion: Optional[int] = Field(
        None,
        description="Versión del objeto en el Directorio Activo"
        # Examples: 655, 720, 801
        # Source: Active Directory queries
        # Used for: Version consistency checks
    )
    
    # =============================================================================
    # CATEGORY 2: NETWORK & SERVICES
    # =============================================================================
    # Configuración de red y servicios Kerberos
    
    DNSHostName: Optional[str] = Field(
        None,
        description="Nombre FQDN completo del equipo"
        # Examples: "web01.corp.local", "dc01.corp.local", "sql01.child.corp.local"
        # Source: DNS, Active Directory
    )
    IPv4Address: Optional[str] = Field(
        None,
        description="Dirección IPv4 asignada al host"
        # Examples: "10.0.10.50", "192.168.1.100", "172.16.0.5"
        # Source: DNS, DHCP, network scans
    )
    ServicePrincipalNames: Optional[list[str]] = Field(
        default=None,
        description="SPNs (Service Principal Names) asociados a la cuenta"
        # Examples: ["MSSQLSvc/db01.corp.local:1433", "HTTP/web01.corp.local"]
        # Source: Active Directory attribute queries
        # Critical for: Kerberoasting attacks
    )
    TrustedForDelegation: Optional[bool] = Field(
        None,
        description="Indica si la cuenta o equipo está marcado como confiable para delegación Kerberos"
        # Values: True (delegation enabled), False (not trusted)
        # Source: AD userAccountControl flags
        # Risk: Enables credential theft via delegation abuse
    )
    TrustedToAuthForDelegation: Optional[bool] = Field(
        None,
        description="Permite autenticación delegada para servicios específicos"
        # Values: True (constrained delegation), False (no delegation)
        # Source: AD msDS-AllowedToDelegateTo attribute
        # Impact: Limited delegation to specific services
    )
    TGTDelegation: Optional[bool] = Field(
        None,
        description="Indica si se permite la delegación de tickets TGT entre dominios"
        # Values: True (TGT can be delegated), False (no TGT delegation)
        # Source: Trust relationship configuration
        # Risk: Allows cross-domain ticket delegation
    )
    
    # =============================================================================
    # CATEGORY 3: ASSET IDENTIFICATION
    # =============================================================================
    # Identificadores únicos del objeto en Active Directory
    
    SamAccountName: Optional[str] = Field(
        None,
        description="Nombre de cuenta único en el dominio"
        # Examples: "administrator", "jdoe", "svc_sql"
        # Source: Active Directory sAMAccountName attribute
    )
    DistinguishedName: Optional[str] = Field(
        None,
        description="Nombre distinguido completo (DN) del objeto en AD"
        # Examples: "CN=John Doe,OU=Usuarios,DC=corp,DC=local"
        # Source: Active Directory distinguishedName attribute
        # Used for: LDAP queries and object hierarchy
    )
    Name: Optional[str] = Field(
        None,
        description="Nombre descriptivo del objeto"
        # Examples: "John Doe", "Domain Controllers", "Default Domain Policy"
        # Source: Active Directory name/cn attribute
    )
    objectSid: Optional[str] = Field(
        None,
        description="Identificador de seguridad (SID) del objeto"
        # Examples: "S-1-5-21-3623811015-3361044348-30300820-500"
        # Source: Active Directory objectSid attribute
        # Critical for: Access control and permissions
    )
    id: Optional[str] = Field(
        None,
        description="Identificador único (GUID) de la GPO u otro objeto"
        # Examples: "{31B2F340-016D-11D2-945F-00C04FB984F9}"
        # Source: Active Directory objectGUID attribute
    )
    DomainName: Optional[str] = Field(
        None,
        description="Nombre del dominio al que pertenece el objeto"
        # Examples: "corp.local", "child.corp.local", "domain.com"
        # Source: Domain DNS name from AD
    )
    
    # =============================================================================
    # CATEGORY 4: NETWORK CONTEXT
    # =============================================================================
    # Relaciones de confianza entre dominios y contexto de red
    
    Target: Optional[str] = Field(
        None,
        description="Dominio de destino de la relación de confianza"
        # Examples: "child.corp.local", "partner.com", "external.org"
        # Source: Trust relationship queries
    )
    Source: Optional[str] = Field(
        None,
        description="Dominio de origen de la relación de confianza"
        # Examples: "corp.local", "parent.local"
        # Source: Trust relationship queries
    )
    Direction: Optional[str] = Field(
        None,
        description="Dirección de la relación de confianza"
        # Examples: "BiDirectional", "Inbound", "Outbound"
        # Source: Trust configuration
        # Impact: Determines authentication flow
    )
    TrustType: Optional[str] = Field(
        None,
        description="Tipo de confianza configurada entre dominios"
        # Examples: "Forest", "External", "ParentChild", "TreeRoot"
        # Source: Trust type attribute
    )
    ForestTransitive: Optional[bool] = Field(
        None,
        description="Indica si la relación de confianza es transitiva a nivel de bosque"
        # Values: True (transitive), False (non-transitive)
        # Source: Trust attributes
        # Risk: Transitive trusts enable lateral movement across forests
    )
    IntraForest: Optional[bool] = Field(
        None,
        description="Indica si la relación de confianza es interna al mismo bosque"
        # Values: True (same forest), False (external)
        # Source: Forest configuration
    )
    SelectiveAuthentication: Optional[bool] = Field(
        None,
        description="Requiere autenticación selectiva para el trust"
        # Values: True (selective auth required), False (forest-wide auth)
        # Source: Trust security settings
        # Impact: Limits authentication scope across trust
    )
    SIDFilteringForestAware: Optional[bool] = Field(
        None,
        description="Filtrado SID activo en la relación de confianza"
        # Values: True (SID filtering enabled), False (disabled)
        # Source: Trust security configuration
        # Security: Prevents SID history attacks
    )
    
    # =============================================================================
    # CATEGORY 5: SECURITY CONTROLS
    # =============================================================================
    # Controles de seguridad y configuración del objeto
    
    Enabled: Optional[bool] = Field(
        None,
        description="Indica si la cuenta u objeto está habilitado"
        # Values: True (enabled), False (disabled)
        # Source: AD userAccountControl flags
    )
    adminCount: Optional[int] = Field(
        None,
        description="Define si el objeto está marcado como privilegiado"
        # Values: 1 (privileged/protected), 0 (not protected)
        # Source: AD adminCount attribute
        # Critical: Indicates membership in protected groups
    )
    PasswordNeverExpires: Optional[bool] = Field(
        None,
        description="Contraseña configurada para no expirar"
        # Values: True (never expires), False (normal expiration)
        # Source: AD userAccountControl flags
        # Risk: Password never rotates
    )
    ProtectedFromAccidentalDeletion: Optional[bool] = Field(
        None,
        description="Protección contra eliminación accidental habilitada"
        # Values: True (protected), False (not protected)
        # Source: Object protection attribute
    )
    nTSecurityDescriptor: Optional[str] = Field(
        None,
        description="Descriptor de seguridad del objeto con ACLs detalladas"
        # Examples: "(A;;RPWPCCDCLCRCSWRCWDWOGA;;;S-1-5-21-3623811015-3361044348-30300820-500)"
        # Source: AD nTSecurityDescriptor attribute
        # Critical for: ACL abuse analysis
    )
    WmiFilter: Optional[str] = Field(
        None,
        description="Filtro WMI aplicado en la GPO"
        # Examples: "SELECT * FROM Win32_OperatingSystem WHERE Version >= '10.0.0' AND ProductType = '1'"
        # Source: GPO WMI filter configuration
        # Used for: Conditional GPO application
    )
    
    # =============================================================================
    # CATEGORY 6: IDENTITY & ACCESS
    # =============================================================================
    # Membresía de grupos y políticas vinculadas
    
    MemberOf: Optional[list[str]] = Field(
        default=None,
        description="Lista de grupos de los que el usuario es miembro"
        # Examples: ["CN=Domain Admins,CN=Users,DC=corp,DC=local", "CN=IT Support,CN=Users,DC=corp,DC=local"]
        # Source: AD memberOf attribute
        # Critical for: Privilege analysis and attack paths
    )
    Members: Optional[list[str]] = Field(
        default=None,
        description="Lista de miembros directos de un grupo"
        # Examples: ["CORP\\alice", "CORP\\bob", "CORP\\svc_sql"]
        # Source: AD member attribute
        # Used for: Group membership enumeration
    )
    LinkedGroupPolicyObjects: Optional[list[str]] = Field(
        default=None,
        description="GPOs asociadas o vinculadas al objeto"
        # Examples: ["LDAP://CN={31B2F340-016D-11D2-945F-00C04FB984F9},CN=Policies,CN=System,DC=corp,DC=local"]
        # Source: GPO link queries
        # Impact: Determines applied policies
    )
    gPLink: Optional[list[str]] = Field(
        default=None,
        description="Enlaces de políticas aplicados a una unidad organizativa (OU)"
        # Examples: ["[LDAP://CN={A1B2C3D4-1111-2222-3333-444455556666},CN=Policies,CN=System,DC=corp,DC=local;0]"]
        # Source: OU gPLink attribute
        # Used for: GPO application order analysis
    )
    owner: Optional[str] = Field(
        None,
        description="Propietario del objeto o política"
        # Examples: "CORP\\Domain Admins", "CORP\\jdoe"
        # Source: Security descriptor owner field
        # Risk: Owner has full control over object
    )
    ManagedBy: Optional[str] = Field(
        None,
        description="Objeto o cuenta que administra la OU o GPO"
        # Examples: "CN=OU-Admins,OU=Groups,DC=corp,DC=local"
        # Source: AD managedBy attribute
    )
    
    # =============================================================================
    # CATEGORY 7: SOFTWARE & APPLICATIONS
    # =============================================================================
    # Configuración de GPO y aplicaciones
    
    DisplayName: Optional[str] = Field(
        None,
        description="Nombre descriptivo de la GPO"
        # Examples: "Default Domain Policy", "Workstation Security Policy"
        # Source: GPO displayName attribute
    )
    computer: Optional[list[str]] = Field(
        default=None,
        description="Secciones de configuración de equipo dentro de la GPO"
        # Examples: ["Scripts", "Security", "Registry"]
        # Source: GPO computer configuration sections
    )
    user: Optional[list[str]] = Field(
        default=None,
        description="Secciones de configuración de usuario dentro de la GPO"
        # Examples: ["Scripts", "Preferences", "Folders"]
        # Source: GPO user configuration sections
    )
    path: Optional[str] = Field(
        None,
        description="Ruta completa LDAP del objeto"
        # Examples: "CN={31B2F340-016D-11D2-945F-00C04FB984F9},CN=Policies,CN=System,DC=corp,DC=local"
        # Source: LDAP distinguished name path
    )
    
    # =============================================================================
    # CATEGORY 8: PATCH & VULNERABILITY MANAGEMENT
    # =============================================================================
    # Estado de parches y versiones (referenciado anteriormente)
    
    # Note: OperatingSystemHotfix, SysvolVersion, and DSVersion are already
    # defined in CATEGORY 1: CORE SYSTEM INFO
    
    # =============================================================================
    # CATEGORY 9: CONFIGURATION & COMPLIANCE
    # =============================================================================
    # Estado de GPO y configuración de compliance
    
    GpoStatus: Optional[str] = Field(
        None,
        description="Estado de la GPO en el dominio"
        # Examples: "AllSettingsEnabled", "UserSettingsDisabled", "ComputerSettingsDisabled", "AllSettingsDisabled"
        # Source: GPO status attribute
    )
    # Note: Enabled, WmiFilter, and nTSecurityDescriptor are already defined
    # in CATEGORY 5: SECURITY CONTROLS
    
    # =============================================================================
    # CATEGORY 10: ASSET CONTEXT & RISK
    # =============================================================================
    # Contexto de riesgo del activo
    
    lastLogonTimestamp: Optional[int] = Field(
        None,
        description="Timestamp del último inicio de sesión"
        # Examples: 133358290010000000 (Windows FILETIME format)
        # Source: AD lastLogonTimestamp attribute
        # Used for: Identifying stale accounts
    )
    # Note: MemberOf and adminCount are already defined in other categories
    
    # =============================================================================
    # CATEGORY 11: CLOUD & CONTAINERS
    # =============================================================================
    # Reservado para futura integración con entornos cloud
    
    # No parameters currently defined for this category
    
    # =============================================================================
    # CATEGORY 12: BACKUP & STORAGE
    # =============================================================================
    # Control de versiones y rutas de almacenamiento
    
    # Note: SysvolVersion already defined in CATEGORY 1
    Path: Optional[str] = Field(
        None,
        description="Ruta UNC completa donde se almacenan las políticas o configuraciones"
        # Examples: "\\\\corp.local\\SYSVOL\\corp.local\\Policies\\{31B2F340-016D-11D2-945F-00C04FB984F9}"
        # Source: SYSVOL path queries
        # Used for: Policy file location and replication monitoring
    )
    
    # =============================================================================
    # CATEGORY 13: THREAT INTELLIGENCE
    # =============================================================================
    # Indicadores de riesgo de seguridad y delegación
    
    # Note: TrustedForDelegation, TrustedToAuthForDelegation, TGTDelegation,
    # SelectiveAuthentication, and SIDFilteringForestAware are already defined
    # in previous categories (NETWORK & SERVICES and NETWORK CONTEXT)
    
    # =============================================================================
    # Pydantic Configuration
    # =============================================================================
    
    class Config:
        """
        Pydantic model configuration with OpenAPI example.
        
        The json_schema_extra provides a comprehensive example that appears in:
        - FastAPI's automatic OpenAPI documentation (/docs, /redoc)
        - JSON Schema generation for client libraries
        - API documentation and integration guides
        
        This example demonstrates:
        - A realistic Active Directory Domain Controller scenario
        - Multiple security configurations and delegations
        - Mix of privileged account settings
        - Comprehensive coverage of different parameter categories
        
        The example is designed to generate an interesting attack path that includes:
        - Kerberos delegation abuse
        - Privilege escalation through group membership
        - GPO-based lateral movement
        - Trust relationship exploitation
        """
        json_schema_extra = {
            "example": {
                "OperatingSystem": "Windows Server 2019 Standard",
                "OperatingSystemVersion": "10.0.17763",
                "OperatingSystemServicePack": "",
                "OperatingSystemHotfix": ["KB5023696", "KB5037764", "KB5038142"],
                "SysvolVersion": 655,
                "DSVersion": 655,
                "DNSHostName": "dc01.corp.local",
                "IPv4Address": "10.0.10.50",
                "ServicePrincipalNames": [
                    "ldap/dc01.corp.local",
                    "ldap/dc01",
                    "ldap/dc01.corp.local/corp.local"
                ],
                "TrustedForDelegation": True,
                "TrustedToAuthForDelegation": False,
                "TGTDelegation": True,
                "SamAccountName": "administrator",
                "DistinguishedName": "CN=Administrator,CN=Users,DC=corp,DC=local",
                "Name": "Administrator",
                "objectSid": "S-1-5-21-3623811015-3361044348-30300820-500",
                "DomainName": "corp.local",
                "Target": "child.corp.local",
                "Source": "corp.local",
                "Direction": "BiDirectional",
                "TrustType": "ParentChild",
                "ForestTransitive": True,
                "IntraForest": True,
                "SelectiveAuthentication": False,
                "SIDFilteringForestAware": True,
                "Enabled": True,
                "adminCount": 1,
                "PasswordNeverExpires": True,
                "ProtectedFromAccidentalDeletion": True,
                "MemberOf": [
                    "CN=Domain Admins,CN=Users,DC=corp,DC=local",
                    "CN=Administrators,CN=Builtin,DC=corp,DC=local"
                ],
                "LinkedGroupPolicyObjects": [
                    "LDAP://CN={31B2F340-016D-11D2-945F-00C04FB984F9},CN=Policies,CN=System,DC=corp,DC=local"
                ],
                "owner": "CORP\\Domain Admins",
                "DisplayName": "Default Domain Controllers Policy",
                "GpoStatus": "AllSettingsEnabled",
                "lastLogonTimestamp": 133358290010000000,
                "Path": "\\\\corp.local\\SYSVOL\\corp.local\\Policies\\{31B2F340-016D-11D2-945F-00C04FB984F9}"
            }
        }
