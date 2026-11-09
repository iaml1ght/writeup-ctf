#!/usr/bin/env python3
"""HUTECH "Lục bát" LFSR solver.

- The lines in tho.txt are shuffled.  The only lục bát order that
  satisfies every rhyme link is the POEM order below.
- Free syllables (1,3,5 of a 6-line, 1,3,5,7 of an 8-line) give TAPS,
  first free syllable = most significant bit.
- The ciphertext is FLAG xor LFSR keystream, with each byte's bits
  consumed LSB-first (may_ma.py: sum(bit << i for i in range(8))).
- "HUTECH{" is the known-plaintext crib; every ASCII byte also has
  MSB 0, which supplies extra GF(2) equations for the unknown STATE.
"""
from pathlib import Path

POEM = [
    "Đêm khuya phòng máy sáng đèn",
    "Ngón tay gõ phím như quen tiếng lòng",
    "Màn hình chữ chạy như dòng",
    "Mắt cay vẫn dõi từng vòng lặp sâu",
    "Cờ kia giấu tận nơi đâu",
    "Lần từng dấu nhỏ tìm câu trả lời",
    "Khoá kia như hạt sương rơi",
    "Mỗi lần thử lỗi lại vơi niềm tin",
    "Anh em vẫn giữ lòng tin",
    "Thêm dòng lệnh nữa để nhìn lối ra",
    "Gió đêm thổi lạnh hiên nhà",
    "Mảnh trăng nghiêng xuống như là mỉm cười",
    "Màn hình bỗng hiện tên người",
    "Chiếc cờ nhỏ bé đỏ tươi trong màn",
    "Tiếng reo vui khắp nhân gian",
    "Đêm dài bỗng hoá muôn vàn sao xa",
    "Nhắn ai mai mốt đi qua",
    "Nhớ rằng mật mã chỉ là bước đầu",
    "Đường xa còn lắm nhịp cầu",
    "Ai nghe đúng nhịp mới hầu hiểu nhau",
]

OUT_MASK = 0x9E3779B97F4A7C15
FLAG_FORMAT = b"HUTECH{"
M64 = (1 << 64) - 1
TRAC = "áắấéếíóốớúứýảẳẩẻểỉỏổởủửỷãẵẫẽễĩõỗỡũữỹạặậẹệịọộợụựỵ"


def is_trac(word: str) -> int:
    return int(any(c in TRAC for c in word.lower()))


def taps_from_poem() -> int:
    bits = []
    for line in POEM:
        words = line.split()
        free = [0, 2, 4] if len(words) == 6 else [0, 2, 4, 6]
        bits.extend(is_trac(words[i]) for i in free)
    return int("".join(map(str, bits[:64])), 2)


def parity(x: int) -> int:
    return x.bit_count() & 1


def output_rows(nbits: int, taps: int) -> list[int]:
    """rows[i] is a 64-bit mask with keystream bit i = parity(rows[i] & STATE)."""
    rows, r = [], OUT_MASK
    for _ in range(nbits):
        rows.append(r)
        fb = (r >> 63) & 1
        r = ((r << 1) & M64) ^ (taps if fb else 0)
    return rows


def keystream(state: int, nbits: int, taps: int) -> list[int]:
    out, s = [], state
    for _ in range(nbits):
        out.append(parity(s & OUT_MASK))
        fb = parity(s & taps)
        s = (s >> 1) | (fb << 63)
    return out


def bits_lsb(data: bytes) -> list[int]:
    return [(b >> k) & 1 for b in data for k in range(8)]


def bytes_lsb(bits: list[int]) -> bytes:
    return bytes(sum(bits[i + k] << k for k in range(8))
                 for i in range(0, len(bits) - 7, 8))


def gf2_solve(eqs: list[tuple[int, int]]) -> int | None:
    """Solve mask . x = rhs over GF(2); return one solution."""
    basis = {}
    for row, rhs in eqs:
        while row:
            p = row.bit_length() - 1
            if p in basis:
                row ^= basis[p][0]
                rhs ^= basis[p][1]
            else:
                basis[p] = (row, rhs)
                break
        else:
            if rhs:
                return None
    x = 0
    for p in sorted(basis):
        row, rhs = basis[p]
        x |= (rhs ^ parity(row & x)) << p
    return x


def solve(ct: bytes, taps: int) -> tuple[int, bytes]:
    n = len(ct)
    ct_bits = bits_lsb(ct)
    rows = output_rows(len(ct_bits), taps)
    eqs = []

    # known flag prefix at byte 0
    for i, b in enumerate(bits_lsb(FLAG_FORMAT)):
        eqs.append((rows[i], ct_bits[i] ^ b))

    # every byte of an ASCII flag has MSB 0 (stream bit 8*j+7 in LSB-first)
    for j in range(n):
        i = 8 * j + 7
        eqs.append((rows[i], ct_bits[i]))

    # known closing brace at the last byte
    base = 8 * (n - 1)
    for k, b in enumerate(bits_lsb(b"}")):
        eqs.append((rows[base + k], ct_bits[base + k] ^ b))

    state = gf2_solve(eqs)
    if state is None:
        raise SystemExit("inconsistent crib: wrong TAPS / poem order")
    pt = bytes_lsb([c ^ k for c, k in zip(ct_bits, keystream(state, len(ct_bits), taps))])
    return state, pt


def main() -> None:
    root = Path(__file__).resolve().parent
    ct = bytes.fromhex((root / "out.txt").read_text(encoding="utf-8").split()[0])
    taps = taps_from_poem()
    state, flag = solve(ct, taps)

    print(f"TAPS  = 0x{taps:016x}")
    print(f"STATE = 0x{state:016x}")
    print(f"FLAG  = {flag.decode()}")

    # independent check: re-encrypt with the exact may_ma.py LFSR
    class LFSR:
        def __init__(self, s, t):
            self.s, self.t = s, t

        def bit(self):
            out = parity(self.s & OUT_MASK)
            fb = parity(self.s & self.t)
            self.s = (self.s >> 1) | (fb << 63)
            return out

        def byte(self):
            return sum(self.bit() << i for i in range(8))

    lf = LFSR(state, taps)
    assert bytes(c ^ lf.byte() for c in flag) == ct
    print("re-encryption matches out.txt")


if __name__ == "__main__":
    main()
