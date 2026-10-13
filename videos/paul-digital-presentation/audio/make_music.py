"""Synthesized, royalty-free music bed for the Paul Digital presentation (fallback when the
FLORA music track is not available). 128 BPM, driving four-on-the-floor, sidechained bass.

Bar grid is anchored so the drop lands on the logo reveal (10.0 s) and the final hit on
the closing logo (40.0 s); one short breakdown bar before the property-types montage.
    python3 audio/make_music.py  ->  assets/audio/src/music_synth.wav
"""
import json
import os
import subprocess
import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(ROOT, "timing.json")))
DUR = T["duration"]
N = int(DUR * SR)
BPM = 128
BEAT = 60 / BPM
BAR = 4 * BEAT
DROP = 10.2
END = 39.6
OFF = DROP - 6 * BAR  # bar 0 starts here (negative = pre-roll)
BRK0, BRK1 = 25.1, 25.1 + BAR  # one-bar breakdown
rng = np.random.default_rng(5)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def filt(x, kind, f, o=2):
    return sosfilt(butter(o, f, kind, fs=SR, output="sos"), x, axis=0)


def saw(f, n, ph=0.0):
    t = np.arange(n) / SR
    return 2 * ((f * t + ph) % 1.0) - 1


def adsr(n, a, d, s, r):
    e = np.ones(n) * s
    A, D, R = min(int(a * SR), n), int(d * SR), int(r * SR)
    e[:A] = np.linspace(0, 1, A)
    D = min(D, n - A)
    e[A:A + D] = np.linspace(1, s, D)
    if 0 < R < n:
        e[-R:] *= np.linspace(1, 0, R)
    return e


def place(buf, t0, sig):
    i = int(round(t0 * SR))
    if i >= len(buf):
        return
    if i < 0:
        sig = sig[-i:]
        i = 0
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


def stereo(s, pan=0.0):
    return np.stack([s * (1 - pan), s * (1 + pan)], 1)


# B minor-ish driving progression: Bm - G - D - A
PROG = [([59, 62, 66, 71], 35), ([55, 59, 62, 67], 31), ([57, 62, 66, 69], 38), ([57, 61, 64, 69], 33)]
ARP = [0, 2, 1, 3, 2, 1, 3, 2, 0, 3, 1, 2, 3, 1, 2, 0]

pad = np.zeros((N, 2)); arp = np.zeros((N, 2)); bass = np.zeros(N); kick = np.zeros(N)
clap = np.zeros(N); hats = np.zeros((N, 2)); lead = np.zeros((N, 2)); fx = np.zeros((N, 2))
side = np.ones(N)  # sidechain gain from the kick

