# web security testing guidance

## 1. web security testing guidance

### web security testing guidance
1. **HTTP web security testing guidance** — Server、X-Powered-By、Set-Cookie web security testing guidance
2. **HTML web security testing guidance** — meta generator、web security testing guidance class/id web security testing guidance
3. **JS web security testing guidance** — /static/js/app.js、/wp-content/、/assets/
4. **Cookie web security testing guidance** — PHPSESSID(php)、JSESSIONID(Java)、_rails_session(Rails)
5. **URL web security testing guidance** —  id= (PHP)、/api/ (REST)、/wp-admin/ (WordPress)

### web security testing guidance
| web security testing guidance | web security testing guidance | web security testing guidance | web security testing guidance | web security testing guidance |
|------|------|--------|--------|------|
| PHP | Laravel | MySQL | Apache/Nginx | Set-Cookie: laravel_session |
| PHP | WordPress | MySQL | Apache | /wp-content/, /wp-admin/ |
| Python | Django | PostgreSQL | Nginx+Gunicorn | CSRF middleware cookie |
| Python | Flask | SQLite/MySQL | Nginx+uWSGI | Set-Cookie: session= |
| Java | Spring | MySQL/Oracle | Tomcat | JSESSIONID |
| Node.js | Express | MongoDB | Nginx | X-Powered-By: Express |
| Ruby | Rails | PostgreSQL | Nginx+Puma | _rails_session |

### python_execute web security testing guidance
```python
import requests

url = "https://target.com"
r = requests.get(url, timeout=10)

# 1. web security testing guidance
headers = r.headers
print(f"Server: {headers.get('Server', 'N/A')}")
print(f"X-Powered-By: {headers.get('X-Powered-By', 'N/A')}")

# 2. Cookie web security testing guidance
cookies = r.cookies
for cookie in cookies:
    print(f"Cookie: {cookie.name} = {cookie.value[:20]}...")

# 3. HTML web security testing guidance
html = r.text
# WordPress
if 'wp-content' in html or 'wp-includes' in html:
    print("[+] WordPress web security testing guidance")
# Laravel
if 'laravel_session' in str(cookies):
    print("[+] Laravel web security testing guidance")
# Django
if 'csrftoken' in str(cookies) or 'csrfmiddlewaretoken' in html:
    print("[+] Django web security testing guidance")
# Hexo
if 'hexo' in html.lower():
    print("[+] Hexo web security testing guidance")
# Hugo
if 'hugo' in html.lower():
    print("[+] Hugo web security testing guidance")
```

## 2. Web web security testing guidance

### CMS web security testing guidance
| CMS | web security testing guidance | web security testing guidance |
|-----|---------|-----------|
| WordPress | /wp-login.php, /wp-content/ | wp-content, xmlrpc.php |
| Joomla | /administrator/ | /media/jui/ |
| Drupal | /misc/drupal.js | Drupal.settings |
| Discuz | /forum.php | discuz_uid |
| Typecho | /admin/login.php | typecho |
| Hexo | /archives/ | hexo |
| Ghost | /ghost/ | ghost-frontend |

### web security testing guidance
| web security testing guidance | web security testing guidance |
|------|------|
| React | data-reactroot, __NEXT_DATA__ |
| Vue.js | data-v-xxx, __vue__ |
| Angular | ng-version, _nghost |
| jQuery | jQuery in scripts |
| Bootstrap | bootstrap.css/js |

### python_execute web security testing guidance
```python
import requests, re

url = "https://target.com"
r = requests.get(url, timeout=10)
html = r.text

# CMS web security testing guidance
cms_signatures = {
    "WordPress": ["wp-content", "wp-includes", "wp-admin"],
    "Joomla": ["/administrator/", "media/jui"],
    "Drupal": ["Drupal.settings", "/misc/drupal"],
    "Hexo": ["hexo", "/archives/"],
    "Hugo": ["hugo", "gohugo"],
    "Ghost": ["ghost-frontend", "/ghost/"],
}

for cms, sigs in cms_signatures.items():
    if any(sig in html for sig in sigs):
        print(f"[+] CMS: {cms}")

# web security testing guidance
fw_signatures = {
    "React": ["data-reactroot", "__NEXT_DATA__", "react"],
    "Vue.js": ["data-v-", "__vue__", "vue"],
    "Angular": ["ng-version", "_nghost", "angular"],
    "jQuery": ["jquery", "jQuery"],
    "Bootstrap": ["bootstrap"],
}

for fw, sigs in fw_signatures.items():
    if any(sig.lower() in html.lower() for sig in sigs):
        print(f"[+] web security testing guidance: {fw}")

# JS web security testing guidance
js_files = re.findall(r'src=["\']([^"\']*\.js[^"\']*)["\']', html)
print(f"JS web security testing guidance: {js_files[:10]}")
```

## 3. WAF web security testing guidance

### web security testing guidance WAF web security testing guidance
| WAF | web security testing guidance |
|-----|---------|
| Cloudflare | Server: cloudflare, CF-Ray header |
| AWS WAF | Server: AmazonS3, x-amz-request-id |
| web security testing guidance WAF | Set-Cookie web security testing guidance acw_tc |
| web security testing guidance WAF | web security testing guidance |
| web security testing guidance WAF | web security testing guidance "web security testing guidance" |
| web security testing guidance | web security testing guidance "safedog" |
| ModSecurity | web security testing guidance 403 web security testing guidance |

