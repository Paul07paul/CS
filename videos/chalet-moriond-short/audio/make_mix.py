"""Full soundtrack for the short Courchevel Moriond cut (41 s).

Voice: Gemini 3.1 Flash TTS (fr-FR, voice "Sulafat") generated in FLORA, one file per line in
assets/audio/vo/l01..l08.wav.  Music: ElevenLabs Music (assets/audio/music.mp3), trimmed
so its drop lands on the salon reveal, ducked under the voice.  SFX: synthesized here.
    python3 audio/make_mix.py  ->  assets/audio/mix.wav
"""
import json
import subprocess
import wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
T = json.load(open("timing.json"))
DUR = T["duration"]
N = int(DUR * SR)
rng = np.random.default_rng(7)


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


def lp(x, f, o=2):
    return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x, axis=0)


def hp(x, f, o=2):
    return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x, axis=0)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x, axis=0)


def place(buf, t, sig):
    i = int(round(t * SR))
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


def st(s, pan=0.0):
    return np.stack([s * (1 - pan), s * (1 + pan)], 1)


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)


# ---------------- voice ----------------
voice = np.zeros((N + SR, 2))
active = np.zeros(N + SR)
for k, (t0, _txt) in enumerate(T["vo"]):
    v = load(f"assets/audio/vo/l{k + 1:02d}.wav")
    v = hp(v, 80)
    place(voice, t0, v)
    lvl = np.abs(v).max(1)
    on = np.nonzero(lvl > 0.02)[0]
    place(active, t0 + on[0] / SR, np.ones(on[-1] - on[0]))
voice = voice[:N]
voice *= 10 ** ((-17.0 - rms_db(voice[np.abs(voice).max(1) > 0.01])) / 20)  # speech RMS ~ -17 dBFS

# ---------------- music, ducked ----------------
m = load("assets/audio/music.mp3")[int(T["music_offset"] * SR):]
music = np.zeros((N, 2))
music[: min(N, len(m))] = m[:N]
music *= 10 ** ((-22.0 - rms_db(music[: int(30 * SR)])) / 20)
# duck envelope: -13 dB while the voice speaks, smooth 120 ms attack / 450 ms release
act = np.minimum(active[:N], 1)
env = np.zeros(N)
g = 0.0
a_att, a_rel = 1 - np.exp(-1 / (0.12 * SR)), 1 - np.exp(-1 / (0.45 * SR))
for i in range(0, N, 48):  # 1 ms control rate
    tgt = act[i]
    g += (tgt - g) * (1 - (1 - (a_att if tgt > g else a_rel)) ** 48)
    env[i : i + 48] = g
duck = 10 ** (-13 * env / 20)
music *= duck[:, None]
fo = int(2.4 * SR)
music[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 2
music[: int(0.25 * SR)] *= np.linspace(0, 1, int(0.25 * SR))[:, None]

# ---------------- sfx ----------------
fx = np.zeros((N + 3 * SR, 2))


def whoosh(t, d=0.6, top=2600, gain=0.2, p0=-0.6, p1=0.6):
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
    out *= np.where(p < 0.62, (p / 0.62) ** 2, ((1 - p) / 0.38) ** 1.5)
    out /= np.max(np.abs(out)) + 1e-9
    pan = np.linspace(p0, p1, n)
    place(fx, t - d * 0.62, np.stack([out * (1 - pan * 0.6), out * (1 + pan * 0.6)], 1) * gain)


def pop(t, gain=0.08, f0=760, f1=460, pan=0.0):
    x = np.arange(int(0.2 * SR)) / SR
    f = f1 + (f0 - f1) * np.exp(-x * 30)
    place(fx, t, st(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 20) * np.clip(x / 0.003, 0, 1) * gain, pan))


def tick(t, gain=0.03, f=1300, pan=0.0):
    x = np.arange(int(0.08 * SR)) / SR
    s = np.sin(2 * np.pi * f * x) * np.exp(-x * 55) + lp(rng.standard_normal(len(x)), 4000) * np.exp(-x * 120) * 0.3
    place(fx, t, st(s * np.clip(x / 0.002, 0, 1) * gain, pan))


