"""Sound design for the Courchevel Moriond YouTube film: whooshes on scene changes,
soft hits under the big titles, ticks on counters, pops on pills/cards, water and
ember textures for the wellness scene, booking click and logo shimmer."""
import wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 99.0
N = int(DUR * SR)
rng = np.random.default_rng(12)


def lp(x, f):
    return sosfilt(butter(2, f, "low", fs=SR, output="sos"), x, axis=0)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x, axis=0)


track = np.zeros((N + 3 * SR, 2))


def at(t, c):
    i = int(t * SR)
    track[i : i + len(c)] += c


def st(s, pan=0.0):
    return np.stack([s * (1 - pan), s * (1 + pan)], 1)


def whoosh(d=0.5, top=4000, gain=0.2, p0=-0.6, p1=0.6):
    n = int(d * SR)
    x = np.arange(n) / SR
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    seg = n // 24
    for i in range(24):
        a, b = i * seg, (i + 1) * seg if i < 23 else n
        fc = 300 + (top - 300) * np.sin(np.pi * (i + 0.5) / 24) ** 1.3
        out[a:b] = bp(noise[a:b], fc * 0.5, min(fc * 1.6, 20000))
    p = x / d
    out *= np.where(p < 0.6, (p / 0.6) ** 2, ((1 - p) / 0.4) ** 1.5)
    out /= np.max(np.abs(out)) + 1e-9
    pan = np.linspace(p0, p1, n)
    return np.stack([out * (1 - pan * 0.6), out * (1 + pan * 0.6)], 1) * gain


def hit(gain=0.2):
    n = int(1.0 * SR)
    x = np.arange(n) / SR
    s = np.sin(2 * np.pi * np.cumsum(48 + 90 * np.exp(-x * 22)) / SR) * np.exp(-x * 6)
    s += lp(rng.standard_normal(n), 2200) * np.exp(-x * 28) * 0.45
    return st(s * gain)


def tick(gain=0.04, f=2400):
    x = np.arange(int(0.04 * SR)) / SR
    return st(np.sin(2 * np.pi * f * x) * np.exp(-x * 120) * gain)


def pop(gain=0.09, f0=700, f1=450, pan=0.0):
    x = np.arange(int(0.2 * SR)) / SR
    f = f1 + (f0 - f1) * np.exp(-x * 30)
    return st(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 20) * np.clip(x / 0.003, 0, 1) * gain, pan)


def chime(f, gain=0.04, pan=0.0):
    x = np.arange(int(1.2 * SR)) / SR
    return st((np.sin(2 * np.pi * f * x) + 0.3 * np.sin(4 * np.pi * f * x)) * np.exp(-x * 4) * np.clip(x / 0.004, 0, 1) * gain, pan)


def texture(d, lo, hi, gain):
    n = int(d * SR)
    x = np.arange(n) / SR
    s = np.stack([bp(rng.standard_normal(n), lo, hi) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.3 * x + c)) for c in range(2)], 1)
    s *= (np.clip(x / 0.8, 0, 1) * np.clip((d - x) / 0.8, 0, 1))[:, None]
    return s / np.max(np.abs(s)) * gain


# scene changes
at(4.4, whoosh(2.2, 2600, 0.16, 0.0, 0.0))  # window opening onto the mountains
for k in range(6):
    at(0.9 + k * 0.1, tick(0.035, 1800 + 120 * k))  # letter reveal
for t, p in [(6.85, 1), (14.7, -1), (24.7, 0), (34.7, 1), (41.7, -1), (53.7, 1), (59.7, 0), (65.25, 1), (69.75, 0), (74.7, -1), (81.7, 1), (87.7, 0), (95.3, 0)]:
    at(t, whoosh(0.55, 4200, 0.2, 0.6 * p, -0.6 * p))
# big titles
for t in [0.9, 7.7, 15.4, 25.8, 30.3, 35.7, 42.4, 49.0, 54.3, 61.4, 65.9, 70.7, 75.5, 88.3]:
    at(t, hit(0.2))
# counters
for i in range(4):
    for k in range(8):
        at(15.8 + i * 0.25 + 1.2 * (1 - (1 - (k + 1) / 8) ** 0.6), tick(0.03, 2300 + 80 * i))
for k in range(12):
    at(18.8 + 1.5 * (1 - (1 - (k + 1) / 12) ** 0.6), tick(0.035, 2600))
# pins, pills, cards
at(9.9, pop(0.12, 520, 300))
for t in [10.8, 11.1, 20.4, 20.6, 20.8, 27.2, 31.6, 37.0, 37.25, 50.2, 84.0]:
    at(t, pop(0.08))
for i in range(4):
    at(43.0 + i * 0.18, whoosh(0.3, 3000, 0.05, 0.5, -0.2))
    at(55.1 + i * 0.15, whoosh(0.25, 3000, 0.05, -0.3, 0.3))
    at(82.6 + i * 0.25, pop(0.07, 650 + 40 * i, 430))
for i in range(8):
    at(76.0 + i * 0.2, pop(0.06, 620 + 30 * i, 420, (i % 4 - 1.5) * 0.3))
# wellness textures: water then ember
at(60.2, texture(5.0, 300, 2500, 0.05))
at(65.4, texture(4.4, 120, 900, 0.06))
at(61.4, chime(1568, 0.04)); at(65.9, chime(1175, 0.04))
# booking + logo
x = np.arange(int(0.08 * SR)) / SR
at(93.1, st((lp(rng.standard_normal(len(x)), 3000) * np.exp(-x * 90) + np.sin(2 * np.pi * 900 * x) * np.exp(-x * 60) * 0.5) * 0.08))
at(93.2, chime(2637, 0.04))
for k, f in enumerate([1568, 2093, 2349, 2637, 3136]):
    at(95.85 + k * 0.07, chime(f, 0.05 * (1 - 0.12 * k), (k - 2) * 0.25))

irn = int(1.4 * SR)
it = np.arange(irn) / SR
ir = lp(rng.standard_normal((irn, 2)) * np.exp(-it * 3.5)[:, None], 6000)
ir /= np.sqrt(np.sum(ir ** 2))
dry = track[:N]
mix = dry * 0.9 + np.stack([fftconvolve(dry[:, c], ir[:, c])[:N] for c in range(2)], 1) * 0.3
mix = mix * 2.5  # no music bed any more: effects carry the soundtrack
mix = np.tanh(mix * 1.1) / np.tanh(1.1) * 0.92
pcm = (mix * 32767).astype("<i2")
with wave.open("assets/audio/sfx.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote assets/audio/sfx.wav")
