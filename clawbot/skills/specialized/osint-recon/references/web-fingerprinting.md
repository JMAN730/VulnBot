# Web web security testing guidance

## web security testing guidance

### HTTP web security testing guidance
| web security testing guidance | web security testing guidance | web security testing guidance |
|--------|---------|------|
| `Server` | Web web security testing guidance | `nginx/1.18.0`、`Apache/2.4.41`、`GitHub.com` |
| `X-Powered-By` | web security testing guidance/web security testing guidance | `PHP/7.4.3`、`Express`、`Next.js` |
| `X-AspNet-Version` | .NET web security testing guidance | `4.0.30319` |
| `Set-Cookie` | web security testing guidance | `PHPSESSID`→PHP、`JSESSIONID`→Java、`csrf_token`→Django |
| `X-Generator` | CMS | `Hugo`、`WordPress`、`Ghost` |
| `X-DRupal-Cache` | CMS | Drupal |
| `Via` | web security testing guidance/CDN | `1.1 varnish`→Varnish CDN |

### HTML web security testing guidance
```python
import re

# WordPress
wp_signs = ['wp-content', 'wp-includes', 'wordpress']
# Hexo
hexo_signs = ['hexo', 'hexo-theme']
# Hugo
hugo_signs = ['hugo', 'gohugo']
# Jekyll
jekyll_signs = ['jekyll']
# Next.js
next_signs = ['__NEXT_DATA__', '_next/']
# Vue
vue_signs = ['data-v-', '__vue__']
# React
react_signs = ['data-reactroot', '__react']

def detect_framework(html):
    html_lower = html.lower()
    frameworks = []
    checks = {
        'WordPress': wp_signs,
        'Hexo': hexo_signs,
        'Hugo': hugo_signs,
        'Jekyll': jekyll_signs,
        'Next.js': next_signs,
        'Vue': vue_signs,
        'React': react_signs,
    }
    for name, signs in checks.items():
        if any(s in html_lower for s in signs):
            frameworks.append(name)
    return frameworks
```

### JavaScript web security testing guidance
- web security testing guidance JS web security testing guidance：`/wp-includes/js/` → WordPress
- Vue/React DevTools web security testing guidance：`__VUE_DEVTOOLS_GLOBAL_HOOK__`、`__REACT_DEVTOOLS_GLOBAL_HOOK__`
- web security testing guidance JS web security testing guidance

### CSS web security testing guidance
- `/wp-content/themes/` → WordPress
- Hexo web security testing guidance class web security testing guidance
- Bootstrap/Tailwind class web security testing guidance

### web security testing guidance
| web security testing guidance | web security testing guidance |
|---------|---------|
| `/robots.txt` | CMS web security testing guidance、web security testing guidance |
| `/sitemap.xml` | web security testing guidance |
| `/favicon.ico` | web security testing guidance |
| `/.well-known/security.txt` | web security testing guidance |
| `/humans.txt` | web security testing guidance |
| `/.git/HEAD` | Git web security testing guidance |
| `/.env` | web security testing guidance |

## GitHub Pages web security testing guidance
- web security testing guidance `Server: GitHub.com`
- `X-GitHub-Request-Id` web security testing guidance
- `X-Cache: HIT` + `X-Fastly-Request-ID` → Fastly CDN
- `Via: 1.1 varnish` → Varnish web security testing guidance
- web security testing guidance：Jekyll、Hexo、Hugo

---

## WAF web security testing guidance

### web security testing guidance WAF web security testing guidance
| WAF | web security testing guidance/web security testing guidance | web security testing guidance |
|-----|----------------|-----------|
| Cloudflare | `Server: cloudflare`, `CF-Ray` | 403 |
| AWS WAF | `x-amz-request-id`, `x-amz-cf-id` | 403 |
| web security testing guidance WAF | Cookie web security testing guidance `acw_tc` | 405/403 |
| web security testing guidance WAF | web security testing guidance JSON web security testing guidance | 403 |
| web security testing guidance WAF | web security testing guidance "web security testing guidance" | 403 |
| web security testing guidance | web security testing guidance "safedog" | 403/404 |
| ModSecurity | web security testing guidance 403 + Server web security testing guidance | 403 |
| Nginx WAF | `HTTP/1.1 444` web security testing guidance 403 | 444/403 |

### WAF web security testing guidance
1. **web security testing guidance vs web security testing guidance** — web security testing guidance，web security testing guidance
2. **web security testing guidance** — web security testing guidance WAF web security testing guidance
3. **Cookie web security testing guidance** — web security testing guidance WAF web security testing guidance Cookie
4. **web security testing guidance** — web security testing guidance（403/406/429/444）

### web security testing guidance WAF web security testing guidance payload
```
/ id=1' OR 1=1--
/ search=<script>alert(1)</script>
/../../../etc/passwd
/ file=php://filter/convert.base64-encode/resource=index
```

---

## web security testing guidance

### web security testing guidance
| web security testing guidance | web security testing guidance | web security testing guidance | web security testing guidance |
|------|------|---------|---------|
| Git web security testing guidance | `/.git/config`, `/.git/HEAD` | 200 web security testing guidance git web security testing guidance | 🔴 Critical |
| SVN web security testing guidance | `/.svn/entries` | 200 web security testing guidance svn web security testing guidance | 🔴 Critical |
| .DS_Store | `/.DS_Store` | web security testing guidance | 🟡 Medium |
| .env web security testing guidance | `/.env` | web security testing guidance DB_PASSWORD web security testing guidance | 🔴 Critical |
| web.config | `/web.config` | IIS web security testing guidance | 🟡 Medium |
| web security testing guidance | `/.bak`, `/.swp`, `/.old`, `/.tar.gz` | web security testing guidance | 🟡 Medium |
| Docker | `/Dockerfile`, `/docker-compose.yml` | web security testing guidance | 🟡 Medium |
| package.json | `/package.json` | Node.js web security testing guidance | 🟢 Low |
| composer.json | `/composer.json` | PHP web security testing guidance | 🟢 Low |
| webpack | `/webpack.json`, `/map Files` | web security testing guidance | 🟡 Medium |

### Git web security testing guidance
1. web security testing guidance `/.git/HEAD` → web security testing guidance ref web security testing guidance
2. web security testing guidance `/.git/config` → web security testing guidance
3. web security testing guidance `/.git/objects/` → web security testing guidance Git web security testing guidance
4. web security testing guidance GitHack/scrabble web security testing guidance

### web security testing guidance
```
/.git/config
/.git/HEAD
/.svn/entries
/.DS_Store
/.env
/.env.bak
/.env.local
/web.config
/config.php
/config.yml
/backup.sql
/database.sql
/db.sql
/phpinfo.php
/test/
/debug/
/console/
/admin/
/wp-config.php
/robots.txt
/sitemap.xml
/.well-known/security.txt
```
