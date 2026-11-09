# SpookyCTF — *Klediophobia*

**Category:** Cryptography · **Points:** 631 · **Author:** N00D135  
**Target:** `http://3.149.129.229:8000/`  
**Flag:** `spooky{4T_L345T_1T_15NT_F0UR}`

---

## 1. Challenge Overview

> Some keys are better left buried...  
> After a mysterious midnight key-generation ceremony, SpookyTrust proudly announced the creation of four new intermediate CA certificates. Each passed verification with flying colors.  
> Whispers of an unusual event buried deep within the HSM logs have raised suspicions about the ceremony. The engineers insist everything went according to plan, but can their certificates really be trusted?  
> You've been given access to the certificates, signing requests, and audit records. Can you uncover SpookyTrust's darkest secret?  
> SpookyTrust's audit server is waiting for proof. Recover the compromised signing key and use it to sign a fresh audit message. The server expects an ECDSA-SHA384 signature over the exact UTF-8 message, encoded as Base64 (DER). If you can convince the server that you possess the key, it will surrender the flag.

Files provided:
- `root.pem`: Root CA certificate (P-384)
- `key-inventory.csv`: Mapping certificates to HSM object IDs
- `ceremony.log`: HSM audit log recorded during the key ceremony
- `client.py`: Client script showing how `/challenge` and `/verify` work
- `ST-ISS-01.pem`, `ST-ISS-01.csr.pem`
- `ST-ISS-02.pem`, `ST-ISS-02.csr.pem`
- `ST-ISS-03.pem`, `ST-ISS-03.csr.pem`
- `ST-ISS-04.pem`, `ST-ISS-04.csr.pem`

---

## 2. HSM Log Analysis & Root Cause

Inspecting `ceremony.log`:

```
2026-10-25T04:32:38Z HSM  INIT         slot=03 status=OK
2026-10-25T04:32:39Z KEY  GENERATE     object=OBJ-0001 curve=P-384 status=OK
2026-10-25T04:32:40Z CSR  CREATE       object=OBJ-0001 certificate=ST-ISS-01 status=OK
2026-10-25T04:32:41Z KEY  GENERATE     object=OBJ-0002 curve=P-384 status=OK
2026-10-25T04:32:42Z CSR  CREATE       object=OBJ-0002 certificate=ST-ISS-02 status=OK
2026-10-25T04:32:43Z KEY  GENERATE     object=OBJ-0003 curve=P-384 status=OK
2026-10-25T04:32:44Z HSM  WRAP         object=OBJ-0003 mechanism=AES256-GCM status=OK
2026-10-25T04:32:45Z HSM  UNWRAP       source=OBJ-0003 object=OBJ-0003-R handler=compat-restore status=OK
2026-10-25T04:32:46Z CSR  CREATE       object=OBJ-0003-R certificate=ST-ISS-03 status=OK
2026-10-25T04:32:47Z KEY  GENERATE     object=OBJ-0004 curve=P-384 status=OK
2026-10-25T04:32:48Z CSR  CREATE       object=OBJ-0004 certificate=ST-ISS-04 status=OK
2026-10-25T04:32:49Z ROOT SIGN_BATCH   signed=4 failures=0 status=OK
2026-10-25T04:32:50Z CERT VERIFY_BATCH certificates=4 failures=0 status=OK
```

Notice lines 7–9:
- While all other intermediate CA keys (`OBJ-0001`, `OBJ-0002`, `OBJ-0004`) were generated and directly signed into CSRs, **`OBJ-0003`** underwent an `HSM WRAP` followed by an `HSM UNWRAP` using a compatibility handler:
  `handler=compat-restore` -> resulting in `OBJ-0003-R` used for **`ST-ISS-03`**.
- This directly aligns with the challenge description: *"Whispers of an unusual event buried deep within the HSM logs..."*.

---

## 3. Cryptographic Flaw: Small Private Key Scalar

When inspecting the public key $Q$ of `ST-ISS-03.pem` on curve NIST P-384 (`secp384r1`):
$$Q = d \cdot G$$

Because of the faulty `compat-restore` handler, the private key scalar $d$ was severely truncated or misparsed into a tiny integer.

Testing for small values of $d$ reveals:
$$d = 1963$$

Verification:
$$1963 \cdot G = (x, y)$$
- $x = \text{0xcf1ca397524bfc660ef7b10225ddf28c55f24b25c921c3580e65ba93920adbf57381c99c8a13571eabf8be29bff91d6c}$
- $y = \text{0x24ff8f64973acc2c6b70bc77dd5ed60a608e987006d62185032a98ea385b796e0f3a4ab777ac6704c4c8383e554a0447}$

This matches the public key in `ST-ISS-03.pem` and `ST-ISS-03.csr.pem` down to the exact bit!

---

## 4. Exploit & Flag Recovery

1. Query `/challenge` to get a fresh `session_id` and random audit message.
2. Sign the message UTF-8 bytes using ECDSA-P384-SHA384 with private key $d = 1963$.
3. DER-encode and Base64-encode the signature.
4. Submit the signature to `/verify`.

### Exploit Script (`solve.py`)

```python
import base64
import requests
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

server = "http://3.149.129.229:8000"

res = requests.get(f"{server}/challenge").json()
session_id = res["session_id"]
message = res["message"]

d = 1963
priv_key = ec.derive_private_key(d, ec.SECP384R1())

signature_der = priv_key.sign(
    message.encode("utf-8"),
    ec.ECDSA(hashes.SHA384())
)
sig_b64 = base64.b64encode(signature_der).decode("utf-8")

verify_res = requests.post(f"{server}/verify", json={
    "session_id": session_id,
    "signature": sig_b64
}).json()

print(verify_res)
# {'result': 'VALID', 'flag': 'spooky{4T_L345T_1T_15NT_F0UR}'}
```

Flag:
```
spooky{4T_L345T_1T_15NT_F0UR}
```
*(The flag text humorously references XKCD 221's "random number generator returning 4")*