def glass(t, f=1760, gain=0.05, pan=0.0):
    """glassy UI tap: two inharmonic partials, quick decay"""
    x = np.arange(int(0.9 * SR)) / SR
    s = np.sin(2 * np.pi * f * x) * np.exp(-x * 6) + 0.5 * np.sin(2 * np.pi * f * 2.76 * x) * np.exp(-x * 11)
    place(fx, t, st(s * np.clip(x / 0.002, 0, 1) * gain, pan))


def chime(t, f, gain=0.04, pan=0.0):
    x = np.arange(int(1.4 * SR)) / SR
    s = (np.sin(2 * np.pi * f * x) + 0.3 * np.sin(4 * np.pi * f * x)) * np.exp(-x * 3.5) * np.clip(x / 0.004, 0, 1)
    place(fx, t, st(s * gain, pan))


def bloom(t, gain=0.2):
    """soft low impact for camera pushes"""
    n = int(1.6 * SR)
    x = np.arange(n) / SR
    s = np.sin(2 * np.pi * np.cumsum(46 + 50 * np.exp(-x * 9)) / SR) * np.clip(x / 0.01, 0, 1) * np.exp(-x * 3.2)
    s += lp(rng.standard_normal(n), 900) * np.exp(-x * 14) * 0.35
    place(fx, t, st(s * gain))


def riser(t_end, d, gain=0.06):
    n = int(d * SR)
    x = np.arange(n) / SR
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    seg = n // 20
    for i in range(20):
        a, b = i * seg, (i + 1) * seg if i < 19 else n
        fc = 500 * (8 ** (i / 19))
        out[a:b] = bp(noise[a:b], fc * 0.7, min(fc * 1.4, 16000))
    out *= (x / d) ** 2.4 * gain / (np.max(np.abs(out)) + 1e-9)
    place(fx, t_end - d, st(out))


def shimmer(t, d=1.2, gain=0.035):
    """wireframe drawing: soft high sparkle cloud"""
    n = int(d * SR)
    x = np.arange(n) / SR
    s = bp(rng.standard_normal((n, 2)), 5000, 9000) * (np.sin(np.pi * x / d) ** 2)[:, None]
    place(fx, t, s / np.max(np.abs(s)) * gain)


def water(t, d, gain=0.04):
    n = int(d * SR)
    x = np.arange(n) / SR
    s = np.stack([bp(rng.standard_normal(n), 400, 2600) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.35 * x + c)) for c in range(2)], 1)
    s *= (np.clip(x / 0.8, 0, 1) * np.clip((d - x) / 0.8, 0, 1))[:, None]
    place(fx, t, s / np.max(np.abs(s)) * gain)


S = T["scenes"]
# shutter transitions (same sound every chapter change)
for t in T["shutters"]:
    whoosh(t, 0.8, 2600, 0.2, -0.7, 0.7)
    pop(t + 0.02, 0.04, 520, 330)
# 1 luxury title: soft and sparse
bloom(0.1, 0.08)
shimmer(0.2, 1.6, 0.012)
chime(0.95, 1318, 0.03)
chime(1.6, 1976, 0.025, 0.2)
chime(1.75, 2637, 0.018, -0.2)
# 2 balcony -> photo wall -> dive
for t in T["chips2"]:
    pop(t, 0.07, 780, 470)
whoosh(6.4, 1.6, 2200, 0.16, 0.6, -0.6)
riser(9.15, 1.2, 0.05)
whoosh(9.1, 0.7, 2600, 0.18, -0.5, 0.5)
bloom(9.2, 0.12)
# 3 suites / dortoir / bathrooms
for k in range(4):
    whoosh(9.5 + k * 0.08, 0.3, 3200, 0.05, -0.6 + 0.4 * k, -0.6 + 0.4 * k)
    tick(10.0 + k * 0.08, 0.03, 1700 + 120 * k, -0.45 + 0.3 * k)
