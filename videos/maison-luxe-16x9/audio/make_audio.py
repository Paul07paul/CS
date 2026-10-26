"""Soundtrack for the Paul Digital presentation (16:9, ~65 s).

Inputs  (assets/audio/src):
  vo.mp3     voice-over — ElevenLabs v4 via FLORA, one take of the full script
  music.mp3  music bed  — ElevenLabs Music via FLORA
Outputs (assets/audio):
  vo.wav     voice, cleaned and levelled, placed at timing.json vo_offset
  music.wav  music bed, faded, kept well under the voice (sidechain-style duck)
  sfx.wav    synthesized, soft and "satisfying" UI sounds on the scene cues of timing.json

    python3 audio/make_audio.py
"""
import json
import os
import subprocess
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(ROOT, "timing.json")))
DUR = T["duration"]
N = int(DUR * SR)
rng = np.random.default_rng(11)


def path(*p):
    return os.path.join(ROOT, *p)


def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


def save(p, x):
    x = np.clip(x, -1, 1)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s16le", p], input=x.astype(np.float32).tobytes(), check=True)


def filt(x, kind, f, o=2):
    return sosfilt(butter(o, f, kind, fs=SR, output="sos"), x, axis=0)


def place(buf, t, sig, gain=1.0):
    i = int(round(t * SR))
    if i >= len(buf) or i + len(sig) <= 0:
        return
    if i < 0:
        sig = sig[-i:]
        i = 0
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain


def st(s, pan=0.0):
    return np.stack([s * (1 - pan), s * (1 + pan)], 1)


def env(n, a, d, curve=4.0):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) * curve / max(d, 1e-4))
    return e


def lufs_ish(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)


# a short, soft room so every synth sits in the same space
IR_N = int(0.9 * SR)
ir = rng.standard_normal((IR_N, 2)) * np.exp(-np.arange(IR_N) / SR * 7.0)[:, None]
ir = filt(ir, "low", 5000)
ir /= np.abs(ir).sum(0) * 0.25


def verb(x, wet=0.25):
    w = np.stack([fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return x * (1 - wet) + w * wet


# ---------------- sound design ----------------
def whoosh(dur=0.55, up=False, gain=0.5):
    n = int(dur * SR)
    noise = rng.standard_normal(n)
    t = np.linspace(0, 1, n)
    shape = np.sin(np.pi * t) ** 2
    out = np.zeros(n)
    # sweep a band-pass through the noise in short blocks
    blk = 512
    for k in range(0, n, blk):
        u = k / n
        fc = 300 + (2600 if up else 2200) * (u if up else (1 - u) * 0.6 + 0.4 * u)
        seg = noise[k:k + blk]
        sos = butter(2, [max(80, fc * 0.6), min(16000, fc * 1.6)], "band", fs=SR, output="sos")
        out[k:k + blk] = sosfilt(sos, seg)
    out *= shape
    out /= np.abs(out).max() + 1e-9
    s = np.stack([out * np.linspace(1.2, 0.6, n), out * np.linspace(0.6, 1.2, n)], 1)
    return verb(s, 0.2) * gain


def pop(gain=0.32, f0=900):
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    f = f0 * np.exp(-t * 22) + 260
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * env(n, 0.002, 0.07, 3.5)
    s += 0.25 * np.sin(2 * ph) * env(n, 0.001, 0.03, 4)
    return verb(st(s), 0.18) * gain


def tick(gain=0.18):
    n = int(0.05 * SR)
    s = rng.standard_normal(n) * env(n, 0.0005, 0.012, 5)
    s = filt(s, "high", 2500)
    return st(s) * gain


def click(gain=0.4):
    a = tick(0.5)
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    b = np.sin(2 * np.pi * 1800 * t) * env(n, 0.0005, 0.02, 5) * 0.4
    out = np.zeros((n, 2))
    out[: len(a)] += a
    out += st(b)
    out[int(0.06 * SR):] += st(rng.standard_normal(n - int(0.06 * SR)) * env(n - int(0.06 * SR), 0.0005, 0.01, 5) * 0.2)
    return out * gain


def card(gain=0.3):
    # soft glassy "fwip" + low thump
    w = whoosh(0.28, up=True, gain=0.6)
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    th = np.sin(2 * np.pi * (120 * np.exp(-t * 10) + 60) * t) * env(n, 0.003, 0.1, 4) * 0.6
    out = np.zeros((max(len(w), n), 2))
    out[: len(w)] += w
    out[:n] += st(th)
    return out * gain


def glass(gain=0.3, f=1567.98):
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * m * t) * a for m, a in [(1, 1), (2.76, 0.35), (5.4, 0.12)]) * env(n, 0.002, 0.6, 5)
    return verb(st(s, 0.15), 0.4) * gain


