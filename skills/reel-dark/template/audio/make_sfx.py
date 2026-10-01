"""Synthesize the mehdiagent sound kit from scratch (no samples, no third-party audio) into audio/sources/.

    python3 make_sfx.py            # writes pop.wav click.wav caption-click.wav whoosh.wav thud.wav (48 kHz stereo)

pop            soft UI pop: pitch-dropping sine + a tiny noise tick     (landings, chips, emoji, reveals)
click          crisp mouse/key press: filtered noise burst + short ping (toggles, Post, Enter, file drop)
caption-click  softer press used on caption words                      (first/last word of full-screen captions)
whoosh         band-swept noise swell                                   (slashes, camera moves, transitions)
thud           low body hit                                             (tiles landing, impacts)
Every file is peak-normalised to -1 dBFS; mix.py sets the real level per cue.
"""
import wave
from pathlib import Path
import numpy as np

SR = 48000
OUT = Path(__file__).resolve().parent / "sources"
rng = np.random.default_rng(7)

def t(d): return np.arange(int(SR * d)) / SR
def env(n, a, d):  # attack seconds, exponential decay time-constant seconds
    x = np.arange(n) / SR
    return np.minimum(1, x / max(a, 1e-4)) * np.exp(-x / d)
def bandpass(x, lo, hi):
    f = np.fft.rfft(x); fr = np.fft.rfftfreq(len(x), 1 / SR)
    f[(fr < lo) | (fr > hi)] = 0
    return np.fft.irfft(f, len(x))
def write(name, mono, width=0.0):
    mono = mono / (np.abs(mono).max() + 1e-12) * 10 ** (-1 / 20)
    pad = np.zeros(int(SR * .01)); mono = np.concatenate([mono, pad])
    l = mono; r = np.roll(mono, int(width * SR)) if width else mono
    st = np.stack([l, r], 1)
    with wave.open(str(OUT / name), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(st, -1, 1) * 32767).astype("<i2").tobytes())

def pop():
    x = t(.11); f = 380 + 620 * np.exp(-x / .018)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(x), .002, .035)
    tick = bandpass(rng.standard_normal(len(x)), 2500, 9000) * env(len(x), .0005, .004) * .35
    return body + tick
def click(soft=False):
    x = t(.06)
    burst = bandpass(rng.standard_normal(len(x)), 1800 if soft else 2500, 7000 if soft else 12000) * env(len(x), .0003, .003 if soft else .0025)
    ping = np.sin(2 * np.pi * (1200 if soft else 2100) * x) * env(len(x), .0005, .012 if soft else .009) * (.45 if soft else .6)
    return burst + ping
def whoosh():
    d = .42; n = int(SR * d); x = np.arange(n) / SR; noise = rng.standard_normal(n); out = np.zeros(n); hop = 512
    for s in range(0, n, hop):                       # sweep a band from low to high and back down a little
        u = s / n; c = 300 + 3200 * np.sin(np.pi * u) ** 1.5; seg = noise[max(0, s - hop):s + 2 * hop]
        f = bandpass(seg, c * .6, c * 1.6)[hop if s else 0:][:hop]; out[s:s + len(f)] = f
    shape = np.sin(np.pi * np.clip(x / d, 0, 1)) ** 2 * np.exp(-x / .5)
    return out * shape
def thud():
    x = t(.42); f = 42 + 50 * np.exp(-x / .03)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(x), .002, .11)
    knock = bandpass(rng.standard_normal(len(x)), 120, 1400) * env(len(x), .0005, .012) * .5
    return body + knock

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    write("pop.wav", pop()); write("click.wav", click()); write("caption-click.wav", click(soft=True))
    write("whoosh.wav", whoosh(), width=.0006); write("thud.wav", thud())
    print("wrote", ", ".join(sorted(p.name for p in OUT.glob("*.wav"))))
