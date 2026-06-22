# CTF Web web security testing guidance

## web security testing guidance flag web security testing guidance

### Linux
```
/flag
/flag.txt
/flag.php
/var/www/html/flag.php
/home/ctf/flag
/root/flag
/tmp/flag
/opt/flag
/srv/flag
```

### Docker/web security testing guidance
```
/proc/self/environ
/environment
/.env
```

### PHP web security testing guidance
```php
// phpinfo() web security testing guidance flag
// web security testing guidance
// web security testing guidance

// web security testing guidance flag web security testing guidance
flag.php
flag.txt
f1ag.php
fl4g.php
fl@g.php
th1s_1s_flag.php
```

## First-Pass web security testing guidance

```
1. web security testing guidance URL
   → web security testing guidance（Ctrl+U）
   → web security testing guidance HTTP web security testing guidance（Server, X-Powered-By, Set-Cookie）
   → web security testing guidance Cookie web security testing guidance（base64/JWT/web security testing guidance）

2. web security testing guidance
   → robots.txt
   → .git/HEAD
   → .svn/
   → backup web security testing guidance：index.php.bak, www.zip, .index.php.swp, index.php~
   → DS_Store: .DS_Store

3. web security testing guidance
   → /flag, /admin, /login, /upload, /api, /debug
   → /phpinfo.php, /info.php, /test.php
   → /console (Flask Debug), /actuator (Spring Boot)

4. web security testing guidance → web security testing guidance
   → web security testing guidance php-code-audit-checklist.md

5. web security testing guidance → web security testing guidance
   → SQL web security testing guidance
   → XSS web security testing guidance
   → web security testing guidance
   → SSTI web security testing guidance
   → LFI/RFI
```

## web security testing guidance

```bash
# web security testing guidance
curl -I http://target/              # HTTP web security testing guidance
curl http://target/robots.txt        # robots
curl http://target/.git/HEAD         # git web security testing guidance

# web security testing guidance
' OR 1=1 --                          # SQLi
{{7*7}}                              # SSTI
<script>alert(1)</script>            # XSS
../../../etc/passwd                  # LFI
```

## web security testing guidance Hint

| web security testing guidance | web security testing guidance | web security testing guidance |
|--------|------|--------|
| `X-Forwarded-For: 127.0.0.1` | web security testing guidance | web security testing guidance X-Forwarded-For web security testing guidance |
| `Server: nginx/1.x` | web security testing guidance | web security testing guidance CVE |
| `X-Powered-By: PHP/7.x` | PHP web security testing guidance | PHP web security testing guidance |
| `Set-Cookie: role=guest` | web security testing guidance | web security testing guidance Cookie |
| `Hint: xxx` | web security testing guidance | web security testing guidance |
| `Flag: xxx` | web security testing guidance | web security testing guidance |

## web security testing guidance

### PHP web security testing guidance
```
URL → web security testing guidance → web security testing guidance → web security testing guidance → RCE → web security testing guidance flag
```

### PHP web security testing guidance
```
web security testing guidance → web security testing guidance hint → web security testing guidance → web security testing guidance → web security testing guidance → web security testing guidance → RCE
```

### web security testing guidance
```
LFI → web security testing guidance（php://filter） → web security testing guidance → web security testing guidance/Sessionweb security testing guidance → RCE
```

### SQL web security testing guidance
```
web security testing guidance → SQLi → web security testing guidance → web security testing guidance → web security testing guidance → web security testing guidance Webshell → RCE
```

### web security testing guidance
```
web security testing guidance → web security testing guidance Gadgets → web security testing guidance → RCE/SSRF/web security testing guidance
```

## web security testing guidance/web security testing guidance

| web security testing guidance | web security testing guidance | web security testing guidance |
|------|---------|---------|
| web security testing guidance `=` | Base64 | `crypto_decode base64_decode` |
| `0-9a-f` web security testing guidance | Hex | `crypto_decode hex_decode` |
| `%XX` | URL web security testing guidance | `crypto_decode url_decode` |
| `&#xNN;` | HTML web security testing guidance | `crypto_decode html_decode` |
| `\uXXXX` | Unicode web security testing guidance | `crypto_decode unicode_decode` |
| web security testing guidance `.` web security testing guidance | JWT | `crypto_decode jwt_decode` |
| web security testing guidance | Morse | `crypto_decode morse_decode` |
| web security testing guidance | ROT13/Caesar | `crypto_decode rot13_decode` |
