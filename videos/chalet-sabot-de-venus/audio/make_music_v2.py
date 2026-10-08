"""Energetic score for the dynamic cut (v2) — 120 BPM, D major (D - A - Bm - G, one chord per bar).

Groove from the hook, emotional breakdown on the mountain view (17.5-21.5 s),
drop on the montage (21.5 s), lighter build on the finale, resolved chord on
the logo (35.5 s).  python3 audio/make_music_v2.py -> assets/audio/music_v2.wav
"""
import wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 49.5
N = int(DUR * SR)
BEAT = 0.5
BAR = 2.0
rng = np.random.default_rng(33)
BD0, BD1, LOGO = 23.5, 28.0, 47.0  # after the reading holds (assets/timing_v2.json)
LIGHT = 40.0


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, f, o=2):
    return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x, axis=0)


def hp(x, f, o=2):
    return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x, axis=0)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x, axis=0)


def place(buf, t, sig):
    i = int(round(t * SR))
    if i < 0 or i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


def st(s, pan=0.0):
    return np.stack([s * (1 - pan), s * (1 + pan)], 1)


def piano(m, dur, vel=0.5):
    n = int((dur + 1.8) * SR)
    t = np.arange(n) / SR
    f = hz(m)
    s = np.zeros(n)
    for k in range(1, 9):
        fk = f * k * np.sqrt(1 + 0.00035 * k * k)
        if fk > 12000:
            break
        s += (1 / k ** 1.2) * ((0.55 + 0.6 * vel) ** (k - 1)) * np.sin(2 * np.pi * fk * t + k) * np.exp(-t * (1.0 + 0.5 * k + f / 900))
    s *= np.clip(t / 0.003, 0, 1) * np.clip((dur + 0.2 - t) / 0.3, 0, 1) ** 2
    return s * vel * 0.3


