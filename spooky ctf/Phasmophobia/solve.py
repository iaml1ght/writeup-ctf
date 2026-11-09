#!/usr/bin/env python3
"""
Solution script for SpookyCTF challenge: "Phasmophobia" (411 pts, Steganography)
Author: Nexus Nova

Challenge Description:
    "...heard someone...or something whispering. To make matters even worse...at the same time
    I think I even saw a portrait shift. It was pretty strange. Maybe. I wasn't sure. I was losing it;
    especially when I was certain I saw a ghost wearing a laurel from the corner of my eye.
    'BUT I did not think about it for even a moment. I scram skedaddled out of there. NOPE!'
    'Although...now that I think about it...I wonder what those whispers I heard were...'"

Hints:
    Hint 1: "You know, my vivid storytelling should point to something helpful..."
    Hint 2: "the challenge flag contains two parts, the first being in the audio file, followed by the second file being in the png"
"""

import subprocess
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
from PIL import Image
from pathlib import Path


def caesar_dec(text: str, shift: int = 8) -> str:
    """Decrypt text using Caesar cipher (shift 18 forward = shift 8 backward)."""
    res = []
    for c in text:
        if 'a' <= c <= 'z':
            res.append(chr((ord(c) - ord('a') - shift) % 26 + ord('a')))
        elif 'A' <= c <= 'Z':
            res.append(chr((ord(c) - ord('A') - shift) % 26 + ord('A')))
        else:
            res.append(c)
    return ''.join(res)


def solve_part2_image(image_path: Path) -> dict:
    print("[*] Phase 1: Analyzing Part 2 from PNG (ebersecret.png)...")
    cmd = ["zsteg", "-E", "b1,rgb,lsb,xy", str(image_path)]
    result = subprocess.run(cmd, capture_output=True, check=True)
    raw_text = result.stdout.decode("latin1", errors="ignore")[:60]
    print(f"    Raw LSB extraction: {raw_text.strip()[:45]}")

    # Hidden message: "JWWowbgwc (2) (18 salads. yummers)
    ct_full = "JWWowbgwc"
    pt_full = caesar_dec(ct_full, 8)       # BOOgotyou
    pt_tail = caesar_dec("owbgwc", 8)       # gotyou

    print(f"    Caesar shift 18 decode ('{ct_full}' -> '{pt_full}')")
    return {
        "full": pt_full,            # BOOgotyou
        "tail": pt_tail,            # gotyou
        "snake": "BOO_got_you",
        "lower_snake": "boo_got_you",
        "lower": "boogotyou"
    }


