---
name: osint-recon
description: OSINT reconnaissance guidance — reconnaissance guidance（reconnaissance guidance→reconnaissance guidance→reconnaissance guidance→reconnaissance guidance），reconnaissance guidance（reconnaissance guidance）reconnaissance guidance
---

# OSINT reconnaissance guidance

reconnaissance guidance/reconnaissance guidance/reconnaissance guidance，reconnaissance guidance**reconnaissance guidance**（reconnaissance guidance → reconnaissance guidance → reconnaissance guidance → reconnaissance guidance），reconnaissance guidance。

**reconnaissance guidance `recon` Skill reconnaissance guidance**：
- `recon` → reconnaissance guidance（reconnaissance guidance、DNS、reconnaissance guidance）— reconnaissance guidance
- `osint-recon` → reconnaissance guidance（reconnaissance guidance + reconnaissance guidance + reconnaissance guidance + reconnaissance guidance/reconnaissance guidance）— reconnaissance guidance

## reconnaissance guidance

1. **reconnaissance guidance** — reconnaissance guidance/reconnaissance guidance/reconnaissance guidance，reconnaissance guidance
2. **reconnaissance guidance** — reconnaissance guidance HTTP reconnaissance guidance，reconnaissance guidance HTML reconnaissance guidance、JS reconnaissance guidance、reconnaissance guidance
3. **reconnaissance guidance** — reconnaissance guidance、DNS、WHOIS（reconnaissance guidance），reconnaissance guidance/reconnaissance guidance（reconnaissance guidance）
4. **reconnaissance guidance** — reconnaissance guidance ✅，reconnaissance guidance ❌，reconnaissance guidance [DONE]
5. **reconnaissance guidance** — reconnaissance guidance
6. **reconnaissance guidance** — reconnaissance guidance Markdown reconnaissance guidance

## reconnaissance guidance

### reconnaissance guidance：reconnaissance guidance
| reconnaissance guidance | reconnaissance guidance/reconnaissance guidance | reconnaissance guidance |
|--------|----------|------|
| reconnaissance guidance & reconnaissance guidance | MCP nmap / `python_execute` + socket | reconnaissance guidance（21/22/80/443/3306/6379/8080/8443） |
| reconnaissance guidance IP reconnaissance guidance | DNS reconnaissance guidance / reconnaissance guidance Ping / reconnaissance guidance | CDN reconnaissance guidance IP — SecurityTrails/DNSHistory/reconnaissance guidancePing |
| reconnaissance guidance | TTL reconnaissance guidance + nmap OS reconnaissance guidance | Linux TTL≈64, Windows TTL≈128, Unix TTL≈255 |
| reconnaissance guidance | reconnaissance guidance Server + reconnaissance guidance + reconnaissance guidance | Apache/Nginx/IIS/Tomcat reconnaissance guidance |
| reconnaissance guidance | reconnaissance guidance + reconnaissance guidance + reconnaissance guidance | MySQL(3306)/Redis(6379)/MongoDB(27017)/MSSQL(1433) |

### reconnaissance guidance：reconnaissance guidance
| reconnaissance guidance | reconnaissance guidance/reconnaissance guidance | reconnaissance guidance |
|--------|----------|------|
| reconnaissance guidance | reconnaissance guidance + reconnaissance guidance + JS reconnaissance guidance | OS + reconnaissance guidance + reconnaissance guidance + reconnaissance guidance + reconnaissance guidance → reconnaissance guidance |
| Web reconnaissance guidance | `fetch` + reconnaissance guidance | CMS reconnaissance guidance、reconnaissance guidance、JS reconnaissance guidance、reconnaissance guidance |
| WAF reconnaissance guidance | wafw00f reconnaissance guidance + reconnaissance guidance | reconnaissance guidance/reconnaissance guidance/reconnaissance guidance |
| reconnaissance guidance & reconnaissance guidance | `python_execute` + reconnaissance guidance | /admin /backup /config /api /robots.txt /sitemap.xml |
| reconnaissance guidance | reconnaissance guidance | .git/.svn/.DS_Store/.env/web.config/reconnaissance guidance(.bak/.swp/.old) |
| reconnaissance guidance | reconnaissance guidance IP reconnaissance guidance | reconnaissance guidance/reconnaissance guidance/crt.sh reconnaissance guidance IP reconnaissance guidance |
| C reconnaissance guidance | reconnaissance guidance | nmap -sn reconnaissance guidance /24 reconnaissance guidance |

