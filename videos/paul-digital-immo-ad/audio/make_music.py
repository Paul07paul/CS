"""Synthesize the music bed for the Paul Digital ad (deterministic, royalty-free).

120 BPM, A minor / C major (Am - F - C - G). Bars start at -0.5 s so that the
drop lands on 5.5 s (villa) and the second section on 21.5 s; the logo lands
on the bar at 33.5 s.
    python3 audio/make_music.py  ->  assets/audio/music.wav
"""
import wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 36.5
N = int(DUR * SR)
BPM = 120
BEAT = 60 / BPM
BAR = 4 * BEAT
OFF = -0.5  # time of bar 0
rng = np.random.default_rng(11)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x, axis=0)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x, axis=0)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x, axis=0)


def saw(f, n, phase=0.0):
    t = np.arange(n) / SR
    return 2 * ((f * t + phase) % 1.0) - 1


def adsr(n, a, d, s, r):
    e = np.ones(n) * s
    A, D, R = int(a * SR), int(d * SR), int(r * SR)
    A = min(A, n)
    e[:A] = np.linspace(0, 1, A)
    D = min(D, n - A)
    e[A : A + D] = np.linspace(1, s, D)
    if R > 0 and R < n:
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


# ---------- harmony ----------
PROG = [  # (pad voicing midi, bass midi)
    ([57, 60, 64, 69], 33),  # Am
    ([53, 57, 60, 65], 29),  # F
    ([55, 60, 64, 67], 36),  # C/G
    ([55, 59, 62, 67], 31),  # G
]
ARP_STEPS = [0, 1, 2, 3, 2, 1, 3, 2]  # index into chord tones (+12)


def bar_time(k):
    return OFF + k * BAR


NBARS = int(np.ceil((DUR - OFF) / BAR)) + 1
DROP, SEC_B, LOGO = 5.5, 21.5, 33.5

pad = np.zeros((N, 2))
arp = np.zeros((N, 2))
bass = np.zeros(N)
kick = np.zeros(N)
clap = np.zeros(N)
hats = np.zeros((N, 2))
lead = np.zeros((N, 2))
fx = np.zeros((N, 2))

for k in range(NBARS):
    t0 = bar_time(k)
    if t0 >= DUR:
        break
    chord, root = PROG[k % 4]
    last = t0 >= LOGO - 0.01
    # --- pad: detuned saws, each bar
    n = int((BAR + 0.6) * SR) if not last else int((DUR - t0 + 0.1) * SR)
    voice = np.zeros((n, 2))
    for m in chord if not last else [48, 55, 60, 64, 67, 72]:  # final: open C major
        for d, side in [(-9, 0), (-3, 1), (4, 0), (10, 1)]:
            voice[:, side] += saw(hz(m) * 2 ** (d / 1200), n, phase=(m * 0.37 + d * 0.11) % 1)
    env = adsr(n, 0.25, 0.4, 0.85, 0.6 if not last else 2.2)
    voice *= env[:, None] * 0.06
    pad_cut = 900 if t0 < DROP - 0.01 else 2200
    if t0 < DROP - 0.01:
        pad_cut = 500 + 400 * max(0, k)
    voice = lp(voice, pad_cut)
    place(pad, t0, voice)
    # --- bass (from the drop)
    if DROP - 0.01 <= t0 < LOGO - 0.01:
        for e in range(8):
            nn = int(BEAT / 2 * SR * 0.9)
            f = hz(root + (12 if e in (3, 7) else 0))
            tt = np.arange(nn) / SR
            s = np.sin(2 * np.pi * f * tt) + 0.35 * saw(f, nn)
            s = lp(s, 380) * adsr(nn, 0.005, 0.12, 0.7, 0.04) * 0.32
            place(bass, t0 + e * BEAT / 2, s)
    if last:
        nn = int(2.8 * SR)
        tt = np.arange(nn) / SR
        s = np.sin(2 * np.pi * hz(36) * tt) * np.exp(-tt * 1.3) * 0.5
        place(bass, t0, s)
    # --- arp plucks (16ths), filtered in the intro
    if t0 < LOGO - 0.01:
        tones = [m + 12 for m in chord]
        for s16 in range(16):
            m = tones[ARP_STEPS[s16 % 8]] + (12 if (s16 // 8) % 2 and t0 >= SEC_B - 0.01 else 0)
            nn = int(0.22 * SR)
            tt = np.arange(nn) / SR
            f = hz(m)
            s = saw(f, nn) * 0.6 + np.sin(2 * np.pi * f * tt)
            s *= np.exp(-tt * 16) * 0.10
            tpos = t0 + s16 * BEAT / 4
            cut = 1200 if tpos < DROP else 3600
            if tpos < DROP:
                cut = 700 + 600 * (tpos / DROP) ** 2
            s = lp(s, cut)
            pan = 0.35 * np.sin(s16 * 1.3)
            place(arp, tpos, np.stack([s * (1 - pan), s * (1 + pan)], 1))
    # --- drums
    if DROP - 0.01 <= t0 < LOGO - 0.01:
        for b in range(4):
            tb = t0 + b * BEAT
            nn = int(0.45 * SR)
            tt = np.arange(nn) / SR
            f = 46 + 110 * np.exp(-tt * 28)
            s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7.5)
            s[:240] += rng.standard_normal(240) * np.linspace(0.08, 0, 240)
            place(kick, tb, s * 0.85)
            if b in (1, 3):
                nn = int(0.35 * SR)
                tt = np.arange(nn) / SR
                burst = rng.standard_normal(nn)
                envc = sum(np.exp(-np.clip(tt - o, 0, None) * 60) * (tt >= o) for o in (0, 0.011, 0.023)) / 3
                envc += np.exp(-tt * 14) * 0.5
                place(clap, tb, bp(burst, 900, 3200) * envc * 0.42)
            for h in (0.5,):
                nn = int(0.09 * SR)
                tt = np.arange(nn) / SR
                open_ = t0 >= SEC_B - 0.01
                s = lp(hp(rng.standard_normal(nn), 7000), 12000) * np.exp(-tt * (28 if open_ else 55)) * 0.09
                pan = 0.3 if b % 2 else -0.3
                place(hats, tb + h * BEAT, np.stack([s * (1 - pan), s * (1 + pan)], 1))
            # quiet 16th shaker
            for q in (0.25, 0.75):
                nn = int(0.05 * SR)
                tt = np.arange(nn) / SR
                s = hp(rng.standard_normal(nn), 9000) * np.exp(-tt * 90) * 0.035
                place(hats, tb + q * BEAT, np.stack([s, s], 1))
    elif 1.5 <= t0 < DROP:  # intro: soft hats only
        for b in range(4):
            nn = int(0.06 * SR)
            tt = np.arange(nn) / SR
            s = hp(rng.standard_normal(nn), 8000) * np.exp(-tt * 70) * 0.07
            place(hats, t0 + (b + 0.5) * BEAT, np.stack([s, s], 1))

# --- lead melody in section B (bell-ish), one phrase per 4 bars
MEL = [(76, 0, 1.5), (72, 1.5, 0.5), (74, 2, 1), (76, 3, 1),  # Am
       (77, 4, 1.5), (76, 5.5, 0.5), (72, 6, 2),               # F
       (79, 8, 1.5), (76, 9.5, 0.5), (72, 10, 2),              # C
       (74, 12, 1), (71, 13, 1), (74, 14, 1), (79, 15, 1)]     # G
for rep in range(3):
    base = SEC_B + rep * 4 * BAR
    for m, st, ln in MEL:
        tpos = base + st * BEAT
        if tpos >= LOGO - 0.01:
            break
        nn = int((ln * BEAT + 0.6) * SR)
        tt = np.arange(nn) / SR
        f = hz(m) * (1 + 0.003 * np.sin(2 * np.pi * 5.5 * tt) * np.clip(tt / 0.3, 0, 1))
        ph = 2 * np.pi * np.cumsum(f) / SR
        s = (np.sin(ph) + 0.3 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)) * adsr(nn, 0.01, 0.3, 0.55, 0.5) * 0.085
        place(lead, tpos, np.stack([s * 0.9, s * 1.1], 1))

