#!/usr/bin/env python3
"""
Exploit for "No Nonsense on this Server" (Spooky CTF)
Vulnerability: ECDSA Nonce Reuse (NIST P-256) on admin signed audit logs.
"""

import sys
import os
import struct
import hashlib
import base64
import subprocess

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

    # Find nonce reuse: identical r
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

    # s1 - s2 = k^-1 (z1 - z2) mod N
    k = ((z1 - z2) * pow(s1 - s2, N - 2, N)) % N
    # d = r^-1 (s1*k - z1) mod N
    d = ((s1 * k - z1) * pow(r, N - 2, N)) % N

    # Verify public key
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
    log_file = 'auth.log.raw'
    d, pub = recover_admin_private_key(log_file)
    print(f"[+] Successfully recovered admin private key d = {hex(d)}")
    export_sec1_pem(d, pub, 'admin.pem')
    print("[+] Exported admin.pem")