### reconnaissance guidance：reconnaissance guidance
| reconnaissance guidance | reconnaissance guidance/reconnaissance guidance | reconnaissance guidance |
|--------|----------|------|
| WHOIS reconnaissance guidance | `python_execute` + whois API/reconnaissance guidance | reconnaissance guidance/reconnaissance guidance/NS reconnaissance guidance/reconnaissance guidance/reconnaissance guidance |
| ICP reconnaissance guidance | reconnaissance guidance API | reconnaissance guidance，reconnaissance guidance |
| reconnaissance guidance | crt.sh + reconnaissance guidance + reconnaissance guidance + DNS reconnaissance guidance | reconnaissance guidance，reconnaissance guidance |
| DNS reconnaissance guidance | `python_execute` + dnspython/socket | A/CNAME/MX/TXT/NS/SPF/SOA reconnaissance guidance |
| reconnaissance guidance | crt.sh / Censys / certspotter | reconnaissance guidance、reconnaissance guidance、reconnaissance guidance |

### reconnaissance guidance：reconnaissance guidance ⚡ reconnaissance guidance
**⚠️ reconnaissance guidance：**
- reconnaissance guidance"reconnaissance guidance/reconnaissance guidance/reconnaissance guidance/reconnaissance guidance/reconnaissance guidance"reconnaissance guidance
- reconnaissance guidance（meta author、about reconnaissance guidance、reconnaissance guidance）

**reconnaissance guidance**：reconnaissance guidance / reconnaissance guidance"reconnaissance guidance" / reconnaissance guidance IP/reconnaissance guidance

| reconnaissance guidance | reconnaissance guidance | reconnaissance guidance |
|----------|------|------|
| reconnaissance guidance | reconnaissance guidance meta author、about reconnaissance guidance | reconnaissance guidance、reconnaissance guidance、reconnaissance guidance |
| GitHub reconnaissance guidance | `fetch` + GitHub API | reconnaissance guidance、reconnaissance guidance、reconnaissance guidance、reconnaissance guidance |
| reconnaissance guidance | reconnaissance guidance → reconnaissance guidance | Breconnaissance guidance、reconnaissance guidance、reconnaissance guidance、Twitter、LinkedIn |
| reconnaissance guidance | reconnaissance guidance/reconnaissance guidance | reconnaissance guidance ID reconnaissance guidance |
| reconnaissance guidance | GitHub commits → reconnaissance guidance | reconnaissance guidance |
| reconnaissance guidance | GitHub reconnaissance guidance | .env、config、reconnaissance guidance |

## First-Pass reconnaissance guidance

1. **reconnaissance guidance** → `fetch` reconnaissance guidance，reconnaissance guidance HTTP reconnaissance guidance + HTML reconnaissance guidance
2. **reconnaissance guidance：reconnaissance guidance** → reconnaissance guidance、reconnaissance guidance IP、OS reconnaissance guidance、reconnaissance guidance/reconnaissance guidance
3. **reconnaissance guidance：reconnaissance guidance** → Web reconnaissance guidance、WAF reconnaissance guidance、reconnaissance guidance/reconnaissance guidance、reconnaissance guidance/Creconnaissance guidance
4. **reconnaissance guidance：reconnaissance guidance** → WHOIS、ICP reconnaissance guidance、reconnaissance guidance、DNS reconnaissance guidance、reconnaissance guidance
5. **reconnaissance guidance（reconnaissance guidance）** → reconnaissance guidance、reconnaissance guidance、reconnaissance guidance
6. **reconnaissance guidance** → reconnaissance guidance
7. **reconnaissance guidance** → reconnaissance guidance Markdown reconnaissance guidance

