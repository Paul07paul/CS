"""Assemble the French voice-over track from the per-line Kokoro renders.
    python3 audio/make_voice.py  ->  assets/audio/voice.wav  (lines in assets/audio/vo/)"""
import json
import wave
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly, fftconvolve

SR = 48000
DUR = 99.0
j = json.load(open("audio/voiceover.json"))
track = np.zeros(int(DUR * SR) + SR)
for i, (t, _) in enumerate(j["lines"]):
    x, sr = sf.read(f"assets/audio/vo/l{i:02d}.wav", dtype="float64")
    if x.ndim > 1:
        x = x.mean(1)
    if sr != SR:
        g = np.gcd(sr, SR)
        x = resample_poly(x, SR // g, sr // g)
    x = x / (np.max(np.abs(x)) + 1e-9)
    f = int(0.01 * SR)
    x[:f] *= np.linspace(0, 1, f)
    x[-f:] *= np.linspace(1, 0, f)
    i0 = int(t * SR)
    track[i0 : i0 + len(x)] += x[: len(track) - i0]
track = track[: int(DUR * SR)]
# gentle voice polish: high-pass rumble, soften harsh top, light compression, small room
track = sosfilt(butter(2, 90, "high", fs=SR, output="sos"), track)
track = sosfilt(butter(2, 9000, "low", fs=SR, output="sos"), track)
track = np.tanh(track * 1.6) / np.tanh(1.6)
rng = np.random.default_rng(3)
irn = int(0.6 * SR)
ir = rng.standard_normal(irn) * np.exp(-np.arange(irn) / SR * 9)
ir = sosfilt(butter(2, 4000, "low", fs=SR, output="sos"), ir)
ir /= np.sqrt(np.sum(ir ** 2))
wet = fftconvolve(track, ir)[: len(track)]
track = track + wet * 0.08
track = track / np.max(np.abs(track)) * 0.85
st = np.stack([track, track], 1)
pcm = (st * 32767).astype("<i2")
with wave.open("assets/audio/voice.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote assets/audio/voice.wav")
