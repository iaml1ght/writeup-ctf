# Writeup: Diagraphephobia

**CTF:** Spooky CTF  
**Challenge:** Diagraphephobia  
**Category:** Forensics / Cryptography  
**Points:** 257  
**Author:** Raindrops095  
**File:** `Diagraphephobia.pdf`  
**Flag:** `spooky{qaStaH_nuq}`

---

## 1. Challenge Overview

The challenge prompt states:
> *"The Federation has found a redacted file from spying on the Klingon. They want to know the contents of it. Can you find it?"*

We are provided with a single PDF document named `Diagraphephobia.pdf`.

---

## 2. Reconnaissance & Initial Analysis

### 2.1 Meaning of the Names
- **Diagraphephobia**: Fear of crossing out, deleting, or redacting text.
- **Header in PDF (`Ja'`)**: In the Klingon language (*tlhIngan Hol*), **ja'** means *"to tell"* or *"to report"*.

### 2.2 Visual Inspection
Opening the PDF reveals:
1. The title: `Ja'`.
2. Four solid black redaction bars obscuring multiple lines of text.
3. An image below the redactions that displays striped, noisy patterns resembling an ECB-encrypted bitmap.

---

## 3. Vulnerability Analysis & Step-by-Step Exploitation

### Step 1: Bypassing Incomplete PDF Redaction
In PDF documents, redacting text by simply placing filled black rectangles over text elements does not remove the underlying text stream from the PDF content stream. 

Using standard PDF text extraction (`pdftotext`):
```bash
pdftotext Diagraphephobia.pdf -
```

Output:
```text
Ja'
B7o731QSZYJtbxIHjz045jhZoAhjG/MHqir4PZANSCWd75Jp/KGdAevRj2JOBEN3eME
W9Sto9ek0bGum9jXYPHiQ/3xQM8ZTrrB6a2OZJNAYCgFizrrNO4enzaXB2ZAGdN+fB
KQPPe530ZxrXlWBTV2QCyqJH8BmHGXKMU3XASpqaWeTXZzvhx1FJOkhV2pw2bif
mMo0Pk4i3XznS1UYsQ==
```

Decoding the Base64 payload yields 160 bytes of binary ciphertext ($10 \times 16\text{ bytes}$ blocks).

### Step 2: Metadata Extraction (The Key)
Inspecting the raw PDF objects and metadata streams (specifically Object 33 and the XMP stream in Object 30):
```pdf
33 0 obj <</CreationDate(D:20261014184308-04'00')/ModDate(D:20261014184308-04'00')/Producer(Skia/PDF m157 Google Docs Renderer)/Subject(lojmIt yIpoSmoH!)/Title()>>endobj
```

- **Subject field:** `lojmIt yIpoSmoH!`
- In Klingon, **"lojmIt yIpoSmoH!"** translates to *"Open the door!"*.
- Byte length: `len("lojmIt yIpoSmoH!") == 16` bytes.

A 16-byte passphrase strongly indicates an **AES-128** encryption key.

### Step 3: Cryptanalysis & Decryption
Given that:
1. The ciphertext length is 160 bytes (a multiple of 16-byte AES blocks).
2. The embedded image in the document exhibits standard AES-ECB leakage (identical blocks produce identical patterns).
3. The key is 16 bytes: `b"lojmIt yIpoSmoH!"`.

We test AES-128 in **ECB** mode using the key:

```python
from Crypto.Cipher import AES
# Or using OpenSSL / libcrypto:
cipher = AES.new(b"lojmIt yIpoSmoH!", AES.MODE_ECB)
plaintext = cipher.decrypt(ciphertext)
```

The ciphertext decrypts cleanly to:
```text
nuqneH
DaHjaj tlhIngan yotlh botlhDaq DIvI' Duj wItu'. Heghlaw' 'ej lonlu'law'. Duj wIHuD 'ej Hov leng peghmey wItu'laH 'e' wItlhoblI'. 

spooky{qaStaH_nuq}
```

### Step 4: Klingon Translation
- **nuqneH**: "What do you want?" / Standard Klingon greeting.
- **DaHjaj tlhIngan yotlh botlhDaq DIvI' Duj wItu'**: "Today, in the center of the Klingon domain, we found a Federation ship."
- **Heghlaw' 'ej lonlu'law'**: "It appears dead and abandoned."
- **Duj wIHuD 'ej Hov leng peghmey wItu'laH 'e' wItlhoblI'**: "We board the ship and hope to discover secrets of space travel."
- **spooky{qaStaH_nuq}**: The flag! (*qaStaH nuq* means *"What is happening?"* in Klingon).

*(Note: The embedded image below the text is an AES-ECB encrypted RGBA rendering of the Federation Starship USS Enterprise NCC-1701, confirming the contents of the Klingon transmission).*

---

## 4. Reproducible Solver Script (`solve.py`)

```python
#!/usr/bin/env python3
"""
Solution for "Diagraphephobia" - Spooky CTF
"""

import re
import base64
import ctypes
import subprocess

def extract_redacted_text_and_key(pdf_path):
    res = subprocess.run(["pdftotext", pdf_path, "-"], capture_output=True, text=True, check=True)
    lines = res.stdout.strip().splitlines()
    b64_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith("Ja'")]
    b64_str = "".join(b64_lines)

    with open(pdf_path, "rb") as f:
        pdf_data = f.read()

    m = re.search(rb'/Subject\s*\((.*?)\)', pdf_data)
    if not m:
        m = re.search(rb'<dc:description>.*?<rdf:li[^>]*>(.*?)</rdf:li>', pdf_data)
        key = m.group(1).decode("utf-8")
    else:
        key = m.group(1).decode("utf-8")

    return b64_str, key

def decrypt_aes_128_ecb(ciphertext, key_bytes):
    libcrypto = ctypes.CDLL("/usr/lib64/libcrypto.so.3")
    libcrypto.EVP_CIPHER_CTX_new.restype = ctypes.c_void_p
    libcrypto.EVP_aes_128_ecb.restype = ctypes.c_void_p

    ctx = libcrypto.EVP_CIPHER_CTX_new()
    cipher = libcrypto.EVP_aes_128_ecb()

    libcrypto.EVP_DecryptInit_ex(ctypes.c_void_p(ctx), ctypes.c_void_p(cipher), None, ctypes.c_char_p(key_bytes), None)
    out = ctypes.create_string_buffer(len(ciphertext) + 32)
    out_len = ctypes.c_int(0)
    libcrypto.EVP_DecryptUpdate(ctypes.c_void_p(ctx), out, ctypes.byref(out_len), ctypes.c_char_p(ciphertext), ctypes.c_int(len(ciphertext)))
    total_len = out_len.value
    final_len = ctypes.c_int(0)
    libcrypto.EVP_DecryptFinal_ex(ctypes.c_void_p(ctx), ctypes.byref(out, total_len), ctypes.byref(final_len))
    libcrypto.EVP_CIPHER_CTX_free(ctypes.c_void_p(ctx))

    return out.raw[:total_len + final_len.value]

def main():
    b64_str, key_str = extract_redacted_text_and_key("Diagraphephobia.pdf")
    ciphertext = base64.b64decode(b64_str)
    plaintext = decrypt_aes_128_ecb(ciphertext, key_str.encode("utf-8")).decode("utf-8")

    print(plaintext.strip())

if __name__ == "__main__":
    main()
```

---

## 5. Flag

```text
spooky{qaStaH_nuq}
```
