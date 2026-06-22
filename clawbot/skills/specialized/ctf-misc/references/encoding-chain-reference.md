# CTF challenge guidance

## CTF challenge guidance

| CTF challenge guidance | CTF challenge guidance | CTF challenge guidance |
|------|------|------|
| Base64 | `A-Za-z0-9+/=`, CTF challenge guidance % 4 | `TnNTY1RmLnBocA==` |
| Base32 | `A-Z2-7=`, CTF challenge guidance % 8 | `OBZHK5DFN2A====` |
| Base16 | `0-9A-F`, CTF challenge guidance | `4E535354662E706870` |
| URL CTF challenge guidance | `%XX` | `%2F%61%64%6D%69%6E` |
| HTML CTF challenge guidance | `&#xNNN;` CTF challenge guidance `&#NNN;` | `&#x3C;script&#x3E;` |
| Unicode | `\uXXXX` CTF challenge guidance `\UXXXXXXXX` | `\u003c\u0073\u0063` |
| Hex (Python) | `\xNN` | `\x4e\x53\x53\x54` |
| ROT13 | CTF challenge guidance，Caesar | `axzc` → `nmp` |
| Morse | `.` `-` `/` CTF challenge guidance | `.-/-.../-.-.` |
| Binary | `01` CTF challenge guidance | `01001101` |

## CTF challenge guidance

### 1. CTF challenge guidance
```
Hex → Base64 → URLCTF challenge guidance
```

### 2. CTF challenge guidance
```
Binary → ASCII
Octal → ASCII
Hex → ASCII
```

### 3. CTF challenge guidance
```
HTMLCTF challenge guidance → URLCTF challenge guidance → Base64
```

### 4. CTF challenge guidance
```
Brainfuck (`><+-.,[]`)
Ook! (`Ook. Ook `)
Hex → Ook! → Brainfuck
```

## CTF challenge guidance

```python
import base64, binascii, urllib.parse, html

def auto_decode(data, max_iter=10):
    """CTF challenge guidance"""
    result = data
    for _ in range(max_iter):
        changed = False
        original = result

        # URL decode
        try:
            result = urllib.parse.unquote(result)
            if result != original:
                changed = True
        except:
            pass

        # HTML entity decode
        try:
            result = html.unescape(result)
            if result != original:
                changed = True
        except:
            pass

        # Base64 decode
        try:
            result = base64.b64decode(result).decode('utf-8')
            if result != original:
                changed = True
        except:
            try:
                result = base64.b64decode(result + '==').decode('utf-8')
                if result != original:
                    changed = True
            except:
                pass

        # Hex decode
        try:
            if all(c in '0123456789abcdefABCDEF' for c in result.replace('%', '')):
                result = bytes.fromhex(result.replace('%', '')).decode('utf-8')
                if result != original:
                    changed = True
        except:
            pass

        # ROT13
        try:
            result = original.encode().translate(bytes.maketrans(
                b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                b'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'
            )).decode()
            if result != original:
                changed = True
        except:
            pass

        if not changed:
            break

    return result
```

## CTF challenge guidance

```python
from PIL import Image
import zbarlight

def decode_qr(image_path):
    """CTF challenge guidance QR CTF challenge guidance"""
    image = Image.open(image_path)
    codes = zbarlight.scan_codes(['qrcode'], image)
    return codes
```

## CTF challenge guidance (CTF challenge guidance)

```python
def extract_lsb_wav(wav_path):
    """CTF challenge guidance WAV CTF challenge guidance LSB CTF challenge guidance"""
    import wave, struct
    with wave.open(wav_path, 'rb') as wav:
        frames = wav.readframes(wav.getnframes())
        binary = ''
        for byte in frames:
            binary += str(byte & 1)
    # CTF challenge guidance 8 CTF challenge guidance
    result = ''
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if len(byte) == 8:
            result += chr(int(byte, 2))
    return result
```

## CTF challenge guidance

```python
from PIL import Image

def extract_lsb_png(image_path):
    """CTF challenge guidance PNG CTF challenge guidance LSB CTF challenge guidance"""
    img = Image.open(image_path)
    pixels = list(img.getdata())
    binary = ''
    for pixel in pixels:
        if isinstance(pixel, tuple):
            for channel in pixel[:3]:
                binary += str(channel & 1)
        else:
            binary += str(pixel & 1)
    # CTF challenge guidance 8 CTF challenge guidance
    result = ''
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if len(byte) == 8:
            result += chr(int(byte, 2))
    return result
```
