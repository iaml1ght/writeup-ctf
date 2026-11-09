# SpookyCTF — *I Feel Like Someone's Watching Me*

**Category:** Cryptography / easy · **Points:** 50 · **Solves:** 203 · **Instance:** inferno  
**File:** `graveyard_letter.txt`  
**Flag:** `spooky{eyez_are_watching_me}`

---

## 1. Challenge Overview

> **Description:**  
> *A letter is found beside a tombstone in a graveyard, but it seems to have been scrambled around.*

We are provided with a single text file:
- `graveyard_letter.txt`: An encrypted letter addressed to Alexander from an unknown sender.

Ciphertext snippet:
```text
Ypejpof Erpveaypj,

Pmpj odagp zlw rptf, D'mp tprf zlwj eiopagp. Iwf D'mp erol tprf fcp qjpopagp lt ealfcpj, fclwuc D yla'f nalx xcl df do...
...
pzps ejp xefgcdau hp. Bwof jphphipj waypjogljpo daofpey lt oqegpo eay fl xjeq df gljjpgfrz.
...
Odagpjprz,

Fcp Lap Zlw Rptf Ipcday
```

---

## 2. Cryptanalysis & The Bijection Trap

### 2.1 Cipher Type
The ciphertext retains punctuation, line breaks, word boundaries, and casing. This is a classic **Monoalphabetic Substitution Cipher** representing a bijective (1-to-1) mapping between the 26 English letters.

### 2.2 Known-Plaintext Patterns & Cribs
1. **Salutation:**  
   `Ypejpof Erpveaypj,` $\longrightarrow$ `Dearest Alexander,`  
   - Maps: `Y` $\to$ `d`, `p` $\to$ `e`, `e` $\to$ `a`, `j` $\to$ `r`, `o` $\to$ `s`, `f` $\to$ `t`, `E` $\to$ `a`, `r` $\to$ `l`, `v` $\to$ `x`, `a` $\to$ `n`, `y` $\to$ `d`.

2. **Sign-off:**  
   `Odagpjprz,` $\longrightarrow$ `Sincerely,`  
   - Confirms: `O` $\to$ `s`, `d` $\to$ `i`, `g` $\to$ `c`, `z` $\to$ `y`.  
   `Fcp Lap Zlw Rptf Ipcday` $\longrightarrow$ `The One You Left Behind`  
   - Confirms: `F` $\to$ `t`, `c` $\to$ `h`, `L` $\to$ `o`, `Z` $\to$ `y`, `l` $\to$ `o`, `w` $\to$ `u`, `R` $\to$ `l`, `t` $\to$ `f`, `I` $\to$ `b`.

3. **Remaining Letters:**  
   - `D'mp` $\to$ `I've` (`m` $\to$ `v`).  
   - `kwdgn` $\to$ `quick` (`k` $\to$ `q`).  
   - `fcdan` $\to$ `think` (`n` $\to$ `k`).  
   - `bwof` $\to$ `just` (`b` $\to$ `j`).  
   - `xefgcdau` $\to$ `watching` (`x` $\to$ `w`, `u` $\to$ `g`).  
   - `hp` $\to$ `me` (`h` $\to$ `m`).  
   - `qjpopagp` $\to$ `presence` (`q` $\to$ `p`).

### 2.3 The Critical Trap: `s` vs `o` (Why `eyes` was incorrect)
Notice that throughout the letter:
- `odagp` $\to$ `since`
- `eiopagp` $\to$ `absence`
- `oqegpo` $\to$ `spaces`
- `waypjogljpo` $\to$ `underscores`

In all instances, **ciphertext `o` maps to plaintext `s`**.  
Because a substitution cipher is a 1-to-1 bijection, ciphertext letter **`s` cannot map to `s`**.

When enumerating the 26 letters:
- 25 plaintext letters are mapped (`a`, `b`, `c`, `d`, `e`, `f`, `g`, `h`, `i`, `j`, `k`, `l`, `m`, `n`, `o`, `p`, `q`, `r`, `s`, `t`, `u`, `v`, `w`, `x`, `y`).
- The only remaining unmapped plaintext letter is **`z`**.

Therefore, ciphertext **`s` maps to plaintext `z`**:
$$\text{Ciphertext } s \longrightarrow \text{Plaintext } z$$

---

## 3. Substitution Mapping Table

