"""Soft sound design for the Paul Digital ad (deterministic, royalty-free).

Rounded, low-passed effects with a room reverb, sitting under the music bed:
airy whooshes on camera moves, soft "bubble" pops on labels, gentle bell
chimes on reveals, muffled thuds for the villa assembly.
    python3 audio/make_sfx.py  ->  assets/audio/sfx.wav
"""
import wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 36.5
N = int(DUR * SR)
rng = np.random.default_rng(7)


def t_axis(d):
    return np.arange(int(d * SR)) / SR


def lp(x, f):
    return sosfilt(butter(2, f, "low", fs=SR, output="sos"), x, axis=0)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x, axis=0)


def stereo(sig, pan=0.0):
    return np.stack([sig * (1 - pan * 0.6), sig * (1 + pan * 0.6)], 1)


def whoosh(d=0.6, top=2800, gain=0.22, pan_from=-0.5, pan_to=0.5, attack=0.55):
    t = t_axis(d)
    n = len(t)
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    seg = max(1, n // 32)
    for i in range(32):  # band sweeping up then down
        a, b = i * seg, (i + 1) * seg if i < 31 else n
        k = np.sin(np.pi * (i + 0.5) / 32)
        fc = 250 + (top - 250) * k ** 1.4
        out[a:b] = bp(noise[a:b], fc * 0.55, min(fc * 1.5, 20000))
    p = np.linspace(0, 1, n)
    env = np.where(p < attack, (p / attack) ** 2, ((1 - p) / (1 - attack)) ** 1.6)
    out = lp(out * env, top * 1.2)
    out /= np.max(np.abs(out)) + 1e-9
    pan = np.linspace(pan_from, pan_to, n)
    return np.stack([out * (1 - pan * 0.6), out * (1 + pan * 0.6)], 1) * gain


def bubble(gain=0.16, f0=640, f1=420, pan=0.0):
    d = 0.22
    t = t_axis(d)
    f = f1 + (f0 - f1) * np.exp(-t * 30)
    sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.clip(t / 0.004, 0, 1) * np.exp(-t * 18)
    return stereo(sig * gain, pan)


def chime(gain=0.10, base=1046.5, pan=0.0, d=1.4):
    t = t_axis(d)
    sig = sum(a * np.sin(2 * np.pi * base * m * t) for m, a in [(1, 1), (2, 0.25), (3, 0.08)])
    sig *= np.clip(t / 0.006, 0, 1) * np.exp(-t * 3.2)
    return stereo(sig * gain, pan)


def thud(gain=0.22, f0=120, f1=55):
    d = 0.5
    t = t_axis(d)
    f = f1 + (f0 - f1) * np.exp(-t * 14)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.clip(t / 0.006, 0, 1) * np.exp(-t * 8)
    return stereo(lp(body, 400) * gain)


def swell(gain=0.3, d=1.8):
    t = t_axis(d)
    f = 38 + 30 * np.exp(-t * 3)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.clip(t / 0.05, 0, 1) * np.exp(-t * 2.0)
    air = lp(rng.standard_normal(len(t)), 900) * np.clip(t / 0.08, 0, 1) * np.exp(-t * 4) * 0.4
    return stereo((sub + air) * gain)


def sparkle(gain=0.06, pan=0.0):
    out = np.zeros((int(1.4 * SR), 2))
    for k, fr in enumerate([2093, 2637, 3136, 3951]):
        c = chime(gain * (1 - k * 0.15), fr, pan + (k - 1.5) * 0.2, 1.0)
        o = int(k * 0.06 * SR)
        out[o : o + len(c)] += c[: len(out) - o]
    return out


def riser(d=0.8, gain=0.08):
    t = t_axis(d)
    n = len(t)
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    seg = n // 16
    for i in range(16):
        a, b = i * seg, (i + 1) * seg if i < 15 else n
        fc = 300 * (8 ** (i / 15))
        out[a:b] = bp(noise[a:b], fc * 0.7, fc * 1.4)
    out *= (t / d) ** 2
    out[-int(0.04 * SR):] *= np.linspace(1, 0, int(0.04 * SR))
    return stereo(out / (np.max(np.abs(out)) + 1e-9) * gain)


track = np.zeros((N + 2 * SR, 2))


def at(time, clip):
    i = int(time * SR)
    track[i : i + len(clip)] += clip


PENTA = [1046.5, 1174.7, 1318.5, 1568.0, 1760.0, 2093.0]

# ---- S1 listing → video (0 – 5.5)
at(0.0, whoosh(1.3, 1800, 0.14, 0.3, -0.3, 0.2))
at(0.45, bubble(0.10, 560, 380))
at(1.5, whoosh(0.5, 2600, 0.10, -0.2, 0.2, 0.8))
at(2.0, chime(0.07, 1568))
at(2.5, whoosh(0.8, 2400, 0.16, -0.5, 0.5))
at(2.95, riser(0.55, 0.06))
at(3.45, whoosh(0.4, 3200, 0.14, 0.0, 0.0, 0.3))
at(3.5, chime(0.08, 1318.5))
at(3.9, bubble(0.12, 700, 460))
at(4.15, bubble(0.09, 620, 420, -0.5))
at(4.3, bubble(0.09, 760, 500, 0.5))
at(4.95, whoosh(0.6, 3200, 0.20, 0.0, 0.0, 0.85))
# ---- S2 villa (5.5 – 18)
at(5.5, swell(0.30))
for k, tm in enumerate([5.68, 5.85, 6.05, 6.25, 6.45]):
    at(tm, thud(0.14 + 0.02 * k, 130 - k * 6, 55))
at(6.5, chime(0.07, 1046.5, 0, 1.6))
at(7.95, whoosh(0.9, 2200, 0.16, -0.4, 0.4))
for tm, p, f in [(8.65, 0.0, 600), (8.95, -0.4, 660), (9.25, 0.4, 720)]:
    at(tm, bubble(0.11, f, f * 0.66, p))
at(8.5, whoosh(0.6, 2000, 0.10, 0.0, 0.0, 0.3))
at(10.95, whoosh(0.7, 3000, 0.16, 0.0, 0.0, 0.3))
at(11.05, riser(0.5, 0.05))
for i, (tm, p) in enumerate([(11.7, -0.3), (12.7, -0.1), (13.7, 0.1), (14.7, 0.3)]):
    at(tm, chime(0.08, PENTA[i + 1], p))
    at(tm + 0.1, bubble(0.09, 640, 430, p))
for tm in [12.55, 13.55, 14.55]:
    at(tm, whoosh(0.6, 1800, 0.10, -0.3, 0.3))
at(15.5, thud(0.16, 110, 50))
at(15.55, whoosh(1.3, 2200, 0.18, 0.4, -0.4))
at(16.35, whoosh(0.6, 1600, 0.08, -0.6, 0.6, 0.2))
at(16.4, bubble(0.12, 520, 340))
at(16.65, whoosh(0.7, 3000, 0.07, -0.5, 0.5, 0.4))
for tm, p, f in [(17.0, 0.4, 600), (17.12, -0.4, 680), (17.24, 0.0, 760)]:
    at(tm, bubble(0.09, f, f * 0.66, p))
at(17.65, whoosh(0.45, 3200, 0.20, 0.6, -0.6, 0.7))
# ---- S3 turnkey (18 – 21.5)
at(18.0, whoosh(0.45, 2400, 0.12, 0.6, -0.2, 0.25))
for i, tm in enumerate([18.4, 19.0, 19.6]):
    at(tm, bubble(0.11, 560 + i * 80, 380 + i * 50))
at(18.65, whoosh(0.5, 2800, 0.09, 0.5, -0.5))
at(19.1, riser(0.75, 0.05))
at(19.85, chime(0.10, 1568, 0, 1.6))
at(20.05, whoosh(0.6, 2000, 0.12, 0.0, 0.0, 0.3))
at(21.15, whoosh(0.4, 3200, 0.18, 0.0, 0.0, 0.8))
# ---- S4 proof, benefits, formats (21.5 – 30.5)
at(21.5, whoosh(0.4, 2400, 0.12, 0.0, 0.0, 0.2))
for i, tm in enumerate([21.7, 22.0, 22.3]):
    at(tm, thud(0.13, 150, 70))
    at(tm + 0.02, chime(0.05, PENTA[i * 2], 0, 0.8))
at(23.7, whoosh(0.45, 2600, 0.14, 0.0, 0.0, 0.6))
at(24.0, whoosh(0.5, 2000, 0.10, 0.0, 0.0, 0.3))
for i in range(5):
    tm = 24.25 + i * 0.3
    at(tm, whoosh(0.35, 2200, 0.06, -0.5 if i % 2 == 0 else 0.5, 0.0, 0.3))
    at(tm + 0.2, chime(0.07, PENTA[i], (i - 2) * 0.2, 1.0))
at(26.7, whoosh(0.4, 2400, 0.14, 0.0, 0.0, 0.6))
at(27.1, whoosh(0.7, 2000, 0.16, 0.0, 0.0, 0.25))
at(27.3, whoosh(0.6, 2600, 0.10, 0.6, 0.0, 0.25))
at(27.45, whoosh(0.6, 2600, 0.10, 0.6, 0.0, 0.25))
for i, tm in enumerate([27.95, 28.13, 28.31]):
    at(tm, bubble(0.10, 600 + i * 70, 420 + i * 40, (i - 1) * 0.4))
at(30.1, whoosh(0.4, 3200, 0.18, 0.0, 0.0, 0.8))
# ---- S5 CTA + logo (30.5 – 36.5)
at(30.5, swell(0.24, 1.6))
at(30.8, chime(0.08, 1318.5, 0, 1.6))
at(32.9, whoosh(0.6, 2400, 0.14, 0.0, 0.0, 0.5))
at(33.25, whoosh(0.4, 3000, 0.12, -0.4, 0.4, 0.6))
at(33.4, bubble(0.12, 520, 330))
at(33.5, sparkle(0.07))
at(33.65, whoosh(0.4, 2200, 0.08, -0.3, 0.0, 0.5))
at(33.8, whoosh(0.4, 2400, 0.08, 0.0, 0.3, 0.5))
at(34.4, sparkle(0.05, 0.3))

# ---- room reverb (convolution) for a soft, non-dry finish
irn = int(1.6 * SR)
it = np.arange(irn) / SR
ir = np.stack([rng.standard_normal(irn), rng.standard_normal(irn)], 1) * np.exp(-it * 3.8)[:, None]
ir = lp(ir, 5000)
ir /= np.sqrt(np.sum(ir ** 2))
dry = track[:N]
wet = np.stack([fftconvolve(dry[:, c], ir[:, c])[:N] for c in range(2)], 1)
mix = dry * 0.85 + wet * 0.45
mix = lp(mix, 9000)
fade = int(0.8 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix /= np.max(np.abs(mix))
mix = np.tanh(mix * 1.2) / np.tanh(1.2) * 0.7

pcm = (mix * 32767).astype("<i2")
with wave.open("assets/audio/sfx.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote assets/audio/sfx.wav", N / SR, "s")
