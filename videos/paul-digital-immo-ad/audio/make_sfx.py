"""Synthesize the Paul Digital ad sound-design track (deterministic, royalty-free).

Every effect is generated from math (seeded noise), then placed at the global
timestamps of the on-screen events and mixed into one stereo track:
    python3 audio/make_sfx.py  ->  assets/audio/sfx.wav
"""
import wave
import numpy as np

SR = 48000
DUR = 32.0
rng = np.random.default_rng(7)


def t_axis(d):
    return np.arange(int(d * SR)) / SR


def lowpass(x, cutoff):
    """One-pole low-pass; cutoff may be an array (time-varying)."""
    cutoff = np.broadcast_to(np.asarray(cutoff, dtype=float), x.shape)
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


def env_ad(n, attack, decay_pow=2.0):
    """Attack/decay envelope over n samples; attack is a 0..1 fraction."""
    p = np.linspace(0, 1, n)
    a = max(attack, 1e-4)
    up = np.clip(p / a, 0, 1)
    down = np.clip((1 - p) / (1 - a), 0, 1) ** decay_pow
    return np.where(p < a, up, down)


def whoosh(d=0.5, lo=300, hi=4000, attack=0.65, gain=0.5, pan_from=-0.6, pan_to=0.6):
    t = t_axis(d)
    n = len(t)
    noise = rng.standard_normal(n)
    sweep = lo + (hi - lo) * np.sin(np.linspace(0, np.pi, n)) ** 1.5
    band = lowpass(noise, sweep) - lowpass(noise, sweep * 0.25)
    sig = band * env_ad(n, attack, 1.6)
    sig /= np.max(np.abs(sig)) + 1e-9
    pan = np.linspace(pan_from, pan_to, n)
    return np.stack([sig * (1 - pan) / 2 * 2, sig * (1 + pan) / 2 * 2], 1) * gain


def mono(sig, gain=1.0, pan=0.0):
    sig = sig / (np.max(np.abs(sig)) + 1e-9) * gain
    return np.stack([sig * (1 - pan), sig * (1 + pan)], 1)


def pop(gain=0.35, f0=1100, f1=320, pan=0.0):
    d = 0.16
    t = t_axis(d)
    f = f1 + (f0 - f1) * np.exp(-t * 45)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = np.sin(ph) * np.exp(-t * 28)
    sig[:60] += rng.standard_normal(60) * np.linspace(1, 0, 60) * 0.6
    return mono(sig, gain, pan)


def tick(gain=0.22, f=2800, pan=0.0):
    d = 0.05
    t = t_axis(d)
    sig = np.sin(2 * np.pi * f * t) * np.exp(-t * 140) + rng.standard_normal(len(t)) * np.exp(-t * 300) * 0.3
    return mono(sig, gain, pan)


def thud(gain=0.5, f0=110, f1=42):
    d = 0.45
    t = t_axis(d)
    f = f1 + (f0 - f1) * np.exp(-t * 18)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 9)
    noise = lowpass(rng.standard_normal(len(t)), 900) * np.exp(-t * 30) * 2.5
    return mono(body + noise, gain)


def boom(gain=0.75, d=2.2):
    t = t_axis(d)
    f = 34 + 46 * np.exp(-t * 6)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.exp(-t * 2.2)
    hit = lowpass(rng.standard_normal(len(t)), 1800) * np.exp(-t * 14) * 3
    shimmer = sum(np.sin(2 * np.pi * fr * t + k) for k, fr in enumerate([1568, 2093, 2637, 3136]))
    shimmer = shimmer * np.exp(-t * 1.6) * np.clip(t / 0.05, 0, 1) * 0.05
    return mono(sub + hit + shimmer, gain)


def chime(gain=0.22, base=1320, pan=0.0, d=0.9):
    t = t_axis(d)
    sig = sum(a * np.sin(2 * np.pi * base * m * t) for m, a in [(1, 1), (1.5, 0.5), (2, 0.35), (3, 0.12)])
    sig *= np.exp(-t * 5) * np.clip(t / 0.004, 0, 1)
    return mono(sig, gain, pan)


def riser(d=0.8, gain=0.3):
    t = t_axis(d)
    n = len(t)
    noise = lowpass(rng.standard_normal(n), np.linspace(400, 7000, n))
    f = np.linspace(220, 880, n)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35
    sig = (noise + tone) * np.linspace(0, 1, n) ** 2
    sig[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR))
    return mono(sig, gain)


def shutter(gain=0.3):
    a = tick(gain, 1900)
    b = tick(gain * 0.8, 1500)
    out = np.zeros((int(0.12 * SR), 2))
    out[: len(a)] += a
    o = int(0.055 * SR)
    out[o : o + len(b)] += b
    return out


def beep(gain=0.12, f=1000):
    d = 0.09
    t = t_axis(d)
    sig = np.sin(2 * np.pi * f * t) * np.clip(t / 0.005, 0, 1) * np.clip((d - t) / 0.01, 0, 1)
    return mono(sig, gain)


track = np.zeros((int(DUR * SR) + SR, 2))


def at(time, clip):
    i = int(time * SR)
    track[i : i + len(clip)] += clip[: len(track) - i]


