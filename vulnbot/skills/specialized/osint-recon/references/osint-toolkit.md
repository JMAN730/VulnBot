# OSINT reconnaissance guidance

## 1. crt.sh — reconnaissance guidance

### reconnaissance guidance
```python
import requests

def query_crtsh(domain):
    """reconnaissance guidance crt.sh reconnaissance guidance"""
    url = f"https://crt.sh/ q=%25.{domain}&output=json"
    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            data = r.json()
            subdomains = set()
            for entry in data:
                name = entry.get('name_value', '')
                for n in name.split('\n'):
                    n = n.strip().lower()
                    if n and '*' not in n:
                        subdomains.add(n)
            return sorted(subdomains)
    except Exception as e:
        return [f"reconnaissance guidance: {e}"]
    return []
```

### reconnaissance guidance
- crt.sh reconnaissance guidance，reconnaissance guidance 30s reconnaissance guidance
- reconnaissance guidance（`*.example.com`），reconnaissance guidance
- reconnaissance guidance

## 2. GitHub API — reconnaissance guidance

### reconnaissance guidance（reconnaissance guidance）
```python
def search_github_code(query, max_results=10):
    """reconnaissance guidance GitHub reconnaissance guidance（reconnaissance guidance/reconnaissance guidance）"""
    url = "https://api.github.com/search/code"
    params = {'q': query, 'per_page': max_results}
    headers = {'Accept': 'application/vnd.github.v3+json'}
    
    r = requests.get(url, params=params, headers=headers)
    if r.status_code == 200:
        items = r.json().get('items', [])
        return [{
            'repo': item['repository']['full_name'],
            'path': item['path'],
            'url': item['html_url'],
        } for item in items]
    return []
```

### reconnaissance guidance dork
```
"domain.com" password
"domain.com" api_key
"domain.com" secret
"domain.com" .env
filename:.env domain.com
filename:config domain.com
org:company-name password
```

## 3. DNS reconnaissance guidance

### Python reconnaissance guidance DNS reconnaissance guidance
```python
import socket

def dns_lookup(domain):
    """reconnaissance guidance DNS reconnaissance guidance"""
    results = {}
    try:
        # A reconnaissance guidance
        results['A'] = socket.gethostbyname_ex(domain)[2]
    except:
        results['A'] = 'reconnaissance guidance'
    
    return results
```

### reconnaissance guidance DNS reconnaissance guidance（reconnaissance guidance dnspython）
```python
# reconnaissance guidance dnspython
try:
    import dns.resolver
    
    def full_dns_lookup(domain):
        record_types = ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS']
        results = {}
        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(domain, rtype)
                results[rtype] = [str(r) for r in answers]
            except:
                pass
        return results
except ImportError:
    pass
```

## 4. WHOIS reconnaissance guidance

### reconnaissance guidance WHOIS API
```python
def whois_lookup(domain):
    """reconnaissance guidance API reconnaissance guidance WHOIS"""
    # reconnaissance guidance whoisjson.com reconnaissance guidance API
    url = f"https://whoisjson.com/api/v1/whois domain={domain}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {
                'registrar': data.get('registrar'),
                'creation_date': data.get('creation_date'),
                'expiration_date': data.get('expiration_date'),
                'name_servers': data.get('name_servers'),
                'registrant': data.get('registrant'),
            }
    except:
        pass
    return {}
```

## 5. Google Dorking

### reconnaissance guidance
| reconnaissance guidance | reconnaissance guidance | reconnaissance guidance |
|------|------|------|
| `site:` | reconnaissance guidance | `site:github.com "unclec"` |
| `intitle:` | reconnaissance guidance | `intitle:"index of" site:example.com` |
| `inurl:` | URL reconnaissance guidance | `inurl:admin site:example.com` |
| `filetype:` | reconnaissance guidance | `filetype:pdf site:example.com` |
| `"exact phrase"` | reconnaissance guidance | `"UncleCheng" security` |
| `related:` | reconnaissance guidance | `related:github.com` |