# --- risers / impacts
def riser(t_end, d, gain):
    nn = int(d * SR)
    tt = np.arange(nn) / SR
    noise = rng.standard_normal(nn)
    out = np.zeros(nn)
    seg = nn // 24
    for i in range(24):  # stepped band sweep up
        a, b = i * seg, (i + 1) * seg if i < 23 else nn
        fc = 400 * (12 ** (i / 23))
        out[a:b] = bp(noise[a:b], fc * 0.7, min(fc * 1.6, 20000))
    out *= (tt / d) ** 2.2 * gain
    place(fx, t_end - d, np.stack([out, out], 1))


riser(DROP, 1.6, 0.16)
riser(SEC_B, 1.0, 0.10)
riser(LOGO, 1.5, 0.13)
nn = int(3.0 * SR)
tt = np.arange(nn) / SR
imp = np.sin(2 * np.pi * np.cumsum(30 + 50 * np.exp(-tt * 5)) / SR) * np.exp(-tt * 1.6) * 0.6
place(fx, DROP, np.stack([imp, imp], 1) * 0.6)
place(fx, LOGO, np.stack([imp, imp], 1))

# ---------- sidechain ----------
duck = np.ones(N)
for k in range(NBARS):
    for b in range(4):
        tb = bar_time(k) + b * BEAT
        if DROP - 0.01 <= tb < LOGO - 0.01:
            i = int(tb * SR)
            nn = int(0.28 * SR)
            j = min(N, i + nn)
            duck[i:j] = np.minimum(duck[i:j], 0.45 + 0.55 * (np.linspace(0, 1, nn)[: j - i] ** 1.5))

# ---------- reverb ----------
irn = int(2.2 * SR)
it = np.arange(irn) / SR
ir = np.stack([rng.standard_normal(irn), rng.standard_normal(irn)], 1) * np.exp(-it * 3.2)[:, None]
ir = lp(ir, 6000)
ir /= np.sqrt(np.sum(ir ** 2))


def verb(x, wet):
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    y = np.stack([fftconvolve(x[:, c], ir[:, c])[:N] for c in range(2)], 1)
    return x + y * wet


mix = np.zeros((N, 2))
mix += verb(pad, 0.5) * duck[:, None]
mix += verb(arp, 0.6) * (0.6 + 0.4 * duck[:, None])
mix += np.stack([bass, bass], 1) * duck[:, None]
mix += np.stack([kick, kick], 1)
mix += verb(clap, 0.7)
mix += verb(hats, 0.3)
mix += verb(lead, 0.8)
mix += verb(fx, 0.5)
mix = hp(mix, 28)

# master: fade-in, end fade, soft clip
fi = int(0.4 * SR)
mix[:fi] *= np.linspace(0, 1, fi)[:, None]
fo = int(1.5 * SR)
mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
mix /= np.max(np.abs(mix))
mix = np.tanh(mix * 1.6) / np.tanh(1.6) * 0.9

pcm = (mix * 32767).astype("<i2")
with wave.open("assets/audio/music.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote assets/audio/music.wav", N / SR, "s")
