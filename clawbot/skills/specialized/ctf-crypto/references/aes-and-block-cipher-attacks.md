# AES cryptography testing guidance

## cryptography testing guidance

| cryptography testing guidance | cryptography testing guidance | cryptography testing guidance |
|------|------|-----------|
| ECB | cryptography testing guidance→cryptography testing guidance | cryptography testing guidance、cryptography testing guidance |
| CBC | cryptography testing guidance | IV cryptography testing guidance、Padding Oracle |
| CTR | cryptography testing guidance | nonce cryptography testing guidance → XOR cryptography testing guidance |
| CFB | cryptography testing guidance | IV cryptography testing guidance |
| OFB | cryptography testing guidance | nonce cryptography testing guidance |
| GCM | cryptography testing guidance | nonce cryptography testing guidance → cryptography testing guidance |

## ECB cryptography testing guidance

```python
from Crypto.Cipher import AES

# ECB cryptography testing guidance
# cryptography testing guidance：cryptography testing guidance → cryptography testing guidance
# cryptography testing guidance

def ecb_detect(ciphertext, block_size=16):
    """cryptography testing guidance ECB cryptography testing guidance（cryptography testing guidance）"""
    blocks = [ciphertext[i:i+block_size] for i in range(0, len(ciphertext), block_size)]
    return len(blocks) != len(set(blocks))
```

## CBC IV cryptography testing guidance

```python
"""
cryptography testing guidance：cryptography testing guidance CBC cryptography testing guidance，P[i] = Decrypt(C[i]) XOR C[i-1]
cryptography testing guidance C[i-1] cryptography testing guidance → cryptography testing guidance P[i] cryptography testing guidance

cryptography testing guidance：cryptography testing guidance IV cryptography testing guidance，cryptography testing guidance C[i-1] cryptography testing guidance i cryptography testing guidance
cryptography testing guidance：C[i-1] cryptography testing guidance P[i-1] cryptography testing guidance
"""

def cbc_iv_flip(ciphertext, known_plain, target_plain, block_size=16):
    """cryptography testing guidance CBC cryptography testing guidance（cryptography testing guidance IV）"""
    iv = bytearray(ciphertext[:block_size])
    for i in range(block_size):
        iv[i] = iv[i] ^ known_plain[i] ^ target_plain[i]
    return bytes(iv) + ciphertext[block_size:]
```

## Padding Oracle cryptography testing guidance

```python
"""
cryptography testing guidance：CBC cryptography testing guidance Padding cryptography testing guidance，cryptography testing guidance
cryptography testing guidance，cryptography testing guidance/cryptography testing guidance

cryptography testing guidance：
1. cryptography testing guidance CBC cryptography testing guidance
2. cryptography testing guidance Padding cryptography testing guidance
3. cryptography testing guidance
"""

def padding_oracle_attack(oracle, ciphertext, block_size=16):
    """Padding Oracle cryptography testing guidance
    
    oracle: cryptography testing guidance，cryptography testing guidance True(paddingcryptography testing guidance)/False(paddingcryptography testing guidance)
    """
    blocks = [ciphertext[i:i+block_size] for i in range(0, len(ciphertext), block_size)]
    plaintext = b''
    
    for block_idx in range(1, len(blocks)):
        prev_block = bytearray(blocks[block_idx - 1])
        curr_block = blocks[block_idx]
        intermediate = bytearray(block_size)
        
        for byte_pos in range(block_size - 1, -1, -1):
            padding_val = block_size - byte_pos
            
            # cryptography testing guidance
            test_block = bytearray(block_size)
            for k in range(byte_pos + 1, block_size):
                test_block[k] = intermediate[k] ^ padding_val
            
            found = False
            for guess in range(256):
                test_block[byte_pos] = guess
                test_cipher = bytes(test_block) + curr_block
                
                if oracle(test_cipher):
                    intermediate[byte_pos] = guess ^ padding_val
                    found = True
                    break
            
            if not found:
                raise Exception(f"Padding oracle attack failed at byte {byte_pos}")
        
        # cryptography testing guidance
        for i in range(block_size):
            plaintext += bytes([intermediate[i] ^ prev_block[i]])
    
    return plaintext
```

## GCM Nonce cryptography testing guidance

```python
"""
cryptography testing guidance nonce cryptography testing guidance：
- cryptography testing guidance
- C1 = P1 XOR keystream
- C2 = P2 XOR keystream
- C1 XOR C2 = P1 XOR P2

cryptography testing guidance P1，cryptography testing guidance P2
"""

def gcm_nonce_reuse(c1, c2, p1):
    """cryptography testing guidance GCM nonce cryptography testing guidance"""
    return bytes(a ^ b ^ c for a, b, c in zip(c1, c2, p1))
```

## CTR Nonce cryptography testing guidance

```python
"""
CTR cryptography testing guidance nonce cryptography testing guidance
C1 = P1 XOR keystream
C2 = P2 XOR keystream
C1 XOR C2 = P1 XOR P2
"""

def ctr_nonce_reuse(c1, c2, known_p1):
    """cryptography testing guidance CTR nonce cryptography testing guidance"""
    return bytes(a ^ b ^ c for a, b, c in zip(c1, c2, known_p1))
```
