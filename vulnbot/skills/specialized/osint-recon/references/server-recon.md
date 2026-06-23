# reconnaissance guidance

## 1. reconnaissance guidance & reconnaissance guidance

### nmap reconnaissance guidance
```bash
# reconnaissance guidance（reconnaissance guidance）
nmap -p- -sV <target>

# reconnaissance guidance
nmap -sV -top-ports 1000 <target>

# UDP reconnaissance guidance
nmap -sU --top-ports 100 <target>

# reconnaissance guidance + OS reconnaissance guidance
nmap -sV -O <target>
```

### python_execute reconnaissance guidance（reconnaissance guidance nmap reconnaissance guidance）
```python
import socket

def scan_port(host, port, timeout=2):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((host, port))
        s.close()
        return result == 0
    except:
        return False

host = "target.com"
common_ports = [21,22,23,25,53,80,110,143,443,445,993,995,1433,1521,3306,3389,5432,6379,8080,8443,9200,27017]
open_ports = [p for p in common_ports if scan_port(host, p)]
print(f"reconnaissance guidance: {open_ports}")
```

### reconnaissance guidance（Banner Grabbing）
```python
import socket

def grab_banner(host, port, timeout=3):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        # HTTP reconnaissance guidance banner
        if port in [80, 443, 8080, 8443]:
            s.send(b"HEAD / HTTP/1.1\r\nHost: " + host.encode() + b"\r\n\r\n")
        else:
            s.send(b"\r\n")
        banner = s.recv(1024).decode('utf-8', errors='ignore')
        s.close()
        return banner[:200]
    except:
        return None
```

## 2. reconnaissance guidance IP reconnaissance guidance（CDN reconnaissance guidance IP）

### reconnaissance guidance：DNS reconnaissance guidance
- SecurityTrails (https://securitytrails.com/dns-trials)
- DNSHistory (https://dnshistory.org)
- ViewDNS (https://viewdns.info/iphistory/)
- Netcraft Site Report (https://sitereport.netcraft.com/)

### reconnaissance guidance：reconnaissance guidance Ping
```python
import requests
# reconnaissance guidance Ping reconnaissance guidance
urls = [
    f"https://www.whatsmydns.net/#A/{domain}",
    f"https://ping.pe/{domain}",
    f"https://tools.keycdn.com/curl url={domain}",
]
# reconnaissance guidance IP，reconnaissance guidance CDN
# reconnaissance guidance IP，reconnaissance guidance IP reconnaissance guidance
```

### reconnaissance guidance：reconnaissance guidance
- reconnaissance guidance/reconnaissance guidance，reconnaissance guidance
- reconnaissance guidance `Received:` reconnaissance guidance
- reconnaissance guidance IP

### reconnaissance guidance：reconnaissance guidance
- CDN reconnaissance guidance
- reconnaissance guidance（reconnaissance guidance mail.ftp.dev.staging）reconnaissance guidance IP
- reconnaissance guidance A reconnaissance guidance，reconnaissance guidance CDN IP

### reconnaissance guidance：SSL reconnaissance guidance
```python
import requests
domain = "target.com"
r = requests.get(f"https://crt.sh/ q=%.{domain}&output=json")
if r.status_code == 200:
    # reconnaissance guidance IP
    for entry in r.json():
        print(entry.get('name_value', ''))
```

## 3. reconnaissance guidance

### TTL reconnaissance guidance
| TTL reconnaissance guidance | reconnaissance guidance |
|--------|-------------|
| ≈ 64 | Linux / Unix / macOS |
| ≈ 128 | Windows |
| ≈ 255 | reconnaissance guidance / reconnaissance guidance Unix |

```python
import subprocess
# Ping reconnaissance guidance TTL
result = subprocess.run(['ping', '-c', '1', host], capture_output=True, text=True)
# Windows: ping -n 1 host
# reconnaissance guidance TTL
import re
ttl_match = re.search(r'TTL[=:]\s*(\d+)', result.output, re.I)
if ttl_match:
    ttl = int(ttl_match.group(1))
    if ttl <= 64:
        print("reconnaissance guidance: Linux/Unix")
    elif ttl <= 128:
        print("reconnaissance guidance: Windows")
    else:
        print("reconnaissance guidance: reconnaissance guidance")
```

### nmap OS reconnaissance guidance
```bash
nmap -O <target>
# reconnaissance guidance（reconnaissance guidance root）
sudo nmap -O --osscan-guess <target>
```

## 4. reconnaissance guidance

### HTTP reconnaissance guidance
```
Server: Apache/2.4.49 (Ubuntu)
Server: nginx/1.18.0
Server: Microsoft-IIS/10.0
X-Powered-By: PHP/7.4.3
X-Powered-By: Express
X-AspNet-Version: 4.0.30319
```

### reconnaissance guidance
- Apache: reconnaissance guidance 404 reconnaissance guidance "Apache" reconnaissance guidance
- Nginx: reconnaissance guidance 404 reconnaissance guidance "nginx" reconnaissance guidance
- IIS: reconnaissance guidance IIS reconnaissance guidance
- Tomcat: reconnaissance guidance 404 reconnaissance guidance Apache Tomcat reconnaissance guidance

### reconnaissance guidance
```python
import requests
target = "https://target.com"
# Apache
r = requests.get(f"{target}/server-status")  # 403 = reconnaissance guidance
r = requests.get(f"{target}/server-info")    # 403 = reconnaissance guidance
# Nginx
r = requests.get(f"{target}/nginx_status")   # reconnaissance guidance
# Tomcat
r = requests.get(f"{target}/manager/html")   # reconnaissance guidance
# IIS
r = requests.get(f"{target}/aspnet_client/") # ASP.NET reconnaissance guidance
```

## 5. reconnaissance guidance

### reconnaissance guidance
| reconnaissance guidance | reconnaissance guidance | reconnaissance guidance |
|--------|---------|------|
| MySQL | 3306 | reconnaissance guidance |
| PostgreSQL | 5432 | reconnaissance guidance Rails/Django |
| MSSQL | 1433 | Windows reconnaissance guidance |
| MongoDB | 27017 | NoSQL |
| Redis | 6379 | reconnaissance guidance/reconnaissance guidance |
| Oracle | 1521 | reconnaissance guidance |
| Memcached | 11211 | reconnaissance guidance |

### reconnaissance guidance
- MySQL: `You have an error in your SQL syntax`
- PostgreSQL: `ERROR: syntax error at or near`
- MSSQL: `Microsoft SQL Server`
- Oracle: `ORA-01756`

### python_execute reconnaissance guidance
```python
import socket

def check_db(host, port, timeout=2):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        # reconnaissance guidance banner
        s.send(b"\r\n")
        banner = s.recv(1024)
        s.close()
        return banner.hex()[:40], banner[:100]
    except:
        return None, None

db_ports = {
    3306: "MySQL", 5432: "PostgreSQL", 1433: "MSSQL",
    27017: "MongoDB", 6379: "Redis", 1521: "Oracle",
}
for port, name in db_ports.items():
    hex_banner, banner = check_db(host, port)
    if hex_banner:
        print(f"[+] {name} ({port}): {banner}")
```
