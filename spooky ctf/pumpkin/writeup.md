# SpookyCTF — *Heads will Roll*

**Category:** easy · **Points:** 50 · **Solves:** 290 · **Instance:** Inferno
**File:** `pumpkin_head_message.txt`

---

## 1. Challenge

> While chasing Ichabod Crane through Sleepy Hollow, the Headless Horseman got as close as he could, then threw his head! While rolling, rolling, rolling, through the air, his pumpkin head shouted...what? His perfect aim knocked Ichabod to the ground near the rails, but what did he say?

Only file provided:

```
Etu_taip5_w5n_hpmnw_hlgsdso{lyh0_d}jyi_piihef_ne_oy3p0lh4oskt_i:k3l3
```

## 2. Hint analysis

Flavor text usually hides the algorithm. Three repeated cues here:

| Hint | Meaning |
|---|---|
| `rolling, rolling, rolling` | data is "rolled" back and forth across several layers |
| `near the rails` | **rails** |
| `threw his head` / up-and-down motion | **zigzag** traversal |

→ **Rail Fence Cipher**: write the plaintext in a zigzag pattern across *N* rails, then read row by row to get the ciphertext.

## 3. Ciphertext structure

```
Etu_taip5_w5n_hpmnw_hlgsdso{lyh0_d}jyi_piihef_ne_oy3p0lh4oskt_i:k3l3
```

- 68 characters, `_`, `{`, `}`, `:` are preserved → this is a **transposition** cipher (positions shuffled), not a substitution. Character values are untouched.
- So no key/alphabet is needed — only the correct rail count.
- Zigzag period for `r` rails: `period = 2*(r-1)`. With 68 chars, plausible `r` is 2..10 → **brute-force them all**.

## 4. Solve script

```python
ct = "Etu_taip5_w5n_hpmnw_hlgsdso{lyh0_d}jyi_piihef_ne_oy3p0lh4oskt_i:k3l3"

def rail_decrypt(ct, rails):
    n = len(ct)
    pattern = list(range(rails)) + list(range(rails - 2, 0, -1))  # 0,1,2,3,2,1
    idxs = [pattern[i % len(pattern)] for i in range(n)]

    # 1) split ciphertext into rails using per-rail character counts
    counts = [idxs.count(k) for k in range(rails)]
    rows, p = [], 0
    for k in range(rails):
        rows.append(ct[p:p + counts[k]])
        p += counts[k]

    # 2) read back along the original zigzag path
    ptr, out = [0] * rails, []
    for k in idxs:
        out.append(rows[k][ptr[k]])
        ptr[k] += 1
    return ''.join(out)

for r in range(2, 12):
    print(r, rail_decrypt(ct, r))
```

Output at `r = 4` is the only readable English sentence:

```
Enjoy_this_pumpkin_with_the_flag_inside:_spooky{5l33py_h0ll0w_h34d5}
```

## 5. Manual reconstruction (verification)

For `rails = 4` the zigzag sequence is `0,1,2,3,2,1` (period 6):

```
rail 0: E.....i.....n.....w.....d.....h.....y.....h....._.....l.....t.....l.
rail 1: .t...a.p...5._...n._...s.s...y.0...j.i...i.e...e.o...0.h...k._...3.3
rail 2: ..u.t...5.w...h.m...h.g...o.l..._.}..._.i...f.n...y.p...4.s...i.k...
rail 3: ..._....._.....p.....l.....{.....d.....p....._.....3.....o.....:....
```

Ciphertext split in that exact order:

| Rail | Chars | Content |
|---|---|---|
| 0 | 12 | `Etu_taip5_w5` |
| 1 | 23 | `n_hpmnw_hlgsdso{lyh0_d}` |
| 2 | 22 | `jyi_piihef_ne_oy3p0lh4` |
| 3 | 11 | `oskt_i:k3l3` |

Read diagonally along the zigzag → plaintext. `_`, `{`, `}` stay intact because the cipher only moves positions.

## 6. Leetspeak decode

```
spooky{5l33py_h0ll0w_h34d5}
        5=s   3=e  0=o  3=e  0=o  4=a  5=s
→ sleepy hollow heads
```

Perfectly matches the theme: the **Headless Horseman** of **Sleepy Hollow** threw his **head** — which also answers "what did he say?".

## 7. Flag

```
spooky{5l33py_h0ll0w_h34d5}
```

## 8. Takeaways

- **Flavor text is a hint, not decoration.** A word repeated three times (`rolling`) plus a technical noun (`rails`) points straight at the cipher.
- `_` / `{}` surviving intact → always distinguish **transposition** (keeps chars, moves positions) from **substitution** (changes chars) before picking tools.
- Rail Fence has a tiny key space (`rails ≈ 2..len/2`), so **brute-force always wins** — no manual guessing needed.
- Alternative tools: CyberChef (`Rail Fence Cipher Decode`, sweep offsets/rails) or `dcode.fr/rail-fence-cipher`.
