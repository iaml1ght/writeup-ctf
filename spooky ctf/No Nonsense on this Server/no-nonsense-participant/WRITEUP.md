# Writeup: No Nonsense on this Server

**CTF:** Spooky CTF  
**Challenge:** No Nonsense on this Server  
**Category:** Cryptography / Network Exploitation  
**Points:** 568  
**Author:** Ryan Alport  
**Target:** `nc 18.222.247.20 19160`  
**Flag:** `spooky{reused_k_no_nons3nse_89f3ae32316e}`

---

## 1. Challenge Overview

We are provided with participant files containing:
- A reference client implementation in C (`client/main.c`, `common/protocol.c`, `common/crypto.c`, `Makefile`).
- Protocol specifications (`docs/PROTOCOL.md`, `docs/PARTICIPANT.md`).
- A private key for an unprivileged account: `data/general.pem` (`general`).

The objective is to read `/home/admin/flag.txt` from the remote server running the proprietary **SP00KY** protocol over TCP port 19160.

---

## 2. Initial Reconnaissance

### 2.1 Protocol Analysis

According to `docs/PROTOCOL.md`:
- Transport: TCP binary protocol, framing consists of `[version: 1B][opcode: 1B][length: 2B][payload: NB]`.
- Authentication flow:
  1. Client sends `HELLO` (`0x01`). Server replies with banner `SP00KY/1 - Remote Access Service`.
  2. Client sends `AUTH_START` (`0x02`) with username.
  3. Server replies with `AUTH_CHALLENGE` (`0x03`) containing a 32-byte nonce.
  4. Client signs `ASCII("SP00KY-AUTH-v1") || len(user) || user || challenge` using **ECDSA over NIST P-256 (secp256r1) with SHA-256**, sending `(r, s)` in `AUTH_PROVE` (`0x04`).
  5. Server validates against registered public key and returns `AUTH_RESULT` (`0x05`).

### 2.2 Accessing the System as Unprivileged User

Building the reference client:
```bash
make
./spooky-client --host 18.222.247.20 --port 19160 --user general --key data/general.pem
```

From the `general` account, we inspect the filesystem:
```text
general@spooky:~$ ls /home
admin/
general/
general@spooky:~$ ls /home/admin
ls: /home/admin: Permission denied
general@spooky:~$ cat notes.txt
Lab notes, general account

The remote service authenticates with ECDSA P-256 challenge-response signatures.
Each account has its own key. Session and signature audit records are appended
to the authentication log, including the fields needed to rebuild a signed record.

The administrator still has a home directory on this host. The matching private
key was never checked into the general account.
```

Reading `/var/log/auth.log` reveals historical audit logs with user public keys, timestamps, event descriptions, and signature components `r` and `s`.

---

## 3. Vulnerability Discovery: ECDSA Nonce Reuse

The challenge title *"No Nonsense on this Server"* is a pun on **"No Nonce"**.

In ECDSA, the security of the signature hinges strictly on the ephemeral nonce $k$ being completely unique and unpredictable for every signed message. If two signatures share the exact same nonce $k$, their curve points $R = k \cdot G = (x_R, y_R)$ will be identical, resulting in $r_1 = r_2$.

Extracting all signed log lines from `/var/log/auth.log` and checking for duplicate $r$ values:

```python
from collections import Counter
r_counts = Counter(record['r'] for record in log_records)
# Found: ca7b852e0061ee6223df1ef9df733cb6a6df89daabe51b3a4236e75980afce49 (count=2)
```

The two records with duplicate $r$ both belonged to user `admin`:

### Record 1
- **Timestamp:** `1705029267000`
- **Username:** `admin`
- **Event hex:** `6163636570746564207369676e617475726520666f722061646d696e2066726f6d2031302e372e302e3134` (`"accepted signature for admin from 10.7.0.14"`)
- **Public key:** `040bd58bb840bcaff60de70d80e10f8f68b3aef656a3fb07714d150336279ed502bedc52adb9e4e24097d2e17f8d1c73bea0911c1a24cfc20bb741608c3176f816`
- **r:** `ca7b852e0061ee6223df1ef9df733cb6a6df89daabe51b3a4236e75980afce49`
- **s1:** `778a3ba4196e34539ae032d2314bbc26d37b5734ca30b3e2a6b66c110e9b774e`