def chime(gain=0.28):
    out = np.zeros((int(1.8 * SR), 2))
    for k, f in enumerate([1046.5, 1318.5, 1568.0, 2093.0]):
        place(out, k * 0.07, glass(1.0, f) * 0.5)
    return out * gain


def ding(gain=0.3):
    return glass(gain, 1760.0) + np.vstack([glass(gain * 0.6, 2637.0)[int(0.05 * SR):], np.zeros((int(0.05 * SR), 2))])


def notif(gain=0.3):
    out = np.zeros((int(1.4 * SR), 2))
    place(out, 0, glass(1, 1318.5))
    place(out, 0.11, glass(1, 1975.5))
    return out * gain


def sub_impact(gain=0.55, f=55, dur=0.9):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * (f + 70 * np.exp(-t * 18)) * t) * env(n, 0.004, 0.45, 3.5)
    nz = filt(rng.standard_normal(n), "low", 1800) * env(n, 0.001, 0.08, 5) * 0.4
    return verb(st(s + nz), 0.25) * gain


def snap(gain=0.4):
    n = int(0.12 * SR)
    s = filt(rng.standard_normal(n), "band", [900, 5000]) * env(n, 0.0005, 0.03, 5)
    t = np.arange(n) / SR
    s += np.sin(2 * np.pi * 220 * t) * env(n, 0.001, 0.05, 4) * 0.6
    return verb(st(s), 0.2) * gain


def riser(dur=1.1, gain=0.22):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 200 * (8 ** (t / dur))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3
    nz = filt(rng.standard_normal(n), "high", 3000) * 0.5
    s = (s + nz) * (t / dur) ** 2
    return verb(st(s), 0.3) * gain


def swell(gain=0.22, dur=1.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * t + p) for f, p in [(220, 0), (277.2, 1), (329.6, 2), (440, 0.5)])
    s *= np.sin(np.pi * np.minimum(1, t / dur)) ** 2 * 0.25
    s = filt(s, "low", 2500)
    return verb(st(s), 0.45) * gain


def shimmer(gain=0.12, dur=1.0):
    n = int(dur * SR)
    out = np.zeros((n, 2))
    for k in range(10):
        f = 2000 + k * 380
        place(out, k * dur / 12, glass(1, f)[: int(0.4 * SR)] * 0.4)
    return verb(out, 0.4) * gain


def scan(gain=0.22, dur=0.9):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 600 + 2400 * t / dur
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15
    s += filt(rng.standard_normal(n), "band", [2000, 7000]) * 0.4
    s *= np.sin(np.pi * t / dur)
    pan = np.linspace(-0.8, 0.8, n)
    return verb(np.stack([s * (1 - pan), s * (1 + pan)], 1), 0.2) * gain


def wire(gain=0.12, dur=2.4, rate=14):
    # a cascade of tiny digital ticks while the wireframe draws itself
    out = np.zeros((int((dur + 0.2) * SR), 2))
    k = 0
    tt = 0.0
    while tt < dur:
        p = ((k * 37) % 11) / 11 * 1.2 - 0.6
        tk = tick(1.0)
        n = len(tk)
        tone = np.sin(2 * np.pi * (2400 + (k % 7) * 260) * np.arange(n) / SR) * env(n, 0.0005, 0.015, 5) * 0.4
        place(out, tt, (tk + st(tone)) * np.array([1 - p, 1 + p]))
        k += 1
        tt += 1.0 / rate * (0.7 + 0.6 * ((k * 13) % 5) / 5)
    return verb(out, 0.2) * gain


def suck(gain=0.35):
    w = whoosh(0.6, up=False, gain=1.0)
    return w[::-1].copy() * gain


def rise(gain=0.18):
    return riser(1.8, 1.0) * gain