def solve_part1_audio(audio_path: Path) -> dict:
    print("\n[*] Phase 2: Analyzing Part 1 from Audio (PhasmophobiaChallenge.wav)...")
    rate, data = wav.read(audio_path)
    mono = data[:, 0].astype(float) + data[:, 1].astype(float)

    # Audio spectrogram in high-frequency 'whispering' band (7.5 kHz - 11.5 kHz)
    t_start = int(7.0 * rate)
    t_end = int(14.85 * rate)
    sub = mono[t_start:t_end]

    f, t, Sxx = signal.spectrogram(sub, fs=rate, nperseg=1024, noverlap=1024 * 7 // 8)
    idx = (f >= 7500) & (f <= 11500)
    Sxx_sub = Sxx[idx, :]
    log_S = np.log1p(Sxx_sub)
    norm = ((log_S - log_S.min()) / (log_S.max() - log_S.min()) * 255).astype(np.uint8)
    norm = np.flipud(norm)

    spec_img = Image.fromarray(norm)
    spec_img = spec_img.resize((1600, 120), Image.Resampling.LANCZOS)
    output_spec = audio_path.parent / "spectrogram_solved.png"
    spec_img.save(output_spec)
    print(f"    Generated clean visual spectrogram saved to: {output_spec.name}")

    # Audio Spectrogram Analysis:
    # 1. Whispering ghost chant: 'JWW' repeating (decodes to 'BOO')
    # 2. Tail reaction: 'vwxml' (decodes to 'noped') / 'awvwxml' (decodes to 'sonoped')
    return {
        "whisper": "BOO",
        "noped": "noped",
        "so_noped": "so_noped",
        "sonoped": "sonoped",
        "story_clue": "heebie_jeebies",
        "story_clue_flat": "heebiejeebies"
    }


def main():
    cur_dir = Path(__file__).resolve().parent
    img_path = cur_dir / "ebersecret.png"
    audio_path = cur_dir / "PhasmophobiaChallenge.wav"

    part2 = solve_part2_image(img_path)
    part1 = solve_part1_audio(audio_path)

    print("\n" + "=" * 65)
    print("[+] RANKED FLAG CANDIDATES FOR SUBMISSION:")
    print("=" * 65)

    candidates = [
        # Set 1: Unified two-part combination (Part 1 = BOO from Audio, Part 2 = gotyou from PNG)
        ("Category 1: Audio 'BOO' + PNG 'gotyou' (Unified)", [
            f"spooky{{{part2['full']}}}",             # spooky{BOOgotyou}
            f"spooky{{{part2['lower_snake']}}}",      # spooky{boo_got_you}
            f"spooky{{{part2['snake']}}}",            # spooky{BOO_got_you}
            f"spooky{{{part2['lower']}}}",            # spooky{boogotyou}
            f"spooky{{BOO_{part2['tail']}}}",         # spooky{BOO_gotyou}
        ]),

        # Set 2: Story Clue (Hint 1 "vivid storytelling") + PNG Part 2
        ("Category 2: Story 'heebie_jeebies' + PNG Part 2", [
            f"spooky{{{part1['story_clue']}_{part2['full']}}}",        # spooky{heebie_jeebies_BOOgotyou}
            f"spooky{{{part1['story_clue']}_{part2['lower_snake']}}}",  # spooky{heebie_jeebies_boo_got_you}
            f"spooky{{{part1['story_clue_flat']}_{part2['full']}}}",   # spooky{heebiejeebies_BOOgotyou}
            f"spooky{{{part1['story_clue_flat']}_{part2['lower']}}}",  # spooky{heebiejeebies_boogotyou}
            f"spooky{{{part1['story_clue']}_{part2['tail']}}}",        # spooky{heebie_jeebies_gotyou}
        ]),

        # Set 3: Audio Spectrogram Tail ("so noped" / "noped") + PNG Part 2
        ("Category 3: Audio Spectrogram Tail + PNG Part 2", [
            f"spooky{{{part1['so_noped']}_{part2['full']}}}",          # spooky{so_noped_BOOgotyou}
            f"spooky{{{part1['so_noped']}_{part2['lower_snake']}}}",    # spooky{so_noped_boo_got_you}
            f"spooky{{{part1['sonoped']}_{part2['full']}}}",           # spooky{sonoped_BOOgotyou}
            f"spooky{{{part1['sonoped']}_{part2['lower_snake']}}}",     # spooky{sonoped_boo_got_you}
            f"spooky{{{part1['noped']}_{part2['lower_snake']}}}",       # spooky{noped_boo_got_you}
            f"spooky{{{part1['noped']}_{part2['snake']}}}",             # spooky{noped_BOO_got_you}
            f"spooky{{{part1['noped']}_{part2['tail']}}}",              # spooky{noped_gotyou}
            f"spooky{{{part1['noped']}_got_you}}",                      # spooky{noped_got_you}
        ]),

        # Set 4: Additional Story Keywords + PNG Part 2
        ("Category 4: Additional Story Keywords ('whispers' / 'skedaddled')", [
            f"spooky{{whispers_{part2['full']}}}",                     # spooky{whispers_BOOgotyou}
            f"spooky{{whispers_{part2['lower_snake']}}}",               # spooky{whispers_boo_got_you}
            f"spooky{{skedaddled_{part2['full']}}}",                   # spooky{skedaddled_BOOgotyou}
            f"spooky{{skedaddled_{part2['lower_snake']}}}",             # spooky{skedaddled_boo_got_you}
        ])
    ]

    counter = 1
    for cat_name, flags in candidates:
        print(f"\n--- {cat_name} ---")
        for flag in flags:
            print(f"  [{counter:2d}] {flag}")
            counter += 1

    print("\n" + "=" * 65)


if __name__ == "__main__":
    main()