| Cipher | Plain | Cipher | Plain | Cipher | Plain | Cipher | Plain |
|:------:|:-----:|:------:|:-----:|:------:|:-----:|:------:|:-----:|
| **a**  |   n   | **h**  |   m   | **o**  |   s   | **v**  |   x   |
| **b**  |   j   | **i**  |   b   | **p**  |   e   | **w**  |   u   |
| **c**  |   h   | **j**  |   r   | **q**  |   p   | **x**  |   w   |
| **d**  |   i   | **k**  |   q   | **r**  |   l   | **y**  |   d   |
| **e**  |   a   | **l**  |   o   | **s**  | **z** | **z**  |   y   |
| **f**  |   t   | **m**  |   v   | **t**  |   f   |        |       |
| **g**  |   c   | **n**  |   k   | **u**  |   g   |        |       |

---

## 4. Full Decrypted Plaintext

```text
Dearest Alexander,

Ever since you left, I've felt your absence. But I've also felt the presence of another, though I don't know who it is. No matter where I go, there's this feeling that follows me. If I ever think it's gone, I'll get a sudden chill up my spine to remind me. But I never see them. If I turn to look, I'll only see quick flashes of hair or clothes, but they'll be gone by the time I round the corner.

It started when I was in crowded areas, like at the mall we used to go to every weekend. The one where we would just walk around and windowshop for hours. You know it. Or at least you did. Then I started feeling it at work, but thought it was just the creepy posters they hang everywhere. Those things have always freaked me out, you know that. They mess with my dreams even though I should be used to them by now.

But a week ago, I started feeling it at home. When I was cooking dinner for just me, watching Hallmark movies in your old living room, or walking Little Alex outside. She misses you by the way. She never liked me much, but she's always causing a racket now. She used to be so cute when you were around, even if she was always trying to nip me.

It's gotten worse the last couple nights. I'll feel someone watching me while I'm trying to sleep, but I'm in our house all alone with the alarm on and every door and window locked and covered. You'd think I'm so paranoid if you were still here. 

I've tried to look for you, but it's like you disappeared. Everywhere you used to go to "get some air" is just missing you. There's only one place I haven't tried yet. I know you used to come visit your mother every Sunday, but I never wanted to overstep. But I've run out of options. I have nothing left here, so I'm going to leave. But I'll put a clue that should help you find me if you still care.

eyez are watching me. Just remember underscores instead of spaces and to wrap it correctly.

I hope you find me before they do.

Sincerely,

The One You Left Behind
```

---

## 5. Flag Extraction

Deciphering the clue line:
- Ciphertext: `pzps ejp xefgcdau hp.`
  - `p` $\to$ `e`
  - `z` $\to$ `y`
  - `p` $\to$ `e`
  - `s` $\to$ `z`
  - Yields: **`eyez are watching me`**

Following the instructions in the letter:
> *"Just remember underscores instead of spaces and to wrap it correctly."*

1. Replace spaces with underscores: `eyez_are_watching_me`
2. Wrap in the SpookyCTF wrapper: `spooky{eyez_are_watching_me}`

---

## 6. Python Solve Script (`solve.py`)

```python
#!/usr/bin/env python3
"""
Solution script for SpookyCTF challenge: "I Feel Like Someone's Watching Me"
Cipher: Monoalphabetic Substitution Cipher (Strict Bijection)
"""

from pathlib import Path

CIPHER_TO_PLAIN = {
    'a': 'n', 'b': 'j', 'c': 'h', 'd': 'i', 'e': 'a', 'f': 't', 'g': 'c',
    'h': 'm', 'i': 'b', 'j': 'r', 'k': 'q', 'l': 'o', 'm': 'v', 'n': 'k',
    'o': 's', 'p': 'e', 'q': 'p', 'r': 'l', 's': 'z', 't': 'f', 'u': 'g',
    'v': 'x', 'w': 'u', 'x': 'w', 'y': 'd', 'z': 'y',
}


def decrypt(text: str) -> str:
    res = []
    for ch in text:
        if ch.lower() in CIPHER_TO_PLAIN:
            p = CIPHER_TO_PLAIN[ch.lower()]
            res.append(p.upper() if ch.isupper() else p)
        else:
            res.append(ch)
    return "".join(res)


def main():
    cur_dir = Path(__file__).resolve().parent
    with open(cur_dir / "graveyard_letter.txt", "r", encoding="utf-8") as f:
        ciphertext = f.read()

    plaintext = decrypt(ciphertext)
    print("=== Decrypted Letter ===")
    print(plaintext)
    print("========================")

    flag_content = "eyez are watching me".replace(" ", "_")
    flag = f"spooky{{{flag_content}}}"
    print(f"\n[+] True Flag: {flag}")


if __name__ == "__main__":
    main()
```

---

## 7. Flag

```text
spooky{eyez_are_watching_me}
```
