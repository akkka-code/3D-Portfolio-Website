"""
make_music.py - synthesises the ORIGINAL soundtrack for the promo video.

Dark synthwave, 100 BPM, A minor, ~46 s, 44.1 kHz / 16-bit stereo.
Uses ONLY the Python standard library (wave, math, struct, random), so the
result is an original work released by the author under CC0 1.0 - there are
no samples, loops or third-party recordings involved.

The arrangement is laid out on a bar grid (1 bar = 4 beats = 2.4 s) that is
shared with video/build_promo.jsx so that scene transitions land on beats:

    bar  0-1   (0.0 - 4.8 s)   intro: pad + filtered bass, riser
    bar  2-4   (4.8 - 12.0 s)  name reveal: + kick, hats            (impact @ 4.8)
    bar  5-8   (12.0 - 21.6 s) skills: full groove + lead arp       (impact @ 12.0)
    bar  9-13  (21.6 - 33.6 s) projects: full groove, clap          (impact @ 21.6)
    bar 14-15  (33.6 - 38.4 s) achievements: half-time break        (impact @ 33.6)
    bar 16-18  (38.4 - 46.0 s) CTA / outro: full, then fade out     (impact @ 38.4)

Run:  python video/music/make_music.py
Out:  video/music/promo_music.wav
"""

import math
import os
import random
import struct
import wave

SR = 44100
BPM = 100.0
BEAT = 60.0 / BPM          # 0.6 s
BAR = BEAT * 4             # 2.4 s
DURATION = 46.0
N = int(SR * DURATION)
TWO_PI = 2.0 * math.pi

random.seed(1337)          # deterministic output

# Section starts (seconds) - transitions get a riser before and an impact on.
IMPACTS = [2 * BAR, 5 * BAR, 9 * BAR, 14 * BAR, 16 * BAR]

L = [0.0] * N
R = [0.0] * N


def midi_hz(m):
    return 440.0 * 2.0 ** ((m - 69) / 12.0)


def add(buf, start, samples, gain=1.0):
    """Mix a mono list of samples into buf at sample index start."""
    end = min(N, start + len(samples))
    for i in range(max(0, start), end):
        buf[i] += samples[i - start] * gain


def add_stereo(start, samples, gain=1.0, pan=0.0):
    """Equal-power pan, pan in [-1, 1]."""
    a = (pan + 1.0) * math.pi / 4.0
    add(L, start, samples, gain * math.cos(a))
    add(R, start, samples, gain * math.sin(a))


# --------------------------------------------------------------------------
# Instruments
# --------------------------------------------------------------------------

def kick(length=0.45):
    n = int(SR * length)
    out = []
    phase = 0.0
    for i in range(n):
        t = i / SR
        f = 45.0 + 110.0 * math.exp(-t * 28.0)
        phase += TWO_PI * f / SR
        env = math.exp(-t * 7.5)
        click = math.exp(-t * 400.0) * 0.4
        out.append(math.tanh(1.6 * math.sin(phase) * env) + click * (random.random() * 2 - 1))
    return out


def snare(length=0.32):
    n = int(SR * length)
    out = []
    lp = 0.0
    for i in range(n):
        t = i / SR
        noise = random.random() * 2 - 1
        hp = noise - lp            # crude high-pass (noise minus its low-pass)
        lp += 0.25 * (noise - lp)
        tone = math.sin(TWO_PI * 185.0 * t) * math.exp(-t * 30.0)
        out.append(0.75 * hp * math.exp(-t * 14.0) + 0.5 * tone)
    return out


def clap(length=0.3):
    n = int(SR * length)
    out = []
    for i in range(n):
        t = i / SR
        # three quick bursts then a tail
        env = 0.0
        for k, off in enumerate((0.0, 0.011, 0.022)):
            if t >= off:
                env = max(env, math.exp(-(t - off) * 120.0))
        env = max(env, 0.6 * math.exp(-max(0.0, t - 0.022) * 18.0) if t > 0.022 else 0.0)
        out.append((random.random() * 2 - 1) * env)
    return out


def hat(length=0.06, open_=False):
    n = int(SR * (0.22 if open_ else length))
    decay = 18.0 if open_ else 70.0
    out = []
    prev = 0.0
    for i in range(n):
        t = i / SR
        x = random.random() * 2 - 1
        y = x - prev                   # first-difference high-pass
        prev = x
        out.append(y * math.exp(-t * decay) * 0.5)
    return out


