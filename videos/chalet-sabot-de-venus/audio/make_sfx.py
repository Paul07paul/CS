"""Subtle sound design for the chalet film (deterministic, royalty-free):
winter wind on exterior shots, soft airy transitions between rooms, very
discreet impacts under the key titles, tiny chimes on the services list,
a soft click on the booking button and a shimmer on the logo.
    python3 audio/make_sfx.py  ->  assets/audio/sfx.wav
"""
import wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 47.5
N = int(DUR * SR)
rng = np.random.default_rng(5)


def lp(x, f):
    return sosfilt(butter(2, f, "low", fs=SR, output="sos"), x, axis=0)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x, axis=0)


track = np.zeros((N + 3 * SR, 2))


def at(t, clip):
    i = int(t * SR)
    track[i : i + len(clip)] += clip


def wind(d, gain, fade=1.2):
    n = int(d * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for c in range(2):
        noise = rng.standard_normal(n)
        # slowly gusting band
        g = 0.6 + 0.4 * np.sin(2 * np.pi * (0.13 + 0.05 * c) * t + c) * np.sin(2 * np.pi * 0.31 * t + 1.3 * c)
        out[:, c] = bp(noise, 250, 1400) * g + lp(noise, 300) * 0.6
    env = np.clip(t / fade, 0, 1) * np.clip((d - t) / fade, 0, 1)
    out *= env[:, None]
    return out / np.max(np.abs(out)) * gain


def air(d=0.9, gain=0.05):
    n = int(d * SR)
    t = np.arange(n) / SR
    p = t / d
    s = bp(rng.standard_normal(n), 400, 2500) * np.sin(np.pi * p) ** 2
    pan = np.linspace(-0.4, 0.4, n)
    s = s / np.max(np.abs(s)) * gain
    return np.stack([s * (1 - pan), s * (1 + pan)], 1)


def impact(gain=0.10):
    d = 1.6
    t = np.arange(int(d * SR)) / SR
    sub = np.sin(2 * np.pi * np.cumsum(40 + 30 * np.exp(-t * 9)) / SR) * np.exp(-t * 3.5) * np.clip(t / 0.01, 0, 1)
    glass = sum(a * np.sin(2 * np.pi * f * t) for f, a in [(1760, 1), (2637, 0.5), (3520, 0.25)])
    glass *= np.exp(-t * 2.6) * np.clip(t / 0.004, 0, 1) * 0.12
    s = lp(sub, 200) + glass
    return np.stack([s, s], 1) * gain


def chime(f=2093, gain=0.035, pan=0.0):
    t = np.arange(int(1.2 * SR)) / SR
    s = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)) * np.exp(-t * 4) * np.clip(t / 0.004, 0, 1)
    return np.stack([s * (1 - pan), s * (1 + pan)], 1) * gain


def click(gain=0.06):
    t = np.arange(int(0.08 * SR)) / SR
    s = lp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 90) + np.sin(2 * np.pi * 900 * t) * np.exp(-t * 60) * 0.5
    return np.stack([s, s], 1) * gain


def shimmer(gain=0.05):
    out = np.zeros((int(2.0 * SR), 2))
    for k, f in enumerate([1568, 2093, 2349, 2637, 3136]):
        c = chime(f, gain * (1 - 0.12 * k), (k - 2) * 0.25)
        o = int(k * 0.07 * SR)
        out[o : o + len(c)] += c
    return out


# winter ambience
at(0.0, wind(5.6, 0.16))
at(26.0, wind(5.4, 0.07, 1.6))
at(30.9, wind(1.2, 0.05, 0.4))
at(39.4, wind(5.8, 0.15))
# airy transitions into each space
for t in [4.4, 8.6, 12.6, 15.6, 18.5, 19.7, 20.9, 21.8, 24.45, 26.0, 35.1, 39.4]:
    at(t, air(0.9, 0.05))
for t in [31.0, 31.6, 32.2, 32.8, 33.4, 34.0, 34.6]:
    at(t - 0.15, air(0.4, 0.03))
# discreet impacts under the key titles
for t in [1.9, 5.4, 9.4, 13.4, 16.4, 20.3, 22.6, 27.0, 31.3, 33.3, 40.3, 41.7]:
    at(t, impact(0.10))
at(0.8, chime(1568, 0.025))
at(29.6, chime(1760, 0.025))
# services
for i in range(6):
    at(35.9 + i * 0.42, chime([1568, 1760, 2093, 2349, 2637, 3136][i], 0.03, (i - 2.5) * 0.15))
# booking + signature
at(43.85, click(0.07))
at(43.9, chime(2637, 0.03))
at(45.3, shimmer(0.05))

# room reverb
irn = int(2.0 * SR)
it = np.arange(irn) / SR
ir = rng.standard_normal((irn, 2)) * np.exp(-it * 2.8)[:, None]
ir = lp(ir, 6000)
ir /= np.sqrt(np.sum(ir ** 2))
dry = track[:N]
wet = np.stack([fftconvolve(dry[:, c], ir[:, c])[:N] for c in range(2)], 1)
mix = dry * 0.85 + wet * 0.4
fo = int(1.5 * SR)
mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = np.clip(mix, -0.98, 0.98)

pcm = (mix * 32767).astype("<i2")
with wave.open("assets/audio/sfx.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote assets/audio/sfx.wav", N / SR, "s, peak", float(np.max(np.abs(mix))))