### Record 2
- **Timestamp:** `1705029336000`
- **Username:** `admin`
- **Event hex:** `73657373696f6e206f70656e656420666f722061646d696e2066726f6d2031302e372e302e3134` (`"session opened for admin from 10.7.0.14"`)
- **r:** `ca7b852e0061ee6223df1ef9df733cb6a6df89daabe51b3a4236e75980afce49`
- **s2:** `7ee53fa43f6313b354903a77c0823f50ae5d57a32a3cf4a28c03be93a7cf0227`

---

## 4. Cryptographic Derivation

According to `PROTOCOL.md`, audit log records are signed over the canonical format:
```text
ASCII("SP00KY-LOG-v1")
|| uint64(timestamp_ms, big-endian)
|| uint8(username_length)
|| ASCII(username)
|| uint16(event_length, big-endian)
|| event_bytes
```

Let:
- $m_1, m_2$ be the canonical messages for Record 1 and Record 2.
- $z_1 = \text{SHA256}(m_1)$ and $z_2 = \text{SHA256}(m_2)$ as integers.
- $n$ be the order of the NIST P-256 base point:
  $$n = \text{0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551}$$

In ECDSA signature generation:
$$s_1 \equiv k^{-1}(z_1 + r \cdot d) \pmod n$$
$$s_2 \equiv k^{-1}(z_2 + r \cdot d) \pmod n$$

Subtracting the two equations eliminates the private key $d$:
$$s_1 - s_2 \equiv k^{-1}(z_1 - z_2) \pmod n$$
$$k \equiv (z_1 - z_2)(s_1 - s_2)^{-1} \pmod n$$

With $k$ recovered, substituting into either signature equation yields the private key $d$:
$$d \equiv r^{-1}(s_1 \cdot k - z_1) \pmod n$$

### Recovered Private Key
$$d = \text{0xb4ade2a2e9404047f56f64d4e10bed17932bb5863180881f7506e90a9c3ebbb1}$$

Computing $Q = d \cdot G$ gives:
- $Q_x = \text{0xbd58bb840bcaff60de70d80e10f8f68b3aef656a3fb07714d150336279ed502}$
- $Q_y = \text{0xbedc52adb9e4e24097d2e17f8d1c73bea0911c1a24cfc20bb741608c3176f816}$

Matching the registered public key in the server database.

---

## 5. Exploitation & Flag Retrieval

1. Encode the recovered private key $d$ into SEC 1 DER / PEM format (`admin.pem`).
2. Run the client authenticating as `admin`:
   ```bash
   printf "cat /home/admin/flag.txt\nexit\n" | ./spooky-client \
       --host 18.222.247.20 \
       --port 19160 \
       --user admin \
       --key admin.pem
   ```

Output:
```text
SP00KY/1 - Remote Access Service
admin@spooky:~$ spooky{reused_k_no_nons3nse_89f3ae32316e}
```

---

## 6. Exploit Script (`solve.py`)