def saw_voice(freq, length, detune=0.0, cutoff=0.12, attack=0.005, release=0.08, sub=0.0):
    """Two slightly detuned band-limited-ish saws through a one-pole low-pass."""
    n = int(SR * length)
    out = []
    p1 = random.random()
    p2 = random.random()
    lp = 0.0
    lp2 = 0.0
    f1 = freq * (1.0 + detune)
    f2 = freq * (1.0 - detune)
    for i in range(n):
        t = i / SR
        p1 = (p1 + f1 / SR) % 1.0
        p2 = (p2 + f2 / SR) % 1.0
        x = (2 * p1 - 1) + (2 * p2 - 1)
        if sub:
            x += sub * math.sin(TWO_PI * freq * 0.5 * t)
        lp += cutoff * (x - lp)
        lp2 += cutoff * (lp - lp2)          # 2 poles = 12 dB/oct
        env = min(1.0, t / attack) if attack > 0 else 1.0
        rel_start = length - release
        if t > rel_start:
            env *= max(0.0, 1.0 - (t - rel_start) / release)
        out.append(lp2 * env * 0.5)
    return out


def riser(length):
    """Filtered noise sweep + rising tone, crescendo into the next section."""
    n = int(SR * length)
    out = []
    lp = 0.0
    phase = 0.0
    for i in range(n):
        t = i / n
        c = 0.01 + 0.4 * t * t
        x = random.random() * 2 - 1
        lp += c * (x - lp)
        phase += TWO_PI * (200.0 + 1400.0 * t * t) / SR
        out.append((lp * 0.9 + 0.18 * math.sin(phase)) * (t ** 2.2))
    return out


def impact(length=2.2):
    """Low boom + noise crash on section downbeats."""
    n = int(SR * length)
    out = []
    phase = 0.0
    prev = 0.0
    for i in range(n):
        t = i / SR
        phase += TWO_PI * (38.0 + 60.0 * math.exp(-t * 10.0)) / SR
        boom = math.sin(phase) * math.exp(-t * 2.2)
        x = random.random() * 2 - 1
        crash = (x - prev) * math.exp(-t * 3.0) * 0.35
        prev = x
        out.append(math.tanh(1.4 * boom) * 0.9 + crash)
    return out


# --------------------------------------------------------------------------
# Harmony: Am - F - Dm - E (dark minor cadence), one chord per bar
# --------------------------------------------------------------------------
CHORDS = [
    (57, [57, 60, 64, 69]),   # A minor
    (53, [53, 57, 60, 65]),   # F major
    (50, [50, 53, 57, 62]),   # D minor
    (52, [52, 56, 59, 64]),   # E major (harmonic minor tension)
]

TOTAL_BARS = int(math.ceil(DURATION / BAR))


def section(bar):
    if bar < 2:
        return "intro"
    if bar < 5:
        return "name"
    if bar < 9:
        return "skills"
    if bar < 14:
        return "projects"
    if bar < 16:
        return "break"
    return "outro"


print("Synthesising %d bars at %.0f BPM ..." % (TOTAL_BARS, BPM))

KICK = kick()
SNARE = snare()
CLAP = clap()
HAT_C = hat()
HAT_O = hat(open_=True)

