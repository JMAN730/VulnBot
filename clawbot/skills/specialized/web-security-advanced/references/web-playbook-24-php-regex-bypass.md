# PHP web security testing guidance

## web security testing guidance

PHP web security testing guidance `preg_match()` web security testing guidance，web security testing guidance。
web security testing guidance PHP web security testing guidance。

## 1. web security testing guidance

**web security testing guidance**: web security testing guidance `i`（PCRE_CASELESS）web security testing guidance

```php
// web security testing guidance — web security testing guidance i web security testing guidance
preg_match("/n|c/m", $_GET['p']);  // web security testing guidance n web security testing guidance c

// web security testing guidance — web security testing guidance
// nss2 web security testing guidance n → web security testing guidance
// Nss2 web security testing guidance N → web security testing guidance n → web security testing guidance！
// Ctf web security testing guidance C → web security testing guidance c → web security testing guidance！

// PHP web security testing guidance
call_user_func('Nss2::Ctf');  // web security testing guidance nss2::ctf()
```

**web security testing guidance**: web security testing guidance `i` web security testing guidance，web security testing guidance

## 2. web security testing guidance

**web security testing guidance**: web security testing guidance，web security testing guidance false

```php
// preg_match() web security testing guidance
// web security testing guidance → web security testing guidance false + Warning → web security testing guidance

// URL:  p[]=nss2&p[]=ctf
// $_GET['p'] = ['nss2', 'ctf']  (web security testing guidance)
// preg_match("/n|c/m", ['nss2', 'ctf']) → false → web security testing guidance！

// call_user_func web security testing guidance
call_user_func(['nss2', 'ctf']);  // web security testing guidance nss2::ctf()
```

## 3. web security testing guidance

**web security testing guidance**: web security testing guidance `^...$` web security testing guidance + `m` web security testing guidance

```php
// web security testing guidance：m web security testing guidance /n/ web security testing guidance
// m web security testing guidance ^ web security testing guidance $ web security testing guidance（web security testing guidance）

// web security testing guidance：
preg_match("/^flag$/", $input);  // m web security testing guidance %0aflag web security testing guidance

// web security testing guidance：
preg_match("/n|c/m", $input);    // m web security testing guidance n web security testing guidance c web security testing guidance
```

## 4. PCRE web security testing guidance

**web security testing guidance**: web security testing guidance + web security testing guidance

```php
// preg_match web security testing guidance 1000000
// web security testing guidance false（web security testing guidance 0 web security testing guidance 1）

// web security testing guidance
$str = str_repeat('a', 1000000);
preg_match("/.*$/", $str);  // web security testing guidance false → web security testing guidance
```

## 5. `%0a` web security testing guidance

**web security testing guidance**: web security testing guidance `^...$` web security testing guidance `s`（DOTALL）web security testing guidance

```php
// web security testing guidance ^...$ web security testing guidance
// web security testing guidance: "good\nmalicious"
preg_match("/^good$/", "good\nmalicious");  // web security testing guidance m web security testing guidance
preg_match("/^good$/m", "good\nmalicious");  // web security testing guidance m web security testing guidance
```

## web security testing guidance CTF web security testing guidance

| web security testing guidance | web security testing guidance | web security testing guidance |
|------|----------|----------|
| web security testing guidance | `/n\|c/m` | `Nss2::Ctf`（web security testing guidance） |
| web security testing guidance | `/system\|exec/` | `p[]=class&p[]=method`（web security testing guidance） |
| web security testing guidance | `/^flag$/` | `flag%0a` web security testing guidance `%0aflag`（web security testing guidance） |
| web security testing guidance | `/.*/` | web security testing guidance PCRE web security testing guidance |
| web security testing guidance | `/flag/` | `flflagag`（web security testing guidance，web security testing guidance str_replace） |

## call_user_func web security testing guidance

```php
// web security testing guidance
call_user_func('readfile', 'flag.php');

// web security testing guidance（web security testing guidance）
call_user_func('Nss2::Ctf');  // web security testing guidance

// web security testing guidance（web security testing guidance）
call_user_func(['Nss2', 'Ctf']);  // web security testing guidance

// web security testing guidance
call_user_func([$obj, 'method']);
```

## ⚠️ web security testing guidance

1. **`call_user_func('readfile')` web security testing guidance** — web security testing guidance，web security testing guidance `call_user_func('readfile', 'flag.php')`
2. **web security testing guidance `m` web security testing guidance `i` web security testing guidance** — `m` web security testing guidance，`i` web security testing guidance
3. **web security testing guidance PHP web security testing guidance** — `preg_match` web security testing guidance `false`，web security testing guidance `0`
4. **web security testing guidance flag web security testing guidance** — web security testing guidance，web security testing guidance