```python
#!/usr/bin/env python3
"""
Exploit for "No Nonsense on this Server" (Spooky CTF)
Vulnerability: ECDSA Nonce Reuse (NIST P-256) on admin signed audit logs.
"""

import struct
import hashlib
import base64

# NIST P-256 (secp256r1) Curve Parameters
P = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
A = P - 3
B = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
GX = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
GY = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
N = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

def point_add(P_pt, Q_pt):
    if P_pt is None: return Q_pt
    if Q_pt is None: return P_pt
    x1, y1 = P_pt
    x2, y2 = Q_pt
    if x1 == x2 and y1 != y2:
        return None
    if x1 == x2:
        m = (3 * x1 * x1 + A) * pow(2 * y1, P - 2, P) % P
    else:
        m = (y2 - y1) * pow(x2 - x1, P - 2, P) % P
    x3 = (m * m - x1 - x2) % P
    y3 = (m * (x1 - x3) - y1) % P
    return (x3, y3)

def point_mul(k, P_pt):
    R = None
    while k > 0:
        if k & 1:
            R = point_add(R, P_pt)
        P_pt = point_add(P_pt, P_pt)
        k >>= 1
    return R

def make_canonical_log_msg(ts_ms, username, event_hex):
    ev = bytes.fromhex(event_hex)
    u = username.encode('ascii')
    return (b"SP00KY-LOG-v1" +
            struct.pack(">Q", ts_ms) +
            struct.pack(">B", len(u)) +
            u +
            struct.pack(">H", len(ev)) +
            ev)

def recover_admin_private_key(log_path):
    records = []
    with open(log_path, 'r', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line.startswith("timestamp_ms="):
                continue
            parts = line.split(' ')
            d = {}
            for p in parts:
                if '=' in p:
                    k, v = p.split('=', 1)
                    d[k] = v
            if 'r' in d and 's' in d and d.get('username') == 'admin':
                records.append(d)

    by_r = {}
    pair = None
    for rec in records:
        r_val = rec['r']
        if r_val in by_r:
            pair = (by_r[r_val], rec)
            break
        by_r[r_val] = rec

    if not pair:
        raise ValueError("No reused r found for admin in audit logs!")

    rec1, rec2 = pair
    r = int(rec1['r'], 16)
    s1 = int(rec1['s'], 16)
    s2 = int(rec2['s'], 16)

    m1 = make_canonical_log_msg(int(rec1['timestamp_ms']), rec1['username'], rec1['event_hex'])
    m2 = make_canonical_log_msg(int(rec2['timestamp_ms']), rec2['username'], rec2['event_hex'])

    z1 = int.from_bytes(hashlib.sha256(m1).digest(), 'big')
    z2 = int.from_bytes(hashlib.sha256(m2).digest(), 'big')

    k = ((z1 - z2) * pow(s1 - s2, N - 2, N)) % N
    d = ((s1 * k - z1) * pow(r, N - 2, N)) % N

    pub_point = point_mul(d, (GX, GY))
    expected_pub = bytes.fromhex(rec1['public_key'])
    actual_pub = b'\x04' + pub_point[0].to_bytes(32, 'big') + pub_point[1].to_bytes(32, 'big')
    assert actual_pub == expected_pub, "Recovered public key mismatch!"

    return d, pub_point

def export_sec1_pem(d, pub_point, out_path):
    d_bytes = d.to_bytes(32, 'big')
    qx_bytes = pub_point[0].to_bytes(32, 'big')
    qy_bytes = pub_point[1].to_bytes(32, 'big')
    pub_bytes = b'\x04' + qx_bytes + qy_bytes

    version = b'\x02\x01\x01'
    priv = b'\x04\x20' + d_bytes
    params = b'\xa0\x0a\x06\x08\x2a\x86\x48\xce\x3d\x03\x01\x07'
    pub = b'\xa1\x44\x03\x42\x00' + pub_bytes

    seq_body = version + priv + params + pub
    der = b'\x30' + bytes([len(seq_body)]) + seq_body

    b64 = base64.b64encode(der).decode('ascii')
    lines = [b64[i:i+64] for i in range(0, len(b64), 64)]
    pem = '-----BEGIN EC PRIVATE KEY-----\n' + '\n'.join(lines) + '\n-----END EC PRIVATE KEY-----\n'

    with open(out_path, 'w') as f:
        f.write(pem)

if __name__ == '__main__':
    d, pub = recover_admin_private_key('auth.log.raw')
    print(f"[+] Recovered admin private key: {hex(d)}")
    export_sec1_pem(d, pub, 'admin.pem')
    print("[+] Exported admin.pem")
```

---

## 7. Remediation / Mitigations

- **RFC 6979 (Deterministic Nonce Generation):** Replace random nonce generation with deterministic nonce generation using HMAC-SHA256 over the message and private key, ensuring no two distinct messages ever share a nonce.
- **Key Rotation:** When a faulty PRNG or nonce leak occurs, immediately revoke and rotate affected identity keys.