k = -1
while True:
    k += 1
    t0 = OFF + k * BAR
    if t0 >= DUR:
        break
    chord, root = PROG[k % 4]
    full = DROP - 0.01 <= t0 < END - 0.01 and not (BRK0 - 0.01 <= t0 < BRK1 - 0.01)
    intro = t0 < DROP - 0.01
    last = t0 >= END - 0.01
    # pad
    n = int((BAR + 0.5) * SR) if not last else int((DUR - t0 + 0.2) * SR)
    v = np.zeros((n, 2))
    for m in (chord if not last else [47, 54, 59, 62, 66, 71]):
        for d, sd in [(-8, 0), (-3, 1), (5, 0), (9, 1)]:
            v[:, sd] += saw(hz(m) * 2 ** (d / 1200), n, (m * 0.37 + d * 0.11) % 1)
    v *= adsr(n, 0.08, 0.3, 0.8, 0.4 if not last else 3.0)[:, None] * 0.045
    v = filt(v, "low", 700 + 2600 * min(1, max(0, (t0 - OFF) / (DROP - OFF))) if intro else 3200)
    place(pad, t0, v)
    # arp 16ths
    if not last:
        tones = [m + 12 for m in chord]
        for s16 in range(16):
            tp = t0 + s16 * BEAT / 4
            m = tones[ARP[s16] % 4] + (12 if s16 % 8 == 6 else 0)
            nn = int(0.2 * SR)
            tt = np.arange(nn) / SR
            f = hz(m)
            s = (saw(f, nn) * 0.55 + np.sin(2 * np.pi * f * tt)) * np.exp(-tt * 18) * 0.085
            cut = 900 + 3200 * max(0, (tp - OFF) / (DROP - OFF)) ** 2 if intro else 5200
            s = filt(s, "low", min(cut, 9000))
            place(arp, tp, stereo(s, 0.4 * np.sin(s16 * 1.7)))
    # drums
    for b in range(4):
        tb = t0 + b * BEAT
        if tb >= END - 0.01 or tb >= DUR:
            continue
        brk = BRK0 - 0.01 <= tb < BRK1 - 0.01
        if (full or (intro and t0 >= OFF + 2 * BAR - 0.01)) and not brk:
            nn = int(0.4 * SR)
            tt = np.arange(nn) / SR
            f = 48 + 120 * np.exp(-tt * 30)
            s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 8)
            s[:200] += rng.standard_normal(200) * np.linspace(0.12, 0, 200)
            place(kick, tb, s * (0.9 if full else 0.55))
            # sidechain dip
            dn = int(0.22 * SR)
            i0 = int(tb * SR)
            if 0 <= i0 < N:
                j = min(N, i0 + dn)
                side[i0:j] = np.minimum(side[i0:j], 0.35 + 0.65 * (np.arange(j - i0) / dn) ** 0.7)
        if full and b in (1, 3):
            nn = int(0.3 * SR)
            tt = np.arange(nn) / SR
            e = sum(np.exp(-np.clip(tt - o, 0, None) * 55) * (tt >= o) for o in (0, 0.01, 0.021)) / 3 + np.exp(-tt * 13) * 0.5
            place(clap, tb, filt(rng.standard_normal(nn), "band", [1000, 3500]) * e * 0.45)
        # hats: offbeat open-ish + 16th shaker from the start
        if not brk:
            nn = int(0.09 * SR)
            tt = np.arange(nn) / SR
            s = filt(rng.standard_normal(nn), "high", 7500) * np.exp(-tt * (26 if full else 45)) * (0.1 if full else 0.07)
            place(hats, tb + BEAT / 2, stereo(s, 0.3 if b % 2 else -0.3))
            if full or t0 >= OFF + BAR:
                for q in (0.25, 0.75):
                    nn = int(0.04 * SR)
                    tt = np.arange(nn) / SR
                    s = filt(rng.standard_normal(nn), "high", 9500) * np.exp(-tt * 100) * 0.04
                    place(hats, tb + q * BEAT, stereo(s))
    # bass: offbeat 8ths, sidechained
    if full:
        for e in range(8):
            nn = int(BEAT / 2 * SR * 0.92)
            tt = np.arange(nn) / SR
            f = hz(root + (12 if e % 2 else 0))
            s = (np.sin(2 * np.pi * f * tt) + 0.45 * saw(f, nn))
            s = filt(s, "low", 520) * adsr(nn, 0.004, 0.1, 0.75, 0.03) * 0.34
            place(bass, t0 + e * BEAT / 2, s)
    if last:
        nn = int(3.0 * SR)
        tt = np.arange(nn) / SR
        place(bass, t0, np.sin(2 * np.pi * hz(35) * tt) * np.exp(-tt * 1.2) * 0.55)
        nn = int(0.6 * SR)
        tt = np.arange(nn) / SR
        hit = np.sin(2 * np.pi * np.cumsum(45 + 140 * np.exp(-tt * 25)) / SR) * np.exp(-tt * 5)
        place(kick, t0, hit)
        place(fx, t0, stereo(filt(rng.standard_normal(int(1.6 * SR)), "high", 3000) * np.exp(-np.arange(int(1.6 * SR)) / SR * 3) * 0.15))

# lead hook from the site scene onwards (bright bell, 2-bar phrase)
MEL = [(78, 0, 0.5), (76, 0.5, 0.5), (74, 1, 1), (71, 2, 0.5), (74, 2.5, 0.5), (76, 3, 1),
       (78, 4, 0.5), (81, 4.5, 0.5), (78, 5, 1), (76, 6, 1), (74, 7, 1)]
start = OFF + int(np.ceil((19.4 - OFF) / BAR)) * BAR
rep = 0
while True:
    base = start + rep * 2 * BAR
    if base >= END - 0.01:
        break
    for m, st, ln in MEL:
        tp = base + st * BEAT
        if tp >= END - 0.01 or BRK0 - 0.01 <= tp < BRK1 - 0.01:
            continue
        nn = int((ln * BEAT + 0.4) * SR)
        tt = np.arange(nn) / SR
        ph = 2 * np.pi * hz(m) * tt
        s = (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.1 * np.sin(3 * ph)) * adsr(nn, 0.005, 0.2, 0.5, 0.3) * 0.06
        place(lead, tp, stereo(s, 0.1))
    rep += 1


def riser(t_end, d, g):
    n = int(d * SR)
    tt = np.arange(n) / SR
    s = filt(rng.standard_normal(n), "band", [1500, 9000]) * (tt / d) ** 2.2
    s += np.sin(2 * np.pi * np.cumsum(300 * 6 ** (tt / d)) / SR) * (tt / d) ** 2 * 0.25
    place(fx, t_end - d, stereo(s * g))


riser(DROP, 2 * BAR, 0.16)
riser(BRK1, BAR, 0.14)
riser(END, BAR, 0.14)

mix = pad * side[:, None] + arp + stereo(bass * side) + stereo(kick) * 0.9 + stereo(clap) + hats + lead + fx
mix = filt(mix, "high", 30)
mix /= np.abs(mix).max() + 1e-9
mix *= 0.8
out = os.path.join(ROOT, "assets/audio/src/music_synth.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s16le", out], input=mix.astype(np.float32).tobytes(), check=True)
print("wrote", out, f"{DUR:.1f}s")
