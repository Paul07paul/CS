"""Sound design for the dynamic cut (v2): whooshes on every transition, punchy-but-soft
hits on the kinetic words, ticks on counters, pops on chips/cards, wind on the
exteriors, booking click and logo shimmer.  -> assets/audio/sfx_v2.wav"""
import wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 49.5
N = int(DUR * SR)
rng = np.random.default_rng(8)


def lp(x, f):
    return sosfilt(butter(2, f, "low", fs=SR, output="sos"), x, axis=0)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x, axis=0)


track = np.zeros((N + 3 * SR, 2))


import json
HOLDS = json.load(open("assets/timing_v2.json"))["holds"]


def T(t):  # event times are authored on the original 38 s cut
    return t + sum(e for h, e in HOLDS if t > h + 1e-6)


def at(t, c):
    i = int(T(t) * SR)
    track[i : i + len(c)] += c


def st(s, pan=0.0):
    return np.stack([s * (1 - pan), s * (1 + pan)], 1)


def whoosh(d=0.45, top=4000, gain=0.22, p0=-0.6, p1=0.6):
    n = int(d * SR)
    x = np.arange(n) / SR
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    seg = n // 24
    for i in range(24):
        a, b = i * seg, (i + 1) * seg if i < 23 else n
        k = np.sin(np.pi * (i + 0.5) / 24)
        fc = 300 + (top - 300) * k ** 1.3
        out[a:b] = bp(noise[a:b], fc * 0.5, min(fc * 1.6, 20000))
    p = x / d
    out *= np.where(p < 0.6, (p / 0.6) ** 2, ((1 - p) / 0.4) ** 1.5)
    out /= np.max(np.abs(out)) + 1e-9
    pan = np.linspace(p0, p1, n)
    return np.stack([out * (1 - pan * 0.6), out * (1 + pan * 0.6)], 1) * gain


def hit(gain=0.25):
    n = int(0.9 * SR)
    x = np.arange(n) / SR
    s = np.sin(2 * np.pi * np.cumsum(50 + 90 * np.exp(-x * 25)) / SR) * np.exp(-x * 7)
    s += lp(rng.standard_normal(n), 2500) * np.exp(-x * 30) * 0.5
    return st(s * gain)


def tick(gain=0.05, f=2400):
    n = int(0.04 * SR)
    x = np.arange(n) / SR
    return st(np.sin(2 * np.pi * f * x) * np.exp(-x * 120) * gain)


def pop(gain=0.10, f0=700, f1=450, pan=0.0):
    n = int(0.2 * SR)
    x = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-x * 30)
    return st(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 20) * np.clip(x / 0.003, 0, 1) * gain, pan)


def wind(d, gain):
    n = int(d * SR)
    x = np.arange(n) / SR
    out = np.stack([bp(rng.standard_normal(n), 250, 1400) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.2 * x + c)) for c in range(2)], 1)
    out *= (np.clip(x / 0.8, 0, 1) * np.clip((d - x) / 0.8, 0, 1))[:, None]
    return out / np.max(np.abs(out)) * gain


def chime(f, gain=0.04, pan=0.0):
    x = np.arange(int(1.2 * SR)) / SR
    return st((np.sin(2 * np.pi * f * x) + 0.3 * np.sin(4 * np.pi * f * x)) * np.exp(-x * 4) * np.clip(x / 0.004, 0, 1) * gain, pan)


# exteriors
at(0.0, wind(3.4, 0.10))
at(30.4, wind(7.3, 0.08))
# transitions
for t, p in [(1.95, -1), (3.95, 1), (5.95, -1), (9.45, 1), (11.45, -1), (14.95, 1), (17.4, -1), (23.95, 1), (27.95, -1), (30.4, 1), (35.4, -1)]:
    at(t, whoosh(0.5, 4200, 0.22, 0.6 * p, -0.6 * p))
for i in range(8):
    at(21.5 + i * 0.33 - 0.05, whoosh(0.18, 5000, 0.07, -0.4, 0.4))
# hits on kinetic words
for t in [0.15, 2.45, 6.7, 9.8, 11.65, 15.15, 17.9, 21.55, 22.2, 22.85, 23.5, 24.45, 30.8]:
    at(t, hit(0.22))
# counters
for t0, n, d in [(4.25, 14, 1.2), (11.65, 5, 0.8), (24.25, 6, 0.7)]:
    for k in range(n):
        at(t0 + d * (1 - (1 - (k + 1) / n) ** 0.6), tick(0.045, 2200 + 60 * k))
for i in range(4):
    for k in range(6):
        at(28.3 + i * 0.18 + 0.9 * (1 - (1 - (k + 1) / 6) ** 0.6), tick(0.03, 2500))
# pin drop, chips, cards
at(5.1, pop(0.12, 520, 300))
for t in [3.0, 7.4, 7.55, 7.7, 10.4, 10.6, 13.0, 13.2, 15.9, 16.05, 16.3]:
    at(t, pop(0.09))
for i in range(4):
    at(12.1 + i * 0.12, pop(0.07, 800, 520, (i - 1.5) * 0.3))
for i in range(6):
    at(25.0 + i * 0.22, pop(0.08, 650 + 40 * i, 430, (i % 2 - 0.5) * 0.6))
for i in range(4):
    at(28.2 + i * 0.18, whoosh(0.3, 3500, 0.06, 0.6, 0.0))
# view: soft chime
at(18.5, chime(1568, 0.05)); at(19.0, chime(2349, 0.04))
# booking + logo
x = np.arange(int(0.08 * SR)) / SR
at(34.2, st((lp(rng.standard_normal(len(x)), 3000) * np.exp(-x * 90) + np.sin(2 * np.pi * 900 * x) * np.exp(-x * 60) * 0.5) * 0.08))
at(34.25, chime(2637, 0.04))
for k, f in enumerate([1568, 2093, 2349, 2637, 3136]):
    at(35.85 + k * 0.07, chime(f, 0.05 * (1 - 0.12 * k), (k - 2) * 0.25))

irn = int(1.4 * SR)
it = np.arange(irn) / SR
ir = lp(rng.standard_normal((irn, 2)) * np.exp(-it * 3.5)[:, None], 6000)
ir /= np.sqrt(np.sum(ir ** 2))
dry = track[:N]
mix = dry * 0.9 + np.stack([fftconvolve(dry[:, c], ir[:, c])[:N] for c in range(2)], 1) * 0.3
mix = np.clip(mix, -0.98, 0.98)
pcm = (mix * 32767).astype("<i2")
with wave.open("assets/audio/sfx_v2.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote assets/audio/sfx_v2.wav", float(np.max(np.abs(mix))))
