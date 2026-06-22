# Web web security testing guidance - web security testing guidance

> web security testing guidance: WooYun web security testing guidance | web security testing guidance web-file-infra.md

## web security testing guidance、web security testing guidance

### 3.1 web security testing guidance

```
web security testing guidance: web security testing guidance -> web security testing guidance -> web security testing guidance
web security testing guidance: web security testing guidance
      web security testing guidance -> web security testing guidance -> web security testing guidance -> web security testing guidance -> web security testing guidance
```

### 3.2 web security testing guidance

web security testing guidance:

```bash
# Gitweb security testing guidance (web security testing guidance)
/.git/config          # web security testing guidance
/.git/HEAD            # web security testing guidance
/.git/index           # web security testing guidance
/.git/logs/HEAD       # web security testing guidance

# SVNweb security testing guidance
/.svn/entries         # SVN 1.6web security testing guidance
/.svn/wc.db           # SVN 1.7+ SQLiteweb security testing guidance

# web security testing guidance: dvcs-ripper, GitHack, svn-extractor
```

web security testing guidance:

```bash
# web security testing guidance (530web security testing guidance)
/wwwroot.rar | /www.zip | /web.rar | /backup.zip | /site.tar.gz
/{domain}.zip | /{domain}.rar

# SQLweb security testing guidance (136web security testing guidance)
/backup.sql | /database.sql | /db.sql | /dump.sql

# web security testing guidance (101web security testing guidance)
/config.php.bak | /web.config.bak | /.env.bak
/config_global.php.bak
```

web security testing guidance:

```bash
# web security testing guidance
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

web security testing guidance/web security testing guidance/web security testing guidance:

```bash
# web security testing guidance
/phpinfo.php | /info.php | /test.php | /probe.php

# web security testing guidance
/ctp.log | /logs/ctp.log | /debug.log | /storage/logs/

# web security testing guidance
/phpmyadmin/ | /pma/ | /adminer.php
/swagger-ui.html | /api-docs
/actuator/env                    # Spring Boot
```

### 3.3 web security testing guidance

```
Phase 1 web security testing guidance: web security testing guidance(Server/X-Powered-By) -> web security testing guidance -> robots.txt -> web security testing guidance/JS
Phase 2 web security testing guidance: web security testing guidance(.git/.svn) -> web security testing guidance(web security testing guidance/web security testing guidance) -> web security testing guidance
Phase 3 web security testing guidance: Google Hackingweb security testing guidance
```

Google Hackingweb security testing guidance:

```
site:target.com filetype:sql | filetype:bak | filetype:zip
site:target.com filetype:env | filetype:log
site:target.com inurl:.git | inurl:.svn
site:target.com inurl:phpinfo | intitle:phpinfo
site:target.com "db_password" | "mysql_connect"
```

### 3.4 web security testing guidance

```
web security testing guidance   -> web security testing guidance -> web security testing guidance -> web security testing guidance -> web security testing guidance
web security testing guidance   -> web security testing guidance -> SQLweb security testing guidance  -> web security testing guidance   -> web security testing guidancegetshell
web security testing guidance   -> DBweb security testing guidance -> web security testing guidance    -> web security testing guidance   -> web security testing guidance
web security testing guidance   -> Session  -> web security testing guidance  -> web security testing guidance   -> web security testing guidance
APIweb security testing guidance    -> web security testing guidance/web security testing guidance -> web security testing guidance     -> web security testing guidance   -> web security testing guidance
web security testing guidance -> web security testing guidance/OSS -> web security testing guidance    -> web security testing guidance   -> web security testing guidance
```

### 3.5 web security testing guidance

Nginxweb security testing guidance:

```nginx
location ~ /\.(git|svn|env|htaccess|htpasswd) { deny all; return 404; }
location ~ \.(bak|sql|log|config|ini|yml)$ { deny all; return 404; }
location ~* /(backup|bak|old|temp|test|dev)/ { deny all; return 404; }
autoindex off;
server_tokens off;
```

Apacheweb security testing guidance:

```apache
<FilesMatch "\.(git|svn|env|bak|sql|log|config)">
    Order Allow,Deny
    Deny from all
</FilesMatch>
Options -Indexes
ServerSignature Off
```

CI/CDweb security testing guidance: web security testing guidance -> web security testing guidance.git/.svnweb security testing guidance -> web security testing guidance

---