for bar in range(TOTAL_BARS):
    sec = section(bar)
    t0 = bar * BAR
    root, chord = CHORDS[bar % 4]
    s0 = int(t0 * SR)

    # ---- Pad: sustained chord, slow attack, wide stereo -------------------
    pad_cut = 0.02 if sec == "intro" else 0.035
    for k, note in enumerate(chord):
        v = saw_voice(midi_hz(note), BAR + 0.3, detune=0.006, cutoff=pad_cut,
                      attack=0.5, release=0.6)
        add_stereo(s0, v, 0.11, pan=(-0.6 if k % 2 == 0 else 0.6))

    # ---- Bass arpeggio: 16ths root / octave / fifth -----------------------
    pattern = [0, 12, 7, 12, 0, 12, 7, 10, 0, 12, 7, 12, 0, 15, 12, 7]
    bass_cut = 0.02 + (0.0 if sec == "intro" else 0.035)
    if sec == "intro":
        bass_cut += 0.03 * (bar + 0.5) / 2.0     # filter opens through intro
    step = BEAT / 4
    for i, iv in enumerate(pattern):
        if sec == "break" and i % 2 == 1:
            continue                              # half-density in the break
        f = midi_hz(root - 24 + iv)
        v = saw_voice(f, step * 0.9, detune=0.003, cutoff=bass_cut,
                      attack=0.003, release=0.04, sub=0.8)
        accent = 1.0 if i % 4 == 0 else 0.7
        add_stereo(int((t0 + i * step) * SR), v, 0.32 * accent, pan=0.0)

    # ---- Lead arp (skills + outro): bright plucks, ping-pong pan ----------
    if sec in ("skills", "outro"):
        arp = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[3] + 12,
               chord[2] + 12, chord[1] + 12, chord[3] + 12, chord[2] + 24]
        for i in range(8):
            v = saw_voice(midi_hz(arp[i]), BEAT / 2 * 0.95, detune=0.004,
                          cutoff=0.09, attack=0.002, release=0.2)
            add_stereo(int((t0 + i * BEAT / 2) * SR), v, 0.075,
                       pan=(-0.5 if i % 2 == 0 else 0.5))

    # ---- Drums ------------------------------------------------------------
    if sec != "intro":
        for b in range(4):
            bt = t0 + b * BEAT
            if sec == "break":
                if b == 0:
                    add_stereo(int(bt * SR), KICK, 0.9)
                if b == 2:
                    add_stereo(int(bt * SR), SNARE, 0.45)
            else:
                add_stereo(int(bt * SR), KICK, 0.9)
                if b in (1, 3) and sec != "name":
                    add_stereo(int(bt * SR), SNARE, 0.4)
                    add_stereo(int(bt * SR), CLAP, 0.28, pan=0.1)
                if b == 3 and sec == "name":
                    add_stereo(int(bt * SR), CLAP, 0.25)
            # hats on 8ths / 16ths
            subdiv = 4 if sec in ("projects", "outro") else 2
            for h in range(subdiv):
                ht = bt + h * BEAT / subdiv
                is_off = (h == subdiv // 2)
                smp = HAT_O if (is_off and sec != "break") else HAT_C
                add_stereo(int(ht * SR), smp, 0.22 if is_off else 0.13,
                           pan=0.25 if h % 2 else -0.25)

# ---- Risers (1 bar before each section) and impacts on the downbeat ------
for t in IMPACTS:
    r = riser(BAR)
    add_stereo(int((t - BAR) * SR), r, 0.35, pan=0.0)
    add_stereo(int(t * SR), impact(), 0.7, pan=0.0)

# Short boot glitch at the very start (bit-crushed blip) ------------------
blip = []
for i in range(int(SR * 0.35)):
    t = i / SR
    blip.append(math.copysign(1.0, math.sin(TWO_PI * (880 - 1200 * t) * t)) * math.exp(-t * 9) * 0.25)
add_stereo(0, blip, 0.5)

# --------------------------------------------------------------------------
# Master: fade in/out, soft-clip, normalise to -1 dBFS
# --------------------------------------------------------------------------
fade_in = int(0.05 * SR)
fade_out_start = int((DURATION - 4.0) * SR)
for i in range(N):
    g = 1.0
    if i < fade_in:
        g = i / fade_in
    if i > fade_out_start:
        g *= max(0.0, 1.0 - (i - fade_out_start) / (N - fade_out_start)) ** 1.5
    L[i] = math.tanh(L[i] * 1.1) * g
    R[i] = math.tanh(R[i] * 1.1) * g

peak = max(max(abs(x) for x in L), max(abs(x) for x in R), 1e-9)
target = 10 ** (-1.0 / 20.0)            # -1 dBFS
gain = target / peak
print("Peak before normalise: %.3f  -> gain %.3f" % (peak, gain))

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "promo_music.wav")
with wave.open(out_path, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    frames = bytearray()
    for i in range(N):
        frames += struct.pack("<hh", int(L[i] * gain * 32767), int(R[i] * gain * 32767))
    w.writeframes(bytes(frames))

print("Wrote %s (%.1f s)" % (out_path, DURATION))
