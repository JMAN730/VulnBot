# PRNG cryptography testing guidance

## MT19937 ( Mersenne Twister ) cryptography testing guidance

```python
# MT19937 cryptography testing guidance（cryptography testing guidance 624 cryptography testing guidance）
from ctypes import *

def untemper(y):
    y ^= y >> 18
    y ^= (y << 15) & 0xefc60000
    y ^= (y << 7) & 0x9d2c5680
    y ^= (y << 14) & 0x9d2c5680
    y ^= (y << 13) & 0x9d2c5680
    y ^= (y << 11) & 0x9d2c5680
    y ^= y >> 18
    return y

def recover_mt(outputs):
    """cryptography testing guidance 624 cryptography testing guidance MT19937 cryptography testing guidance"""
    state = [untemper(y) for y in outputs[:624]]
    MT = c_ulong * 624
    mt = MT(*state)
    index = 624
    def twist():
        global index, mt
        for i in range(227):
            y = (mt[i] & 0x80000000) + (mt[(i+1)%624] & 0x7fffffff)
            mt[i] = mt[(i+397) % 624] ^ (y >> 1)
            if y & 1:
                mt[i] ^= 0x9908b0df
        index = 0
    return mt, twist, index
```

## LCG (cryptography testing guidance) cryptography testing guidance

```python
"""
LCG: s_{n+1} = a * s_n + c (mod m)
cryptography testing guidance：cryptography testing guidance
cryptography testing guidance：cryptography testing guidance 3 cryptography testing guidance (s, s_next) cryptography testing guidance a, c, m
"""

def lcg_attack(states):
    """cryptography testing guidance 3 cryptography testing guidance LCG cryptography testing guidance (a, c, m)"""
    s0, s1, s2 = states[0], states[1], states[2]
    # s1 = a*s0 + c (mod m)
    # s2 = a*s1 + c (mod m)
    # s2 - s1 = a*(s1 - s0) (mod m)
    # cryptography testing guidance a, m
```

## LFSR (cryptography testing guidance) cryptography testing guidance

```python
"""
Berlekamp-Massey cryptography testing guidance：cryptography testing guidance LFSR cryptography testing guidance
"""

def berlekamp_massey(s):
    """cryptography testing guidance LFSR cryptography testing guidance"""
    # Sage cryptography testing guidance
    # F.<x> = GF(2)[]
    # s_seq = sequence(s)
    # return list(lfsr_sequence(f, [1]+[0]*15, len(s)))
```

## cryptography testing guidance (XOR cryptography testing guidance)

```python
"""
cryptography testing guidance: C = P XOR keystream
cryptography testing guidance P，cryptography testing guidance keystream = C XOR P
keystream cryptography testing guidance
"""

def xor_attack(ciphertext, known_plaintext):
    """XOR cryptography testing guidance"""
    key = bytes(a ^ b for a, b in zip(ciphertext, known_plaintext))
    return key

def xor_decrypt(key, ciphertext):
    """cryptography testing guidance"""
    return bytes(a ^ b for a, b in zip(key, ciphertext))
```

## RC4 cryptography testing guidance

```python
"""
RC4 cryptography testing guidance：
1. RC4 Drop (cryptography testing guidance N cryptography testing guidance，cryptography testing guidance)
2. cryptography testing guidance
"""

def rc4_drop(ciphertext, drop=3072):
    """RC4 Drop N cryptography testing guidance"""
```

## Python random cryptography testing guidance

```python
import random

# cryptography testing guidance Python random cryptography testing guidance，cryptography testing guidance
# cryptography testing guidance 624 * 4 = 2496 cryptography testing guidance
state = random.getstate()
# cryptography testing guidance
random.setstate(state)
next_val = random.randint(0, 2**31)
```
