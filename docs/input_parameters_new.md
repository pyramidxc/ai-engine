# input_parameters_new.md

---

## 1. CORE SYSTEM INFO

| Parameter                    | Type        | Description                                 | Examples                                  |
| ---------------------------- | ----------- | ------------------------------------------- | ----------------------------------------- |
| `OperatingSystem`            | `str`       | Sistema operativo detectado en el equipo.   | `Windows Server 2019 Standard`            |
| `OperatingSystemVersion`     | `str`       | Versión del sistema operativo.              | `10.0.17763`                              |
| `OperatingSystemServicePack` | `str`       | Service Pack instalado en el sistema.       | `Service Pack 2`                          |
| `OperatingSystemHotfix`      | `list[str]` | Lista de actualizaciones o KB instaladas.   | `["KB5021234", "KB5030015", "KB5037764"]` |
| `SysvolVersion`              | `int`       | Versión de la política replicada en SYSVOL. | `655`                                     |
| `DSVersion`                  | `int`       | Versión del objeto en el Directorio Activo. | `655`                                     |

---

## 2. NETWORK & SERVICES

| Parameter                    | Type        | Description                                                                        | Examples                                                     |
| ---------------------------- | ----------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| `DNSHostName`                | `str`       | Nombre FQDN completo del equipo.                                                   | `web01.corp.local`                                           |
| `IPv4Address`                | `str`       | Dirección IPv4 asignada al host.                                                   | `10.0.10.50`                                                 |
| `ServicePrincipalNames`      | `list[str]` | SPNs (Service Principal Names) asociados a la cuenta.                              | `["MSSQLSvc/db01.corp.local:1433", "HTTP/web01.corp.local"]` |
| `TrustedForDelegation`       | `bool`      | Indica si la cuenta o equipo está marcado como confiable para delegación Kerberos. | `true`                                                       |
| `TrustedToAuthForDelegation` | `bool`      | Permite autenticación delegada para servicios específicos.                         | `false`                                                      |
| `TGTDelegation`              | `bool`      | Indica si se permite la delegación de tickets TGT entre dominios.                  | `true`                                                       |

---

## 3. ASSET IDENTIFICATION

| Parameter           | Type  | Description                                         | Examples                                      |
| ------------------- | ----- | --------------------------------------------------- | --------------------------------------------- |
| `SamAccountName`    | `str` | Nombre de cuenta único en el dominio.               | `administrator`                               |
| `DistinguishedName` | `str` | Nombre distinguido completo (DN) del objeto en AD.  | `CN=John Doe,OU=Usuarios,DC=corp,DC=local`    |
| `Name`              | `str` | Nombre descriptivo del objeto.                      | `John Doe`                                    |
| `objectSid`         | `str` | Identificador de seguridad (SID) del objeto.        | `S-1-5-21-3623811015-3361044348-30300820-500` |
| `id`                | `str` | Identificador único (GUID) de la GPO u otro objeto. | `{31B2F340-016D-11D2-945F-00C04FB984F9}`      |
| `DomainName`        | `str` | Nombre del dominio al que pertenece el objeto.      | `corp.local`                                  |

---

## 4. NETWORK CONTEXT

| Parameter                 | Type   | Description                                                         | Examples           |
| ------------------------- | ------ | ------------------------------------------------------------------- | ------------------ |
| `Target`                  | `str`  | Dominio de destino de la relación de confianza.                     | `child.corp.local` |
| `Source`                  | `str`  | Dominio de origen de la relación de confianza.                      | `corp.local`       |
| `Direction`               | `str`  | Dirección de la relación de confianza.                              | `BiDirectional`    |
| `TrustType`               | `str`  | Tipo de confianza configurada entre dominios.                       | `Forest`           |
| `ForestTransitive`        | `bool` | Indica si la relación de confianza es transitiva a nivel de bosque. | `true`             |
| `IntraForest`             | `bool` | Indica si la relación de confianza es interna al mismo bosque.      | `true`             |
| `SelectiveAuthentication` | `bool` | Requiere autenticación selectiva para el trust.                     | `false`            |
| `SIDFilteringForestAware` | `bool` | Filtrado SID activo en la relación de confianza.                    | `true`             |

---

## 5. SECURITY CONTROLS

