#!/usr/bin/env python3
"""
Exploit / Solve script for SpookyCTF - Klediophobia
Challenge: Klediophobia (SpookyTrust Intermediate CA compromised key)
Flag: spooky{4T_L345T_1T_15NT_F0UR}
"""

import base64
import requests
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

SERVER_URL = "http://3.149.129.229:8000"

def main():
    print("[*] Requesting fresh audit challenge...")
    res = requests.get(f"{SERVER_URL}/challenge", timeout=10).json()
    session_id = res["session_id"]
    message = res["message"]
    print(f"[+] Session ID : {session_id}")
    print(f"[+] Message    : {message}")

    # Recovered private key for ST-ISS-03 (OBJ-0003-R)
    # The HSM compat-restore handler corrupted/reduced the key scalar to d = 1963
    d = 1963
    priv_key = ec.derive_private_key(d, ec.SECP384R1())

    print("[*] Signing audit message using ECDSA-P384-SHA384...")
    signature_der = priv_key.sign(
        message.encode("utf-8"),
        ec.ECDSA(hashes.SHA384())
    )
    sig_b64 = base64.b64encode(signature_der).decode("utf-8")
    print(f"[+] Signature (Base64 DER): {sig_b64}")

    print("[*] Submitting signature to /verify...")
    verify_res = requests.post(
        f"{SERVER_URL}/verify",
        json={"session_id": session_id, "signature": sig_b64},
        timeout=10
    ).json()

    print("[+] Server response:", verify_res)
    if "flag" in verify_res:
        print(f"\n[!!!] FLAG: {verify_res['flag']}")

if __name__ == "__main__":
    main()
