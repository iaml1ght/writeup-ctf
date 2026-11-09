#!/usr/bin/env python3
"""
Solution for "Diagraphephobia" - Spooky CTF
"""

import re
import base64
import ctypes
import subprocess

def extract_redacted_text_and_key(pdf_path):
    # 1. Extract base64 text using pdftotext or direct stream parsing
    res = subprocess.run(["pdftotext", pdf_path, "-"], capture_output=True, text=True, check=True)
    lines = res.stdout.strip().splitlines()
    b64_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith("Ja'")]
    b64_str = "".join(b64_lines)

    # 2. Extract key from PDF metadata (/Subject or XMP)
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
    pdf_file = "Diagraphephobia.pdf"
    b64_str, key_str = extract_redacted_text_and_key(pdf_file)
    print(f"[+] Extracted Base64 ciphertext ({len(b64_str)} chars)")
    print(f"[+] Extracted metadata key: {key_str} (length: {len(key_str)} bytes)")

    ciphertext = base64.b64decode(b64_str)
    plaintext = decrypt_aes_128_ecb(ciphertext, key_str.encode("utf-8")).decode("utf-8")

    print("\n[+] Decrypted Klingon Transmission:")
    print("-" * 50)
    print(plaintext.strip())
    print("-" * 50)

    m = re.search(r"spooky\{.*?\}", plaintext)
    if m:
        print(f"\n[+] FLAG: {m.group(0)}")

if __name__ == "__main__":
    main()