| Parameter                         | Type   | Description                                             | Examples                                                                              |
| --------------------------------- | ------ | ------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `Enabled`                         | `bool` | Indica si la cuenta u objeto está habilitado.           | `true`                                                                                |
| `adminCount`                      | `int`  | Define si el objeto está marcado como privilegiado.     | `1`                                                                                   |
| `PasswordNeverExpires`            | `bool` | Contraseña configurada para no expirar.                 | `true`                                                                                |
| `ProtectedFromAccidentalDeletion` | `bool` | Protección contra eliminación accidental habilitada.    | `true`                                                                                |
| `nTSecurityDescriptor`            | `str`  | Descriptor de seguridad del objeto con ACLs detalladas. | `(A;;RPWPCCDCLCRCSWRCWDWOGA;;;S-1-5-21-3623811015-3361044348-30300820-500)`           |
| `WmiFilter`                       | `str`  | Filtro WMI aplicado en la GPO.                          | `SELECT * FROM Win32_OperatingSystem WHERE Version >= '10.0.0' AND ProductType = '1'` |

---

## 6. IDENTITY & ACCESS

| Parameter                  | Type        | Description                                                    | Examples                                                                                          |
| -------------------------- | ----------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `MemberOf`                 | `list[str]` | Lista de grupos de los que el usuario es miembro.              | `["CN=Domain Admins,CN=Users,DC=corp,DC=local", "CN=IT Support,CN=Users,DC=corp,DC=local"]`       |
| `Members`                  | `list[str]` | Lista de miembros directos de un grupo.                        | `["CORP\\alice", "CORP\\bob", "CORP\\svc_sql"]`                                                   |
| `LinkedGroupPolicyObjects` | `list[str]` | GPOs asociadas o vinculadas al objeto.                         | `["LDAP://CN={31B2F340-016D-11D2-945F-00C04FB984F9},CN=Policies,CN=System,DC=corp,DC=local"]`     |
| `gPLink`                   | `list[str]` | Enlaces de políticas aplicados a una unidad organizativa (OU). | `["[LDAP://CN={A1B2C3D4-1111-2222-3333-444455556666},CN=Policies,CN=System,DC=corp,DC=local;0]"]` |
| `owner`                    | `str`       | Propietario del objeto o política.                             | `CORP\\Domain Admins`                                                                             |
| `ManagedBy`                | `str`       | Objeto o cuenta que administra la OU o GPO.                    | `CN=OU-Admins,OU=Groups,DC=corp,DC=local`                                                         |

---

## 7. SOFTWARE & APPLICATIONS

| Parameter     | Type        | Description                                             | Examples                                                                           |
| ------------- | ----------- | ------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `DisplayName` | `str`       | Nombre descriptivo de la GPO.                           | `Default Domain Policy`                                                            |
| `computer`    | `list[str]` | Secciones de configuración de equipo dentro de la GPO.  | `["Scripts", "Security", "Registry"]`                                              |
| `user`        | `list[str]` | Secciones de configuración de usuario dentro de la GPO. | `["Scripts", "Preferences", "Folders"]`                                            |
| `path`        | `str`       | Ruta completa LDAP del objeto.                          | `CN={31B2F340-016D-11D2-945F-00C04FB984F9},CN=Policies,CN=System,DC=corp,DC=local` |

---

## 8. PATCH & VULNERABILITY MANAGEMENT

| Parameter               | Type        | Description                                   | Examples                                  |
| ----------------------- | ----------- | --------------------------------------------- | ----------------------------------------- |
| `OperatingSystemHotfix` | `list[str]` | Lista detallada de parches instalados.        | `["KB5023696", "KB5037764", "KB5038142"]` |
| `SysvolVersion`         | `int`       | Versión actual de la política en SYSVOL.      | `655`                                     |
| `DSVersion`             | `int`       | Versión sincronizada en el Directorio Activo. | `655`                                     |

---

## 9. CONFIGURATION & COMPLIANCE

| Parameter              | Type   | Description                                   | Examples                                                                                |
| ---------------------- | ------ | --------------------------------------------- | --------------------------------------------------------------------------------------- |
| `GpoStatus`            | `str`  | Estado de la GPO en el dominio.               | `AllSettingsEnabled`                                                                    |
| `Enabled`              | `bool` | Indica si el objeto está activo o inactivo.   | `true`                                                                                  |
| `WmiFilter`            | `str`  | Consulta WMI usada como filtro de aplicación. | `SELECT * FROM Win32_OperatingSystem WHERE Version >= '10.0.17763'`                     |
| `nTSecurityDescriptor` | `str`  | Descriptor de seguridad completo con ACLs.    | `(A;;RPWPCRLC;;;S-1-5-32-544)(A;;RPWP;;;S-1-5-21-1111111111-2222222222-3333333333-500)` |

---

## 10. ASSET CONTEXT & RISK

