#!/usr/bin/env python3
"""
Solution script for SpookyCTF challenge: "I Feel Like Someone's Watching Me"
Cipher: Monoalphabetic Substitution Cipher (Strict Bijection)
"""

from pathlib import Path

# Strict 1-to-1 mapping derived from cryptanalysis
# Note: Ciphertext 'o' maps to plaintext 's' (e.g. 'odagp' -> 'since', 'oqegpo' -> 'spaces').
# Therefore, ciphertext 's' maps to the remaining unused letter 'z' (e.g. 'pzps' -> 'eyez').
CIPHER_TO_PLAIN = {
    'a': 'n',
    'b': 'j',
    'c': 'h',
    'd': 'i',
    'e': 'a',
    'f': 't',
    'g': 'c',
    'h': 'm',
    'i': 'b',
    'j': 'r',
    'k': 'q',
    'l': 'o',
    'm': 'v',
    'n': 'k',
    'o': 's',
    'p': 'e',
    'q': 'p',
    'r': 'l',
    's': 'z',  # 's' maps to 'z', making 'pzps' -> 'eyez'
    't': 'f',
    'u': 'g',
    'v': 'x',
    'w': 'u',
    'x': 'w',
    'y': 'd',
    'z': 'y',
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

    # Line 13 decrypted:
    # "eyez are watching me. Just remember underscores instead of spaces and to wrap it correctly."
    flag_content = "eyez are watching me".replace(" ", "_")
    flag = f"spooky{{{flag_content}}}"
    print(f"\n[+] True Flag: {flag}")


if __name__ == "__main__":
    main()
