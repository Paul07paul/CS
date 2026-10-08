"""Instrumental score for the Chalet Le Sabot de Venus film (deterministic, royalty-free).

Piano + strings in D major (D - A/C# - Bm - G), one chord every 2.5 s.
Calm piano intro, strings enter inside the chalet, emotional swell on the
mountain view (26.2 s), a soft pulse under the montage, calm services,
the theme returns for the finale and resolves on the logo.
    python3 audio/make_music.py  ->  assets/audio/music.wav
"""
import wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 47.5
N = int(DUR * SR)
rng = np.random.default_rng(21)
CH = 2.5  # seconds per chord
T0 = 0.3


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, f, o=2):
    return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x, axis=0)


def hp(x, f, o=2):
    return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x, axis=0)


def place(buf, t, sig):
    i = int(round(t * SR))
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


def piano(m, dur, vel=0.5):
    n = int((dur + 2.5) * SR)
    t = np.arange(n) / SR
    f = hz(m)
    B = 0.00035
    s = np.zeros(n)
    bright = 0.6 + 0.6 * vel
    for k in range(1, 10):
        fk = f * k * np.sqrt(1 + B * k * k)
        if fk > 12000:
            break
        amp = (1 / k ** 1.25) * (bright ** (k - 1))
        dec = 0.9 + 0.45 * k + f / 900
        s += amp * np.sin(2 * np.pi * fk * t + k * 0.7) * np.exp(-t * dec)
    s *= np.clip(t / 0.003, 0, 1)
    rel = np.clip((dur + 0.25 - t) / 0.35, 0, 1) ** 2  # damper
    s *= rel  # note-off
    hammer = lp(rng.standard_normal(int(0.02 * SR)), 2500) * np.linspace(1, 0, int(0.02 * SR)) * 0.08
    s[: len(hammer)] += hammer
    return s * vel * 0.32