def strings(ms, dur, gain):
    n = int((dur + 1.2) * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for m in ms:
        for d, side in [(-7, 0), (-2, 1), (3, 0), (8, 1)]:
            f = hz(m) * 2 ** (d / 1200) * (1 + 0.0025 * np.sin(2 * np.pi * 5.2 * t))
            ph = np.cumsum(f) / SR + (m + d) * 0.13
            out[:, side] += 2 * (ph % 1) - 1
    env = np.clip(t / 0.6, 0, 1) * np.clip((dur + 1.0 - t) / 1.0, 0, 1)
    return lp(out * env[:, None], 2200) * gain * 0.016


PROG = [(38, [62, 66, 69], 74), (33, [61, 64, 69], 73), (35, [62, 66, 71], 71), (31, [62, 67, 71], 74)]
MEL = [[78, 76, 74, 76], [76, 73, 71, 73], [74, 73, 71, 69], [71, 74, 76, 78]]  # quarter-note hook per chord

pno = np.zeros((N + 3 * SR, 2))
strg = np.zeros((N + 3 * SR, 2))
bass = np.zeros(N + 3 * SR)
kick = np.zeros(N + 3 * SR)
clap = np.zeros(N + 3 * SR)
hats = np.zeros((N + 3 * SR, 2))
fx = np.zeros((N + 3 * SR, 2))

nb = int(np.ceil(DUR / BAR))
for b in range(nb):
    t0 = b * BAR
    root, tones, _ = PROG[b % 4]
    breakdown = BD0 - 0.01 <= t0 < BD1 - 0.01 or (BD0 - 0.01 <= t0 + BAR - 0.5 and t0 < BD0)
    in_bd = BD0 - 0.01 <= t0 + 0.6 < BD1 - 0.01
    logo = t0 >= LOGO - 0.6
    if logo:
        root, tones = 38, [62, 66, 69, 74]
    # strings: always, louder in the breakdown and finale
    g = 1.0 if in_bd else (0.55 if t0 < LOGO else 1.0)
    place(strg, t0, strings([root + 12] + tones + ([tones[1] + 12] if in_bd or logo else []), BAR if not logo else 3.0, g))
    if logo:
        for m in [root, root + 12] + tones + [tones[1] + 12]:
            place(pno, t0 + 0.0, st(piano(m, 2.4, 0.5), 0.0))
        continue
    # piano: off-beat chord stabs in the groove, flowing arpeggio in the breakdown
    if in_bd:
        for i, m in enumerate([tones[0], tones[1], tones[2], tones[1] + 12, tones[2], tones[1]] * 2):
            place(pno, t0 + i * BAR / 12 * 1.0 * 2 / 2, st(piano(m, 0.5, 0.33), -0.2 + 0.08 * (i % 5)))
        place(pno, t0, st(piano(MEL[b % 4][0] + 0, 1.6, 0.55), 0.1))
    else:
        for q in range(4):
            for m in tones:
                place(pno, t0 + q * BEAT + BEAT / 2, st(piano(m + 12, 0.18, 0.36), 0.15))
        if t0 >= 2.0:  # the hook melody on top
            for q, m in enumerate(MEL[b % 4]):
                place(pno, t0 + q * BEAT, st(piano(m, 0.42, 0.5), -0.1))
    # bass (eighths) and drums, not in the breakdown
    if not in_bd:
        for e in range(8):
            tt = t0 + e * BEAT / 2
            n = int(0.22 * SR)
            x = np.arange(n) / SR
            f = hz(root + (12 if e % 4 == 3 else 0))
            s = (np.sin(2 * np.pi * f * x) + 0.3 * (2 * ((f * x) % 1) - 1)) * np.exp(-x * 6) * np.clip(x / 0.004, 0, 1)
            place(bass, tt, lp(s, 420) * 0.34)
        light = t0 >= LIGHT  # finale: half-time feel
        for q in range(4):
            tb = t0 + q * BEAT
            if not light or q % 2 == 0:
                n = int(0.42 * SR)
                x = np.arange(n) / SR
                s = np.sin(2 * np.pi * np.cumsum(45 + 105 * np.exp(-x * 30)) / SR) * np.exp(-x * 8)
                place(kick, tb, s * 0.85)
            if q in (1, 3) and not light:
                n = int(0.3 * SR)
                x = np.arange(n) / SR
                env = sum(np.exp(-np.clip(x - o, 0, None) * 55) * (x >= o) for o in (0, 0.012, 0.024)) / 3 + np.exp(-x * 13) * 0.4
                place(clap, tb, bp(rng.standard_normal(n), 900, 3200) * env * 0.36)
            n = int(0.07 * SR)
            x = np.arange(n) / SR
            h = lp(hp(rng.standard_normal(n), 7000), 12000) * np.exp(-x * 50) * 0.07
            place(hats, tb + BEAT / 2, st(h, 0.3 if q % 2 else -0.3))

# risers into the drop and the logo, impacts on the hook and drop
def riser(t_end, d, gain):
    n = int(d * SR)
    x = np.arange(n) / SR
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    seg = n // 20
    for i in range(20):
        a, b = i * seg, (i + 1) * seg if i < 19 else n
        fc = 400 * (12 ** (i / 19))
        out[a:b] = bp(noise[a:b], fc * 0.7, min(fc * 1.5, 20000))
    out *= (x / d) ** 2.2 * gain
    place(fx, t_end - d, st(out))


def impact(t, gain):
    n = int(2.5 * SR)
    x = np.arange(n) / SR
    s = np.sin(2 * np.pi * np.cumsum(32 + 55 * np.exp(-x * 5)) / SR) * np.exp(-x * 1.8)
    s += lp(rng.standard_normal(n), 1500) * np.exp(-x * 12) * 0.8
    place(fx, t, st(s * gain))


riser(BD1, 1.8, 0.10)
riser(LOGO, 1.2, 0.08)
impact(0.0, 0.55)
impact(BD1, 0.55)
impact(LOGO, 0.45)

# sidechain on kicks
duck = np.ones(len(kick))
for b in range(nb):
    for q in range(4):
        tb = b * BAR + q * BEAT
        if tb < BD0 - 0.01 or BD1 - 0.01 <= tb < LOGO - 0.6:
            i = int(tb * SR)
            n = int(0.25 * SR)
            j = min(len(duck), i + n)
            duck[i:j] = np.minimum(duck[i:j], 0.5 + 0.5 * np.linspace(0, 1, n)[: j - i] ** 1.5)

irn = int(2.4 * SR)
it = np.arange(irn) / SR
ir = lp(rng.standard_normal((irn, 2)) * np.exp(-it * 2.6)[:, None], 6000)
ir /= np.sqrt(np.sum(ir ** 2))


def verb(x, wet):
    y = np.stack([fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return x + y * wet


mix = (verb(pno, 0.45) + verb(strg, 0.6)) * duck[:, None] + st(bass) * duck[:, None] + st(kick) + verb(st(clap), 0.5) + verb(hats, 0.25) + verb(fx, 0.4)
mix = hp(mix[:N], 28)
fo = int(1.2 * SR)
mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
mix /= np.max(np.abs(mix))
mix = np.tanh(mix * 1.5) / np.tanh(1.5) * 0.9
pcm = (mix * 32767).astype("<i2")
with wave.open("assets/audio/music_v2.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote assets/audio/music_v2.wav", N / SR, "s")