| Parameter            | Type        | Description                                           | Examples                                                                                               |
| -------------------- | ----------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `lastLogonTimestamp` | `int`       | Timestamp del último inicio de sesión.                | `133358290010000000`                                                                                   |
| `MemberOf`           | `list[str]` | Grupos que influyen en el nivel de riesgo del objeto. | `["CN=Administrators,CN=Builtin,DC=corp,DC=local", "CN=Backup Operators,CN=Builtin,DC=corp,DC=local"]` |
| `adminCount`         | `int`       | Indica privilegio administrativo (riesgo alto).       | `1`                                                                                                    |

---

## 11. CLOUD & CONTAINERS

| Parameter | Type | Description                                                                                     | Examples |
| --------- | ---- | ----------------------------------------------------------------------------------------------- | -------- |
| —         | —    | No se identificaron campos relacionados con entornos cloud o contenedores en los JSON actuales. | —        |

---

## 12. BACKUP & STORAGE

| Parameter       | Type  | Description                                                           | Examples                                                                             |
| --------------- | ----- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `SysvolVersion` | `int` | Versión del SYSVOL replicado para control de integridad.              | `655`                                                                                |
| `Path`          | `str` | Ruta UNC completa donde se almacenan las políticas o configuraciones. | `\\corp.local\\SYSVOL\\corp.local\\Policies\\{31B2F340-016D-11D2-945F-00C04FB984F9}` |

---

## 13. THREAT INTELLIGENCE

| Parameter                    | Type   | Description                                                    | Examples |
| ---------------------------- | ------ | -------------------------------------------------------------- | -------- |
| `TrustedForDelegation`       | `bool` | Indica que la cuenta puede impersonar identidades en Kerberos. | `true`   |
| `TrustedToAuthForDelegation` | `bool` | Permite autenticación delegada hacia servicios.                | `false`  |
| `SelectiveAuthentication`    | `bool` | Controla autenticación selectiva en trusts.                    | `true`   |
| `SIDFilteringForestAware`    | `bool` | Filtro SID habilitado para evitar abuso de SIDs falsos.        | `true`   |
| `TGTDelegation`              | `bool` | Permite delegación de tickets TGT (potencial riesgo lateral).  | `true`   |

---

## additional parameters found in examples

| Parameter                         | Type   | Description                                                     | Examples                                  |
| --------------------------------- | ------ | --------------------------------------------------------------- | ----------------------------------------- |
| `ForestTransitive`                | `bool` | Indica si la relación de confianza es transitiva entre bosques. | `true`                                    |
| `ManagedBy`                       | `str`  | Cuenta o grupo administrador de la OU o GPO.                    | `CN=OU-Admins,OU=Groups,DC=corp,DC=local` |
| `ProtectedFromAccidentalDeletion` | `bool` | Habilita la protección contra eliminación accidental.           | `true`                                    |
| `DisplayName`                     | `str`  | Nombre completo del objeto GPO.                                 | `Default Domain Controllers Policy`       |

---

## Complete Example Request

```json
{
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
  "TrustedForDelegation": true,
  "TrustedToAuthForDelegation": false,
  "TGTDelegation": true,
  "SamAccountName": "administrator",
  "DistinguishedName": "CN=Administrator,CN=Users,DC=corp,DC=local",
  "Name": "Administrator",
  "objectSid": "S-1-5-21-3623811015-3361044348-30300820-500",
  "id": "{6AC1786C-016F-11D2-945F-00C04fB984F9}",
  "DomainName": "corp.local",
  "Target": "child.corp.local",
  "Source": "corp.local",
  "Direction": "BiDirectional",
  "TrustType": "ParentChild",
  "ForestTransitive": true,
  "IntraForest": true,
  "SelectiveAuthentication": false,
  "SIDFilteringForestAware": true,
  "Enabled": true,
  "adminCount": 1,
  "PasswordNeverExpires": true,
  "ProtectedFromAccidentalDeletion": true,
  "nTSecurityDescriptor": "(A;;RPWPCCDCLCRCSWRCWDWOGA;;;S-1-5-21-3623811015-3361044348-30300820-500)",
  "WmiFilter": "SELECT * FROM Win32_OperatingSystem WHERE Version >= '10.0.17763'",
  "MemberOf": [
    "CN=Domain Admins,CN=Users,DC=corp,DC=local",
    "CN=Administrators,CN=Builtin,DC=corp,DC=local",
    "CN=Enterprise Admins,CN=Users,DC=corp,DC=local"
  ],
  "Members": ["CORP\\alice", "CORP\\bob"],
  "LinkedGroupPolicyObjects": [
    "LDAP://CN={31B2F340-016D-11D2-945F-00C04FB984F9},CN=Policies,CN=System,DC=corp,DC=local",
    "LDAP://CN={6AC1786C-016F-11D2-945F-00C04fB984F9},CN=Policies,CN=System,DC=corp,DC=local"
  ],
  "gPLink": [
    "[LDAP://CN={31B2F340-016D-11D2-945F-00C04FB984F9},CN=Policies,CN=System,DC=corp,DC=local;0]"
  ],
  "owner": "CORP\\Domain Admins",
  "ManagedBy": "CN=IT-Admins,OU=Groups,DC=corp,DC=local",
  "DisplayName": "Default Domain Controllers Policy",
  "computer": ["Scripts", "Security", "Registry", "Administrative Templates"],
  "user": ["Scripts", "Preferences", "Administrative Templates"],
  "path": "CN={31B2F340-016D-11D2-945F-00C04FB984F9},CN=Policies,CN=System,DC=corp,DC=local",
  "GpoStatus": "AllSettingsEnabled",
  "lastLogonTimestamp": 133358290010000000,
  "Path": "\\\\corp.local\\SYSVOL\\corp.local\\Policies\\{31B2F340-016D-11D2-945F-00C04FB984F9}"
}
```