### python_execute WAF web security testing guidance
```python
import requests

url = "https://target.com"

# 1. web security testing guidance
r1 = requests.get(url)

# 2. web security testing guidance WAF web security testing guidance
waf_payloads = [
    "/ id=1' OR 1=1--",
    "/ search=<script>alert(1)</script>",
    "/../../../etc/passwd",
    "/ file=php://filter/convert.base64-encode/resource=index",
]

for payload in waf_payloads:
    r2 = requests.get(url + payload, allow_redirects=False)
    # web security testing guidance
    if r2.status_code in [403, 406, 429, 501]:
        print(f"[!] WAF web security testing guidance: {payload} → {r2.status_code}")
    # web security testing guidance
    if abs(len(r2.text) - len(r1.text)) > 500:
        print(f"[!] web security testing guidance: web security testing guidance={len(r1.text)}, web security testing guidance={len(r2.text)}")

# 3. web security testing guidance WAF web security testing guidance
waf_headers = {
    "cloudflare": ["cf-ray", "server: cloudflare"],
    "aws": ["x-amz-request-id", "x-amz-cf-id"],
    "web security testing guidance": ["acw_tc"],
}
for waf_name, sigs in waf_headers.items():
    for sig in sigs:
        if sig in str(r1.headers).lower():
            print(f"[+] WAF web security testing guidance: {waf_name}")
```

## 4. web security testing guidance & web security testing guidance

### web security testing guidance
```
/robots.txt
/sitemap.xml
/.git/
/.svn/
/.env
/.DS_Store
/web.config
/config.php
/config.yml
/backup/
/admin/
/login/
/api/
/swagger/
/graphql
/phpinfo.php
/test/
/debug/
/console/
/actuator/
/.well-known/
```

### python_execute web security testing guidance
```python
import requests

target = "https://target.com"
paths = [
    "/robots.txt", "/sitemap.xml", "/.git/", "/.env", "/.DS_Store",
    "/admin/", "/backup/", "/config.php", "/api/", "/phpinfo.php",
    "/.git/config", "/.git/HEAD", "/wp-config.php",
    "/swagger/", "/graphql", "/actuator/",
]

for path in paths:
    try:
        r = requests.get(target + path, timeout=5, allow_redirects=False)
        if r.status_code in [200, 301, 302, 401, 403]:
            print(f"[{r.status_code}] {path}")
    except:
        pass
```

## 5. web security testing guidance

### web security testing guidance
| web security testing guidance | web security testing guidance | web security testing guidance |
|------|------|---------|
| Git web security testing guidance | /.git/config, /.git/HEAD | 200 web security testing guidance git web security testing guidance |
| SVN web security testing guidance | /.svn/entries | 200 web security testing guidance svn web security testing guidance |
| .DS_Store | /.DS_Store | web security testing guidance |
| .env web security testing guidance | /.env | web security testing guidance DB_PASSWORD web security testing guidance |
| web.config | /web.config | IIS web security testing guidance |
| web security testing guidance | /.bak, /.swp, /.old, /~ | web security testing guidance |
| Docker | /Dockerfile, /docker-compose.yml | web security testing guidance |
| package.json | /package.json | Node.js web security testing guidance |
| composer.json | /composer.json | PHP web security testing guidance |

### Git web security testing guidance
```python
import requests

target = "https://target.com"

# 1. web security testing guidance .git/HEAD
r = requests.get(f"{target}/.git/HEAD")
if r.status_code == 200 and "ref:" in r.text:
    print("[!] Git web security testing guidance!")
    # 2. web security testing guidance ref
    ref_path = r.text.strip().split("ref: ")[1] if "ref: " in r.text else ""
    if ref_path:
        r2 = requests.get(f"{target}/.git/{ref_path}")
        if r2.status_code == 200:
            print(f"[+] Git ref: {r2.text.strip()}")

# 3. web security testing guidance config
r3 = requests.get(f"{target}/.git/config")
if r3.status_code == 200:
    print(f"[+] Git config:\n{r3.text}")
```

## 6. web security testing guidance（web security testing guidance IP web security testing guidance）

### web security testing guidance
1. **web security testing guidance** — https://stool.chinaz.com/same
2. **web security testing guidance** — https://x.threatbook.cn
3. **crt.sh** — web security testing guidance IP web security testing guidance
4. **Censys** — https://search.censys.io

### python_execute web security testing guidance
```python
import requests, json

ip = "1.2.3.4"

# web security testing guidance1: crt.sh web security testing guidance IP web security testing guidance
r = requests.get(f"https://crt.sh/ q={ip}&output=json", timeout=15)
if r.status_code == 200:
    domains = set()
    for entry in r.json():
        for name in entry.get('name_value', '').split('\n'):
            if name.strip() and '*' not in name:
                domains.add(name.strip())
    print(f"[+] web security testing guidance IP web security testing guidance ({len(domains)}):")
    for d in sorted(domains):
        print(f"  - {d}")
```

## 7. C web security testing guidance（web security testing guidance）

### python_execute C web security testing guidance
```python
import requests, socket
from concurrent.futures import ThreadPoolExecutor

# web security testing guidance IP
domain = "target.com"
ip = socket.gethostbyname(domain)
# web security testing guidance C web security testing guidance
c_segment = ".".join(ip.split(".")[:3])

def check_host(ip, timeout=1):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((ip, 80))
        s.close()
        if result == 0:
            return ip
    except:
        pass
    return None

# web security testing guidance C web security testing guidance（1-254）
alive_hosts = []
with ThreadPoolExecutor(max_workers=50) as executor:
    ips = [f"{c_segment}.{i}" for i in range(1, 255)]
    results = executor.map(check_host, ips)
    alive_hosts = [ip for ip in results if ip]

print(f"[+] C web security testing guidance: {alive_hosts}")
```