# ---- S1 listing → video (0 – 5.5)
at(0.0, whoosh(1.4, 200, 2200, 0.15, 0.35, 0.3, -0.3))
at(0.45, pop(0.22, 900, 400))
at(1.5, whoosh(0.45, 600, 5000, 0.8, 0.18))
at(1.98, shutter(0.32))
at(1.9, beep())
at(2.5, whoosh(0.7, 250, 3000, 0.5, 0.35, -0.5, 0.5))
at(2.95, riser(0.5, 0.18))
at(3.42, whoosh(0.35, 800, 6000, 0.3, 0.3))
at(3.45, thud(0.3, 140, 60))
at(3.9, pop(0.3, 1200, 380))
at(4.15, pop(0.22, 1000, 450, -0.4))
at(4.3, pop(0.22, 1250, 500, 0.4))
at(4.95, whoosh(0.6, 300, 7000, 0.85, 0.55))
# ---- S2 villa (5.5 – 16.5)
at(5.5, boom(0.55, 1.6))
for k, tm in enumerate([5.68, 5.82, 5.95, 6.12, 6.28]):
    at(tm, thud(0.22 + 0.02 * k, 160 - k * 8, 60))
at(6.5, thud(0.42, 120, 45))
at(6.55, chime(0.10, 1046))
at(7.9, whoosh(0.9, 200, 2600, 0.5, 0.4, -0.4, 0.4))
for tm, p in [(8.65, 0.0), (8.95, -0.3), (9.25, 0.4)]:
    at(tm, pop(0.28, 1150, 420, p))
at(10.4, whoosh(0.7, 400, 5000, 0.3, 0.4, 0.0, 0.0))
at(10.5, riser(0.5, 0.12))
for tm, p in [(11.2, -0.2), (12.2, 0.0), (13.2, 0.2)]:
    at(tm, chime(0.13, 1318, p))
    at(tm + 0.1, pop(0.22, 1050, 420, p))
for tm in [12.03, 13.03]:
    at(tm, whoosh(0.6, 250, 2500, 0.5, 0.25, -0.3, 0.3))
at(14.0, thud(0.35, 130, 50))
at(14.05, whoosh(1.3, 150, 3200, 0.55, 0.45, 0.4, -0.4))
for k in range(12):
    at(14.85 + k * 0.04, tick(0.08, 1200 + (k % 4) * 150, (k % 3 - 1) * 0.5))
at(14.85, whoosh(0.3, 900, 5000, 0.7, 0.15))
at(15.2, thud(0.3, 200, 90))
at(15.15, whoosh(0.7, 1500, 6000, 0.4, 0.12, -0.5, 0.5))
for tm, p in [(15.5, 0.4), (15.62, -0.4), (15.74, 0.0)]:
    at(tm, pop(0.24, 1200, 450, p))
at(16.15, whoosh(0.45, 400, 6500, 0.7, 0.55, 0.6, -0.6))
# ---- S3 turnkey (16.5 – 20)
at(16.95, pop(0.3, 1000, 350))
at(17.25, whoosh(0.5, 900, 6000, 0.6, 0.25, 0.5, -0.5))
at(17.7, pop(0.3, 1050, 360))
at(17.8, riser(0.85, 0.16))
for tm in [17.95, 18.13, 18.31]:
    at(tm, tick(0.18, 2400))
at(18.45, pop(0.3, 1100, 370))
at(18.75, chime(0.24, 1568))
at(19.6, whoosh(0.4, 400, 7000, 0.8, 0.45))
# ---- S4 proof + benefits (20 – 26)
at(20.0, whoosh(0.35, 500, 4000, 0.2, 0.3))
for tm in [20.2, 20.52, 20.84]:
    at(tm, thud(0.28, 170, 70))
tick_times = np.concatenate([20.3 + np.cumsum(np.linspace(0.05, 0.16, 6)), 20.9 + np.cumsum(np.linspace(0.03, 0.12, 14))])
for k, tm in enumerate(tick_times):
    at(tm, tick(0.07, 3200 - (k % 5) * 120))
at(22.15, whoosh(0.4, 400, 5000, 0.6, 0.35, 0.0, 0.0))
at(22.35, whoosh(0.7, 200, 2400, 0.25, 0.4, 0.0, 0.0))
for tm in [23.6, 24.6]:
    at(tm, whoosh(0.35, 800, 5000, 0.4, 0.22, 0.4, -0.4))
for k, tm in enumerate([23.17, 23.5, 23.83, 24.16, 24.49]):
    at(tm, pop(0.22, 900 + k * 60, 380))
    at(tm + 0.1, tick(0.14, 2600 + k * 120))
at(25.55, whoosh(0.5, 400, 7000, 0.8, 0.5))
# ---- S5 CTA (26 – 32)
at(26.0, boom(0.45, 1.4))
at(26.32, thud(0.4, 120, 48))
at(26.3, chime(0.12, 1046, 0, 1.4))
at(28.4, whoosh(0.6, 250, 3500, 0.5, 0.35))
at(29.2, whoosh(0.55, 500, 5500, 0.7, 0.3, -0.5, 0.5))
for k in range(12):
    at(29.35 + k * 0.035, tick(0.06, 1800 + k * 60, (k / 11 - 0.5)))
at(29.55, shutter(0.32))
at(29.7, boom(0.8, 2.2))
at(31.9, beep(0.0))

# light room reverb (two feedback taps) for glue
mix = track.copy()
for delay, g in [(0.043, 0.22), (0.071, 0.16), (0.113, 0.11)]:
    d = int(delay * SR)
    mix[d:] += track[:-d] * g
mix = mix[: int(DUR * SR)]
# fade out the tail so the last frame ends clean
fade = int(0.6 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
peak = np.max(np.abs(mix))
mix = np.tanh(mix / peak * 1.4) / np.tanh(1.4) * 0.89

pcm = (mix * 32767).astype("<i2")
with wave.open("assets/audio/sfx.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote assets/audio/sfx.wav", len(pcm) / SR, "s")
