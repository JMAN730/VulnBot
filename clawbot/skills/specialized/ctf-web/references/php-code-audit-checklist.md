# PHP web security testing guidance Checklist

## web security testing guidance：web security testing guidance

### web security testing guidance
```php
$_GET['param']        // URL web security testing guidance
$_POST['param']       // POST web security testing guidance
$_REQUEST['param']    // GET + POST + COOKIE
$_COOKIE['param']     // Cookie web security testing guidance
$_SERVER['HTTP_X']    // HTTP web security testing guidance
$_FILES['file']       // web security testing guidance
$_SESSION['key']      // Session web security testing guidance（web security testing guidance）
```

### web security testing guidance
```php
php://input           // POST web security testing guidance
getallheaders()       // web security testing guidance HTTP web security testing guidance
getenv()              // web security testing guidance
file_get_contents()   // web security testing guidance/URL web security testing guidance
```

## web security testing guidance：web security testing guidance

### web security testing guidance
```php
eval()                // web security testing guidance PHP web security testing guidance
assert()              // PHP < 7 web security testing guidance
preg_replace(/e)      // /e web security testing guidance
create_function()     // web security testing guidance
call_user_func()      // web security testing guidance
call_user_func_array()// web security testing guidance（web security testing guidance
array_map()           // web security testing guidance
usort()               // web security testing guidance（web security testing guidance
array_filter()        // web security testing guidance（web security testing guidance
```

### web security testing guidance
```php
system()              // web security testing guidance，web security testing guidance
exec()                // web security testing guidance，web security testing guidance
shell_exec()          // web security testing guidance，web security testing guidance
passthru()            // web security testing guidance，web security testing guidance
popen()               // web security testing guidance
proc_open()           // web security testing guidance（web security testing guidance
pcntl_exec()          // web security testing guidance（web security testing guidance pcntl web security testing guidance
web security testing guidance `cmd`           // web security testing guidance shell_exec()
```

### web security testing guidance
```php
include() / require()          // web security testing guidance
include_once() / require_once()
file_get_contents()            // web security testing guidance
file_put_contents()            // web security testing guidance
fopen() + fread()              // web security testing guidance
readfile()                     // web security testing guidance
highlight_file() / show_source()// web security testing guidance
unlink()                       // web security testing guidance
rename()                       // web security testing guidance
copy()                         // web security testing guidance
move_uploaded_file()           // web security testing guidance
```

### web security testing guidance
```php
unserialize()        // web security testing guidance
__wakeup()           // web security testing guidance
__destruct()         // web security testing guidance
__toString()         // web security testing guidance
__call()             // web security testing guidance
__get()              // web security testing guidance
```

## web security testing guidance：web security testing guidance/web security testing guidance

### web security testing guidance
```php
preg_match("/pattern/flags", $input)

□ web security testing guidance i web security testing guidance？  → web security testing guidance → web security testing guidance
□ web security testing guidance m web security testing guidance？  → web security testing guidance → web security testing guidance ^$
□ web security testing guidance s web security testing guidance？  → web security testing guidance → . web security testing guidance
□ web security testing guidance？ → web security testing guidance
□ web security testing guidance？  → PCRE web security testing guidance
```

### web security testing guidance
```php
str_replace()        // web security testing guidance（web security testing guidance）
str_ireplace()       // web security testing guidance
strstr() / strpos()  // web security testing guidance（web security testing guidance / web security testing guidance）
strlen()             // web security testing guidance（web security testing guidance）
in_array()           // web security testing guidance（web security testing guidance）
is_numeric()         // web security testing guidance（web security testing guidance/web security testing guidance）
intval()             // web security testing guidance（web security testing guidance）
trim()               // web security testing guidance（%0a%0d web security testing guidance）
htmlspecialchars()   // HTML web security testing guidance（web security testing guidance）
addslashes()         // web security testing guidance（web security testing guidance/GBK web security testing guidance）
mysql_real_escape_string() // web security testing guidance（web security testing guidance/GBK web security testing guidance）
```

## web security testing guidance：web security testing guidance

```
web security testing guidance → [web security testing guidanceA] → [web security testing guidanceB] → web security testing guidance
          ↓
          web security testing guidance？
          ↓ web security testing guidance
          [web security testing guidance] → web security testing guidance
```

### web security testing guidance
1. **web security testing guidance**
2. **web security testing guidance**（3 web security testing guidance < 5 web security testing guidance）
3. **web security testing guidance**（system() web security testing guidance exec()）
4. **web security testing guidance**（web security testing guidance < web security testing guidance < web security testing guidance）

## web security testing guidance：web security testing guidance

### web security testing guidance
```
1. system() web security testing guidance → web security testing guidance HTTP web security testing guidance
2. exec() web security testing guidance → web security testing guidance echo
3. eval() + system() → web security testing guidance eval web security testing guidance
4. highlight_file() + system() → web security testing guidance
```

### web security testing guidance
```php
// web security testing guidance
system('id');
system('echo TESTFLAG123');
// web security testing guidance HTTP web security testing guidance TESTFLAG123
```

### web security testing guidance
```python
# web security testing guidance python_execute web security testing guidance
import requests
r = requests.get(url, params=payload)
print(f"Status: {r.status_code}")
print(f"Length: {len(r.text)}")
print(f"Headers: {dict(r.headers)}")
# web security testing guidance N web security testing guidance（flag web security testing guidance）
print(f"Tail: {r.text[-500:]}")
# web security testing guidance flag web security testing guidance
import re
flags = re.findall(r'(NSSCTF\{[^}]+\}|flag\{[^}]+\}|CTF\{[^}]+\})', r.text)
if flags:
    print(f"FLAG FOUND: {flags}")
```