pop(9.7, 0.08, 820, 500)
for k in range(4):
    whoosh(10.75 + k * 0.06, 0.32, 2800, 0.06, -0.5 + 0.33 * k, 0.5)
pop(10.9, 0.08, 860, 520)
for k in range(4):
    whoosh(11.8 + k * 0.09, 0.35, 3000, 0.06, 0.6, -0.2)
    pop(11.85 + k * 0.09, 0.05, 700 + 60 * k, 460)
glass(12.0, 2349, 0.03)
# 4 living spaces (music drop)
bloom(S["s4"], 0.22)
whoosh(15.45, 0.5, 3000, 0.08, -0.6, 0.2)
whoosh(15.95, 0.5, 3000, 0.08, 0.6, -0.2)
whoosh(17.45, 0.6, 2800, 0.1, 0.4, -0.4)
for k in range(14):
    tick(18.0 + 1.5 * (1 - (1 - (k + 1) / 14) ** 0.6), 0.03, 2000)
for k, f in enumerate([1568, 1976, 2349, 2637, 3136]):
    chime(19.6 + k * 0.09, f, 0.03, (k - 2) * 0.2)
# 5 pool + sauna
water(S["s5"], 5.0, 0.045)
for k in range(15):
    tick(22.0 + k * 0.045, 0.018, 1700 + 30 * k)
pop(23.2, 0.07)
for t in (22.4, 23.0, 23.6):
    glass(t, 1318, 0.025, 0.3)
whoosh(24.45, 0.6, 2800, 0.1, 0.7, -0.2)
pop(24.6, 0.07, 820, 500)
# 6 phone
bloom(S["s6"], 0.1)
for i, t in enumerate(T["chips6"]):
    pop(t, 0.07, 760 + 50 * i, 480, 0.4 * (1 if i % 2 else -1))
for t in T["notifs6"]:
    chime(t, 1760, 0.035); chime(t + 0.11, 2637, 0.03)
# 7 cta
for i in range(5):
    whoosh(S["s7"] + 0.4 + i * 0.22, 0.3, 3200, 0.05, -0.4, 0.4)
x = np.arange(int(0.08 * SR)) / SR
place(fx, T["click"], st((lp(rng.standard_normal(len(x)), 3000) * np.exp(-x * 90) + np.sin(2 * np.pi * 900 * x) * np.exp(-x * 60) * 0.5) * 0.09))
chime(T["click"] + 0.1, 2637, 0.04)
# 8 logo
bloom(S["s8"] + 0.1, 0.16)
for k, f in enumerate([1568, 2093, 2349, 2637, 3136]):
    chime(S["s8"] + 0.45 + k * 0.07, f, 0.045 * (1 - 0.12 * k), (k - 2) * 0.25)

irn = int(1.2 * SR)
it = np.arange(irn) / SR
ir = lp(rng.standard_normal((irn, 2)) * np.exp(-it * 2.8)[:, None], 5000)
ir /= np.sqrt(np.sum(ir ** 2))
dry = lp(fx[:N], 7000)
sfx = dry * 0.85 + np.stack([fftconvolve(dry[:, c], ir[:, c])[:N] for c in range(2)], 1) * 0.45
sfx *= 10 ** ((-29.0 - rms_db(sfx[np.abs(sfx).max(1) > 1e-3])) / 20)
sfx *= 1 - 0.35 * env[:, None]  # a touch softer under the voice

# ---------------- master ----------------
mix = voice + music + sfx
mix = hp(mix, 25)
peak = np.max(np.abs(mix))
mix = mix / max(peak, 1e-9) * 0.97 if peak > 0.97 else mix
mix = np.tanh(mix * 1.15) / np.tanh(1.15)
pcm = (np.clip(mix, -1, 1) * 32767).astype("<i2")
with wave.open("assets/audio/mix.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote assets/audio/mix.wav", DUR, "s")