def flash(gain=0.25):
    return verb(st(filt(rng.standard_normal(int(0.3 * SR)), "high", 4000) * env(int(0.3 * SR), 0.002, 0.15, 4)), 0.4) * gain


def sparkle(gain=0.1):
    return shimmer(1.0, 1.4) * gain


BANK = {
    "whoosh": lambda: whoosh(0.55, False, 0.42),
    "whoosh_in": lambda: whoosh(0.45, True, 0.3),
    "pop": lambda: pop(0.3, 700 + rng.integers(0, 500)),
    "tick": lambda: tick(0.25),
    "click": lambda: click(0.55),
    "card": lambda: card(0.3),
    "glass": lambda: glass(0.25),
    "chime": lambda: chime(0.35),
    "ding": lambda: ding(0.28),
    "notif": lambda: notif(0.35),
    "impact": lambda: sub_impact(0.45),
    "impact_big": lambda: sub_impact(0.7, 45, 1.6),
    "snap": lambda: snap(0.4),
    "riser": lambda: riser(1.1, 0.2),
    "swell": lambda: swell(0.22),
    "shimmer": lambda: shimmer(0.14),
    "scan": lambda: scan(0.26),
    "wire": lambda: wire(0.13, 2.4),
    "wire_short": lambda: wire(0.11, 0.55, 18),
    "suck": lambda: suck(0.3),
    "rise": lambda: rise(1.0),
    "flash": lambda: flash(0.2),
    "iris": lambda: whoosh(0.7, True, 0.35),
    "sparkle": lambda: sparkle(1.0),
}

sfx = np.zeros((N + SR * 2, 2))
for scene, cues in T["sfx"].items():
    t0, _, k = T["scenes"][scene]
    for name, dt in cues:
        place(sfx, t0 + dt * k, BANK[name]())
for name, t in T.get("global_sfx", []):
    place(sfx, t - 0.02, BANK[name]() * 0.8)
sfx = sfx[:N]

# ---------------- voice ----------------
voice = np.zeros((N, 2))
vo_src = path("assets/audio/src/vo-vindemiatrix.wav")
if os.path.exists(vo_src):
    v = load(vo_src)
    v = filt(v, "high", 70)
    # gentle presence lift and level to a speech target
    v = v + 0.25 * filt(v, "band", [2500, 6000])
    v *= 10 ** ((-17.0 - lufs_ish(v[np.abs(v).max(1) > 0.02])) / 20)
    place(voice, T["vo_offset"], v)
    voice = voice[:N]

# voice activity envelope (smoothed) for the duck
act = np.abs(voice).max(1)
win = int(0.25 * SR)
act = np.convolve(act > 0.015, np.ones(win) / win, mode="same")
act = np.convolve(act, np.ones(win) / win, mode="same")
act = np.clip(act * 1.6, 0, 1)

# ---------------- music ----------------
music = np.zeros((N, 2))
mu_src = path("assets/audio/src/music.mp3")
if not os.path.exists(mu_src):
    mu_src = path("assets/audio/src/music_synth.wav")
if os.path.exists(mu_src):
    m = load(mu_src)
    m = m[: N]
    m *= 10 ** ((-21.5 - lufs_ish(m)) / 20)
    music[: len(m)] = m
    # fades: in, and out under the final logo
    fi = int(0.6 * SR)
    music[:fi] *= np.linspace(0, 1, fi)[:, None]
    fo0 = int((DUR - 3.0) * SR)
    music[fo0:] *= np.linspace(1, 0, N - fo0)[:, None]
    # duck: voice present → music −9 dB, plus a mid carve so words stay clear
    duck = 10 ** (-10 * act / 20)
    mid = filt(music, "band", [300, 3500])
    music = music * duck[:, None] - mid * (0.35 * act)[:, None]

save(path("assets/audio/vo.wav"), voice)
save(path("assets/audio/music.wav"), music)
sfx *= min(1.0, 0.6 / (np.abs(sfx).max() + 1e-9))
save(path("assets/audio/sfx.wav"), sfx)
for name, x in [("vo", voice), ("music", music), ("sfx", sfx)]:
    print(f"{name:6s} peak {20*np.log10(np.abs(x).max()+1e-12):6.1f} dBFS  rms {lufs_ish(x):6.1f} dB")