def strings(ms, dur, gain):
    n = int((dur + 1.6) * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for m in ms:
        for d, side in [(-6, 0), (-2, 1), (3, 0), (7, 1)]:
            f = hz(m) * 2 ** (d / 1200) * (1 + 0.0025 * np.sin(2 * np.pi * (5.1 + d * 0.05) * t))
            ph = 2 * np.pi * np.cumsum(f) / SR + (m + d) * 0.3
            saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
            out[:, side] += saw
    env = np.clip(t / 1.1, 0, 1) ** 1.5 * np.clip((dur + 1.4 - t) / 1.4, 0, 1)
    out *= env[:, None]
    out = lp(out, 1900, 2)
    return out * gain * 0.018


PROG = [  # (bass, chord tones, melody pool)
    (38, [62, 66, 69], [78, 81]),      # D
    (37, [61, 64, 69], [76, 73]),      # A/C#
    (35, [62, 66, 71], [74, 78]),      # Bm
    (31, [62, 67, 71], [74, 71]),      # G
]
END_PROG = [(40, [64, 67, 71], [79, 76]), (33, [61, 64, 69], [76, 73]), (38, [62, 66, 69, 74], [78])]  # Em, A, D

nchords = int(np.ceil((DUR - T0) / CH))
seq = [PROG[k % 4] for k in range(nchords)]
# cadence: chords landing on the logo (~44.8 s)
k_end = int((44.8 - T0) // CH)
seq[k_end - 2], seq[k_end - 1], seq[k_end] = END_PROG
seq = seq[: k_end + 1]


def section_gain(t):
    """strings dynamics over the film"""
    pts = [(0, 0), (8.5, 0), (10.5, 0.55), (25.5, 0.6), (28.5, 1.0), (31, 0.85), (35.3, 0.55), (39.6, 0.8), (44.5, 1.0), (47.5, 0.8)]
    xs, ys = zip(*pts)
    return float(np.interp(t, xs, ys))


pno = np.zeros((N + 3 * SR, 2))
strg = np.zeros((N + 3 * SR, 2))
pulse = np.zeros(N + 3 * SR)
fx = np.zeros((N + 3 * SR, 2))

for k, (bass, tones, mel) in enumerate(seq):
    t = T0 + k * CH
    last = k == len(seq) - 1
    dur = CH if not last else 3.2
    # left hand
    for oct_ in (0, 12):
        s = piano(bass + oct_, dur, 0.42 if oct_ else 0.5)
        place(pno, t, np.stack([s * 1.05, s * 0.95], 1))
    # right hand broken chord (eighths in 3 + 3 + 2 feel)
    arp = [tones[0], tones[1], tones[2], tones[1], tones[2] + 12 if len(tones) < 4 else tones[3], tones[2]]
    steps = 6 if not last else 4
    busy = 31.0 <= t < 35.3
    for i in range(steps):
        tt = t + i * CH / 6
        v = 0.30 if t < 9 else 0.26
        if busy:
            v = 0.32
        s = piano(arp[i % len(arp)], CH / 3, v)
        pan = -0.25 + 0.1 * (i % 3)
        place(pno, tt, np.stack([s * (1 - pan), s * (1 + pan)], 1))
    # melody (from inside the chalet on)
    if t >= 4.5 or last:
        top = mel[k % len(mel)] if not last else 78
        s = piano(top, CH * (0.9 if not busy else 0.45), 0.55)
        place(pno, t + 0.02, np.stack([s * 0.95, s * 1.05], 1))
        if busy:
            s2 = piano(mel[(k + 1) % len(mel)], CH * 0.45, 0.45)
            place(pno, t + CH / 2, np.stack([s2, s2], 1))
        elif 26 <= t < 31:  # the view: an answering phrase an octave up
            s2 = piano(tones[2] + 12, CH * 0.6, 0.35)
            place(pno, t + CH * 0.5, np.stack([s2 * 1.1, s2 * 0.9], 1))
    # strings
    g = section_gain(t + CH / 2)
    if g > 0:
        place(strg, t, strings([bass + 12] + tones + ([tones[1] + 12] if t >= 26 else []), dur, g))

# soft heartbeat pulse under the montage and the finale
for t in np.arange(31.0, 35.2, 60 / 72):
    nn = int(0.5 * SR)
    tt = np.arange(nn) / SR
    s = np.sin(2 * np.pi * np.cumsum(42 + 40 * np.exp(-tt * 20)) / SR) * np.exp(-tt * 7)
    place(pulse, t, s * 0.35)
for t in np.arange(39.6, 44.6, 60 / 72 * 2):
    nn = int(0.5 * SR)
    tt = np.arange(nn) / SR
    s = np.sin(2 * np.pi * np.cumsum(42 + 40 * np.exp(-tt * 20)) / SR) * np.exp(-tt * 7)
    place(pulse, t, s * 0.25)


def swell(t_end, d, gain):
    nn = int(d * SR)
    tt = np.arange(nn) / SR
    s = lp(hp(rng.standard_normal((nn, 2)), 2500), 6000) * ((tt / d) ** 3)[:, None] * gain
    s[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))[:, None]
    place(fx, t_end - d, s)


swell(26.2, 2.2, 0.03)
swell(39.6, 1.8, 0.025)

# ---------- hall reverb ----------
irn = int(3.2 * SR)
it = np.arange(irn) / SR
ir = rng.standard_normal((irn, 2)) * np.exp(-it * 2.1)[:, None]
ir = lp(ir, 5500)
ir[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))[:, None]
ir /= np.sqrt(np.sum(ir ** 2))


def verb(x, wet):
    y = np.stack([fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return x + y * wet


mix = verb(pno, 0.55) + verb(strg, 0.7) + np.stack([pulse, pulse], 1) + verb(fx, 0.6)
mix = mix[:N]
mix = hp(mix, 30)
fi = int(0.3 * SR)
mix[:fi] *= np.linspace(0, 1, fi)[:, None]
fo = int(2.0 * SR)
mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
mix /= np.max(np.abs(mix))
mix = np.tanh(mix * 1.3) / np.tanh(1.3) * 0.9

pcm = (mix * 32767).astype("<i2")
with wave.open("assets/audio/music.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote assets/audio/music.wav", N / SR, "s")