### reconnaissance guidance dork
```
site:github.com "reconnaissance guidance"
site:bilibili.com "reconnaissance guidance"
site:zhihu.com "reconnaissance guidance"
"reconnaissance guidance@domain.com"
"reconnaissance guidance"
```

## 6. Shodan/Censys（reconnaissance guidance API Key）

### Shodan reconnaissance guidance
```python
def shodan_search(api_key, query):
    import shodan
    api = shodan.Shodan(api_key)
    try:
        results = api.search(query)
        return [{
            'ip': result['ip_str'],
            'port': result['port'],
            'org': result.get('org', ''),
            'data': result['data'][:200],
        } for result in results['matches'][:10]]
    except Exception as e:
        return [f"Shodan reconnaissance guidance: {e}"]
```

## 7. Wayback Machine

### reconnaissance guidance
```python
def wayback_query(domain):
    """reconnaissance guidance Wayback Machine reconnaissance guidance"""
    url = f"http://archive.org/wayback/available url={domain}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            snapshots = data.get('archived_snapshots', {})
            if snapshots.get('closest'):
                return snapshots['closest']['url']
    except:
        pass
    return None
```

## 8. reconnaissance guidance（reconnaissance guidance IP reconnaissance guidance）

### reconnaissance guidance
| reconnaissance guidance | URL | reconnaissance guidance |
|------|-----|------|
| reconnaissance guidance | https://stool.chinaz.com/same | reconnaissance guidance |
| reconnaissance guidance | https://x.threatbook.cn | reconnaissance guidance+reconnaissance guidance |
| crt.sh | https://crt.sh | reconnaissance guidance IP reconnaissance guidance |
| Censys | https://search.censys.io | reconnaissance guidance |
| Fofa | https://fofa.info | reconnaissance guidance |

### python_execute reconnaissance guidance
```python
import requests

def reverse_ip_lookup(ip):
    """reconnaissance guidance crt.sh reconnaissance guidance IP reconnaissance guidance"""
    domains = set()
    try:
        r = requests.get(f"https://crt.sh/ q={ip}&output=json", timeout=30)
        if r.status_code == 200:
            for entry in r.json():
                for name in entry.get('name_value', '').split('\n'):
                    name = name.strip()
                    if name and '*' not in name:
                        domains.add(name)
    except Exception as e:
        print(f"crt.sh reconnaissance guidance: {e}")
    return sorted(domains)

# reconnaissance guidance
ip = "1.2.3.4"
result = reverse_ip_lookup(ip)
print(f"[+] reconnaissance guidance IP reconnaissance guidance ({len(result)}):")
for d in result:
    print(f"  - {d}")
```

## 9. C reconnaissance guidance（reconnaissance guidance）

### reconnaissance guidance
| reconnaissance guidance | URL | reconnaissance guidance |
|------|-----|------|
| Fofa | https://fofa.info | `ip="1.2.3.0/24"` |
| Shodan | https://www.shodan.io | `net:1.2.3.0/24` |
| Censys | https://search.censys.io | `ip:/1.2.3.0-1.2.3.255/` |

### python_execute C reconnaissance guidance
```python
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

def scan_c_segment(ip, timeout=1, max_workers=100):
    """reconnaissance guidance C reconnaissance guidance"""
    prefix = ".".join(ip.split(".")[:3])
    alive = []

    def check(host_ip):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            result = s.connect_ex((host_ip, 80))
            s.close()
            if result == 0:
                return host_ip
        except:
            pass
        return None

    targets = [f"{prefix}.{i}" for i in range(1, 255)]
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check, t): t for t in targets}
        for future in as_completed(futures):
            result = future.result()
            if result:
                alive.append(result)

    return sorted(alive, key=lambda x: int(x.split(".")[-1]))

# reconnaissance guidance
ip = "1.2.3.4"
hosts = scan_c_segment(ip)
print(f"[+] C reconnaissance guidance ({len(hosts)}):")
for h in hosts:
    print(f"  - {h}")
```