## reconnaissance guidance

| reconnaissance guidance | reconnaissance guidance | reconnaissance guidance |
|------|---------|---------|
| reconnaissance guidance | `server-recon.md` | reconnaissance guidance、reconnaissance guidance IP、OS reconnaissance guidance、reconnaissance guidance/reconnaissance guidance |
| reconnaissance guidance | `website-recon.md` | reconnaissance guidance/reconnaissance guidance/WAF/reconnaissance guidance/reconnaissance guidance/reconnaissance guidance/Creconnaissance guidance |
| Web reconnaissance guidance | `web-fingerprinting.md` | reconnaissance guidance、reconnaissance guidance、reconnaissance guidance |
| reconnaissance guidance | `author-tracking.md` | reconnaissance guidance → reconnaissance guidance → reconnaissance guidance |
| OSINT reconnaissance guidance | `osint-toolkit.md` | crt.sh、GitHub API、reconnaissance guidance dork、reconnaissance guidance/Creconnaissance guidance/ICP |
| reconnaissance guidance | `social-engineering-intel.md` | reconnaissance guidance、reconnaissance guidance、reconnaissance guidance |
| reconnaissance guidance | `recon-report-template.md` | reconnaissance guidance Markdown reconnaissance guidance（reconnaissance guidance） |

## ⭐ reconnaissance guidance

### reconnaissance guidance HTML reconnaissance guidance
```python
import re
html = "..."  # fetch reconnaissance guidance HTML
links = re.findall(r'href=["\'](https ://[^"\']+)["\']', html)
for link in set(links):
    print(link)
```

### reconnaissance guidance HTML reconnaissance guidance
```python
import re
# meta author
author = re.findall(r'<meta\s+name=["\']author["\']\s+content=["\']([^"\']+)["\']', html)
# about reconnaissance guidance
about_links = re.findall(r'href=["\']([^"\']*( :about|me|contact)[^"\']*)["\']', html, re.I)
```

### reconnaissance guidance crt.sh reconnaissance guidance
```python
import requests
domain = "example.com"
r = requests.get(f"https://crt.sh/ q=%.{domain}&output=json")
if r.status_code == 200:
    for entry in r.json():
        print(entry['name_value'])
```

### GitHub reconnaissance guidance
```python
import requests
username = "target_user"
r = requests.get(f"https://api.github.com/users/{username}")
if r.status_code == 200:
    data = r.json()
    print(f"Name: {data.get('name')}")
    print(f"Bio: {data.get('bio')}")
    print(f"Email: {data.get('email')}")
    print(f"Blog: {data.get('blog')}")
    print(f"Location: {data.get('location')}")
    print(f"Company: {data.get('company')}")
```

### WAF reconnaissance guidance（reconnaissance guidance）
```python
import requests
url = "https://target.com"
# reconnaissance guidance
r1 = requests.get(url)
# reconnaissance guidance WAF reconnaissance guidance（reconnaissance guidance）
r2 = requests.get(url + "/ id=1' OR 1=1--")
# reconnaissance guidance
if r1.status_code != r2.status_code or len(r1.text) != len(r2.text):
    print("[!] reconnaissance guidance WAF")
    print(f"reconnaissance guidance: {r1.status_code}, reconnaissance guidance: {r2.status_code}")
```

### reconnaissance guidance（reconnaissance guidance IP reconnaissance guidance）
```python
import requests
ip = "1.2.3.4"
# reconnaissance guidance chinaz API reconnaissance guidance
# reconnaissance guidance crt.sh reconnaissance guidance IP reconnaissance guidance
r = requests.get(f"https://crt.sh/ q={ip}&output=json")
```
