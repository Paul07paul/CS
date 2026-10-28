"""Trim leading/trailing silence and shorten long pauses in each voice line.
assets/audio/vo/lNN.wav -> assets/audio/vo/pNN.wav ; prints phrase onsets (s) for timing.json."""
import subprocess, wave, json
import numpy as np
SR = 48000
MAXGAP = {1: 0.42, 2: 0.42, 3: 0.42}
TEMPO = {1: 1.1, 2: 1.12, 3: 1.1}  # pitch-preserving speed-up (ffmpeg atempo); upbeat lines use 1.1  # horror lines keep slow, heavy pauses
out = {}
for k in range(1, 9):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"assets/audio/vo/l{k:02d}.wav", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    hop = SR // 100
    fr = np.abs(x[: len(x) // hop * hop]).reshape(-1, hop).max(1) > 0.015
    on = np.nonzero(fr)[0]
    segs, a, prev = [], on[0], on[0]
    for j in on[1:]:
        if j - prev > 25:
            segs.append((a, prev + 1)); a = j
        prev = j
    segs.append((a, prev + 1))
    gap = int(MAXGAP.get(k, 0.24) * 100)
    pieces, onsets, t = [], [], 0
    pad = 3  # 30 ms of air around each phrase
    for i, (s, e) in enumerate(segs):
        s0, e0 = max(0, s - pad), min(len(fr), e + pad)
        if i:
            g = min(s - segs[i - 1][1], gap)
            pieces.append(np.zeros(max(0, g - 2 * pad) * hop)); t += max(0, g - 2 * pad)
        onsets.append(round((t + (s - s0)) / 100, 2))
        pieces.append(x[s0 * hop: e0 * hop]); t += e0 - s0
    y = np.concatenate(pieces)
    y[: 96] *= np.linspace(0, 1, 96); y[-480:] *= np.linspace(1, 0, 480)
    with wave.open(f"assets/audio/vo/p{k:02d}.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
    tmp = f"assets/audio/vo/p{k:02d}.wav"
    tempo = TEMPO.get(k, 1.1)
    with wave.open(tmp, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
    sped = subprocess.run(["ffmpeg", "-v", "error", "-i", tmp, "-af", f"atempo={tempo}", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    y = np.frombuffer(sped, np.float32).astype(np.float64)
    onsets = [round(o / tempo, 2) for o in onsets]
    with wave.open(tmp, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
    out[k] = {"dur": round(len(y) / SR, 2), "phrases": onsets}
    print(k, out[k])