---

## Minimal Example Request

```json
{
  "OperatingSystem": "Windows Server 2019",
  "DNSHostName": "dc01.corp.local",
  "DomainName": "corp.local"
}
```

---

## Example Scenarios

### Scenario 1: Domain Controller with Delegation

```json
{
  "OperatingSystem": "Windows Server 2019 Standard",
  "OperatingSystemVersion": "10.0.17763",
  "DNSHostName": "dc01.corp.local",
  "IPv4Address": "10.0.10.50",
  "DomainName": "corp.local",
  "SamAccountName": "DC01$",
  "DistinguishedName": "CN=DC01,OU=Domain Controllers,DC=corp,DC=local",
  "ServicePrincipalNames": ["ldap/dc01.corp.local", "ldap/dc01"],
  "TrustedForDelegation": true,
  "adminCount": 1,
  "Enabled": true,
  "MemberOf": ["CN=Domain Controllers,CN=Users,DC=corp,DC=local"]
}
```

### Scenario 2: Privileged User Account

```json
{
  "SamAccountName": "admin.jdoe",
  "DistinguishedName": "CN=John Doe (Admin),OU=Admin Accounts,DC=corp,DC=local",
  "Name": "John Doe (Admin)",
  "objectSid": "S-1-5-21-3623811015-3361044348-30300820-1105",
  "DomainName": "corp.local",
  "Enabled": true,
  "adminCount": 1,
  "PasswordNeverExpires": false,
  "MemberOf": [
    "CN=Domain Admins,CN=Users,DC=corp,DC=local",
    "CN=Schema Admins,CN=Users,DC=corp,DC=local"
  ],
  "lastLogonTimestamp": 133358290010000000
}
```

### Scenario 3: Service Account with SPNs (Kerberoasting Target)

```json
{
  "SamAccountName": "svc_sql",
  "DistinguishedName": "CN=SQL Service Account,OU=Service Accounts,DC=corp,DC=local",
  "Name": "SQL Service Account",
  "objectSid": "S-1-5-21-3623811015-3361044348-30300820-2201",
  "DomainName": "corp.local",
  "ServicePrincipalNames": [
    "MSSQLSvc/sql01.corp.local:1433",
    "MSSQLSvc/sql01.corp.local"
  ],
  "Enabled": true,
  "PasswordNeverExpires": true,
  "MemberOf": ["CN=SQL Admins,OU=Groups,DC=corp,DC=local"]
}
```

## Implementation Notes

### Design Philosophy

- All fields are optional for maximum flexibility
- More context = better attack path generation
- Supports partial data from any Active Directory scanner
- Backward compatible with any subset of parameters

### Integration Points

The API accepts this model at the following endpoint:

- **POST** `/attack-path` → Returns Markdown-formatted attack path

### Data Sources

These parameters are typically collected from:

- **Active Directory:** BloodHound, PowerView, ADExplorer
- **LDAP Queries:** Direct AD enumeration
- **Group Policy:** GPO reports, GPMC exports
- **Security Tools:** PingCastle, Purple Knight
- **Native Commands:** `Get-ADUser`, `Get-ADComputer`, `Get-GPO`

---

## Source Files Referenced

1. `app/models/host.py` - Primary model definition
2. `app/core/prompts.py` - AD reconnaissance summary builder
3. `app/services/orchestrator.py` - Validation and orchestration
4. `examples/requests/ad_domain_controller.json` - Complete example

---

**Document Version:** 2.0  
**Last Updated:** 2025-11-10  
**AI Engine Version:** 7.2.0  
**Total Parameters Documented:** 40+
