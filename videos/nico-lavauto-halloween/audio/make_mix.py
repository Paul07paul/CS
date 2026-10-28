"""Soundtrack for the Nico Lav'Auto Halloween reel.

Voice: Gemini 3.1 Flash TTS fr-FR (FLORA): lines 1-3 'Charon' (horror), 4-8 'Puck' (upbeat) -> assets/audio/vo/l01..l08.wav
Music: ElevenLabs Music -> assets/audio/music-horror.mp3 (0 -> s4), assets/audio/music-dyn.mp3 (s4 -> end)
SFX:   ElevenLabs SFX -> assets/audio/sfx/*.mp3 (door, whispers, creak, stinger, banish) + synthesized whooshes/sparkles.
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
S = T["scenes"]
rng = np.random.default_rng(13)


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


def lp(x, f, o=2):
    return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x, axis=0)


def hp(x, f, o=2):
    return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x, axis=0)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x, axis=0)


def place(buf, t, sig, gain=1.0):
    i = int(round(t * SR))
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain


def st(s, pan=0.0):
    return np.stack([s * (1 - pan), s * (1 + pan)], 1)


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)


def norm(x, db):
    m = np.abs(x).max(1) > 1e-3
    return x * 10 ** ((db - rms_db(x[m] if m.any() else x)) / 20)


def fade(x, a, b):
    x = x.copy()
    na, nb = int(a * SR), int(b * SR)
    if na:
        x[:na] *= np.linspace(0, 1, na)[:, None]
    if nb:
        x[-nb:] *= np.linspace(1, 0, nb)[:, None] ** 2
    return x


# ---------------- voice ----------------
voice = np.zeros((N + 4 * SR, 2))
active = np.zeros(N + 4 * SR)
for k, (t0, _txt) in enumerate(T["vo"]):
    v = hp(load(f"assets/audio/vo/p{k + 1:02d}.wav"), 70)
    lvl = np.abs(v).max(1)
    on = np.nonzero(lvl > 0.02)[0]
    v = v[max(0, on[0] - int(0.03 * SR)):]  # trim leading silence so t0 = first syllable
    on = on - on[0]
    v = norm(v, -17.0)
    if k < 3:  # horror voice: a touch of dark room reverb
        irn = int(0.9 * SR)
        it = np.arange(irn) / SR
        ir = lp(rng.standard_normal((irn, 2)) * np.exp(-it * 4.5)[:, None], 3500)
        ir /= np.sqrt(np.sum(ir ** 2))
        wet = np.stack([fftconvolve(v[:, c], ir[:, c]) for c in range(2)], 1)
        v = np.vstack([v, np.zeros((len(wet) - len(v), 2))]) + wet * 0.22
    place(voice, t0, v)
    place(active, t0, np.ones(on[-1] + int(0.1 * SR)))
    print(f"l{k + 1:02d} at {t0:5.2f}s  speech {on[-1] / SR:4.2f}s  ends {t0 + on[-1] / SR:5.2f}s")
voice = voice[:N]

# duck envelope (smooth 120 ms attack / 400 ms release)
act = np.minimum(active[:N], 1)
env = np.zeros(N)
g = 0.0
for i in range(0, N, 48):
    tgt = act[i]
    c = 1 - np.exp(-48 / ((0.12 if tgt > g else 0.4) * SR))
    g += (tgt - g) * c
    env[i: i + 48] = g

# ---------------- music ----------------
music = np.zeros((N, 2))
t_sw = S["s4"]
mh = load("assets/audio/music-horror.mp3")
# ambient bed, no pulse: extend 16 s -> ~23 s with a long crossfade into a second pass
a, b, xf = int(12.0 * SR), int(3.0 * SR), int(2.0 * SR)
w = np.linspace(0, 1, xf)[:, None]
mh = np.vstack([mh[:a - xf], mh[a - xf:a] * (1 - w) + mh[b:b + xf] * w, mh[b + xf:]])
mh = norm(mh[: int((t_sw + 0.3) * SR)], -24.0)
mh = fade(mh, 0.8, 0.35)
place(music, 0, mh)
md = load("assets/audio/music-dyn.mp3")
# extend ~30 s -> ~40 s: jump back 24 beats (143.5 BPM) at a beat, 40 ms crossfade
import librosa
_y = librosa.to_mono(md.T.astype(np.float32))
_, _bt = librosa.beat.beat_track(y=_y, sr=SR, units="samples")
i = int(np.argmin(np.abs(_bt - 18.0 * SR)))
j0, j1 = _bt[i], _bt[i - 24]  # play to j0, then continue from j1 (earlier)
xf = int(0.04 * SR)
w = np.linspace(0, 1, xf)[:, None]
md = np.vstack([md[:j0], md[j0:j0 + xf] * (1 - w) + md[j1:j1 + xf] * w, md[j1 + xf:]])
md = norm(md[: N - int(t_sw * SR)], -19.5)
md = fade(md, 0.02, 2.5)
place(music, t_sw, md)
duck = 10 ** (-11 * env / 20)
music *= duck[:, None]

# ---------------- sfx ----------------
fx = np.zeros((N + 4 * SR, 2))


def sfx(name, t, db, a=0.05, b=0.4):
    x = fade(norm(load(f"assets/audio/sfx/{name}.mp3"), db), a, b)
    place(fx, t, x)


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


def chime(t, f, gain=0.04, pan=0.0):
    x = np.arange(int(1.2 * SR)) / SR
    s = (np.sin(2 * np.pi * f * x) + 0.3 * np.sin(4 * np.pi * f * x)) * np.exp(-x * 4) * np.clip(x / 0.004, 0, 1)
    place(fx, t, st(s * gain, pan))


def boom(t, gain=0.3):
    n = int(1.6 * SR)
    x = np.arange(n) / SR
    s = np.sin(2 * np.pi * np.cumsum(42 + 70 * np.exp(-x * 10)) / SR) * np.clip(x / 0.005, 0, 1) * np.exp(-x * 3)
    s += lp(rng.standard_normal(n), 1200) * np.exp(-x * 12) * 0.4
    place(fx, t, st(s * gain))


def heartbeat(t, gain=0.25):
    for dt in (0, 0.28):
        n = int(0.25 * SR)
        x = np.arange(n) / SR
        s = np.sin(2 * np.pi * 50 * x) * np.exp(-x * 22) * np.clip(x / 0.004, 0, 1)
        place(fx, t + dt, st(s * gain * (1 if dt == 0 else 0.7)))


# horror part — kept under the voice
sfx("door", 0.05, -27, 0.02, 0.6)
sfx("whispers", 2.4, -31, 0.4, 0.8)
for t in (3.6, 5.0):
    heartbeat(t, 0.22)
for t in T["cuts"]:  # three cuts in the dirt montage
    boom(t, 0.18)
    whoosh(t + 0.05, 0.35, 3200, 0.07)
sfx("whispers", 12.4, -31, 0.5, 0.8)
sfx("creak", S["s3"] - 0.2, -27, 0.05, 0.6)
heartbeat(T["scare"] - 1.6, 0.22)
heartbeat(T["scare"] - 0.85, 0.28)
sfx("stinger", T["scare"] - 0.02, -21, 0.0, 0.5)
# banish + hero entrance
sfx("banish", S["s4"] - 0.1, -22, 0.0, 0.4)
boom(S["s4"], 0.3)
for k, f in enumerate([1568, 1976, 2349, 2637]):
    chime(S["s4"] + 0.25 + k * 0.07, f, 0.035, (k - 1.5) * 0.25)
whoosh(S["s4"] + 2.75, 0.4, 3000, 0.1)
# before/after sweeps
for k, t in enumerate(T["pairs"]):
    if k:
        whoosh(t + 0.1, 0.35, 3000, 0.08, 0.5, -0.5)
    whoosh(t + 0.6 + 0.45, 0.7, 4200, 0.12, -0.7, 0.7)
    for j, f in enumerate([2093, 2637, 3136]):
        chime(t + 1.15 + j * 0.12, f, 0.03, (j - 1) * 0.4)
# nightmare -> showroom
boom(S["s6"], 0.2)
whoosh(S["s6"] + 0.35, 0.5, 3000, 0.1)
boom(T["show"], 0.22)
for k, f in enumerate([1568, 2093, 2637, 3136]):
    chime(T["show"] + 0.05 + k * 0.06, f, 0.035, (k - 1.5) * 0.3)
# CTA
boom(S["s7"] + 1.5, 0.12)
whoosh(T["vo"][7][0] + 1.4, 0.5, 2800, 0.08, -0.6, 0.2)
whoosh(T["vo"][7][0] + 5.9, 0.5, 2800, 0.08, 0.6, -0.2)

sfx_bus = fx[:N]
sfx_bus *= (1 - 0.45 * env)[:, None]  # sfx sit back while the voice speaks

# ---------------- master ----------------
mix = voice + music + sfx_bus
mix = hp(mix, 25)
peak = np.max(np.abs(mix))
if peak > 0.97:
    mix = mix / peak * 0.97
mix = np.tanh(mix * 1.15) / np.tanh(1.15)
pcm = (np.clip(mix, -1, 1) * 32767).astype("<i2")
with wave.open("assets/audio/mix.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote assets/audio/mix.wav", DUR, "s")