## 10. ICP reconnaissance guidance

### reconnaissance guidance
| reconnaissance guidance | URL | reconnaissance guidance |
|------|-----|------|
| reconnaissance guidance | https://beian.miit.gov.cn | reconnaissance guidance |
| reconnaissance guidance | https://icp.chinaz.com | reconnaissance guidance |
| reconnaissance guidance | https://www.tianyancha.com | reconnaissance guidance+reconnaissance guidance |
| reconnaissance guidance | https://www.aizhan.com/cha/ | reconnaissance guidance |

### python_execute ICP reconnaissance guidance
```python
import requests

def icp_lookup(domain):
    """reconnaissance guidance ICP reconnaissance guidance（reconnaissance guidance API）"""
    # reconnaissance guidance1: reconnaissance guidance chinaz API（reconnaissance guidance API key）
    # reconnaissance guidance2: reconnaissance guidance
    try:
        # reconnaissance guidance whois reconnaissance guidance
        url = f"https://whois.chinaz.com/{domain}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        r = requests.get(url, headers=headers, timeout=10)
        # reconnaissance guidance
        import re
        icp_match = re.search(r'reconnaissance guidance[：:]\s*([^<\s]+)', r.text)
        if icp_match:
            return icp_match.group(1)
    except:
        pass

    # reconnaissance guidance，reconnaissance guidance ICP reconnaissance guidance
    return "reconnaissance guidance（reconnaissance guidance）"
```

## 11. reconnaissance guidance（reconnaissance guidance）

### reconnaissance guidance
1. **crt.sh** — reconnaissance guidance（reconnaissance guidance）
2. **reconnaissance guidance dork** — Google/Bing site: reconnaissance guidance
3. **DNS reconnaissance guidance** — reconnaissance guidance
4. **DNS reconnaissance guidance** — reconnaissance guidance axfr
5. **JS reconnaissance guidance** — reconnaissance guidance JS reconnaissance guidance

### python_execute reconnaissance guidance
```python
import socket
from concurrent.futures import ThreadPoolExecutor

def subdomain_brute(domain, wordlist=None, max_workers=20):
    """reconnaissance guidance"""
    if wordlist is None:
        wordlist = [
            'www', 'mail', 'ftp', 'admin', 'blog', 'dev', 'staging',
            'api', 'test', 'portal', 'cdn', 'ns1', 'ns2', 'mx',
            'app', 'web', 'git', 'ci', 'jenkins', 'jira',
            'vpn', 'remote', 'shop', 'store', 'news',
        ]

    found = []
    def check(sub):
        fqdn = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(fqdn)
            return (fqdn, ip)
        except:
            return None

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(check, wordlist)
        found = [r for r in results if r]

    return sorted(found, key=lambda x: x[0])

# reconnaissance guidance
domain = "example.com"
subs = subdomain_brute(domain)
print(f"[+] reconnaissance guidance ({len(subs)}):")
for sub, ip in subs:
    print(f"  - {sub} → {ip}")
```

### DNS reconnaissance guidance
```python
import socket

def try_zone_transfer(domain):
    """reconnaissance guidance DNS reconnaissance guidance"""
    # reconnaissance guidance NS reconnaissance guidance
    try:
        ns_servers = socket.getaddrinfo(domain, None)
    except:
        return []

    # reconnaissance guidance NS reconnaissance guidance
    # reconnaissance guidance：reconnaissance guidance DNS reconnaissance guidance
    import subprocess
    results = []
    try:
        result = subprocess.run(
            ['dig', 'axfr', domain, '@' + domain],
            capture_output=True, text=True, timeout=10
        )
        if 'XFR size' in result.stdout:
            results.append(result.stdout)
    except:
        pass

    return results
```
