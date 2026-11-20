import math
import os
import random
import struct
import subprocess
import wave

SAMPLE_RATE = 44100
BPM = 116.0
BEAT_SEC = 60.0 / BPM
STEP_SEC = BEAT_SEC / 4.0  # 16th note
TOTAL_BARS = 24  # ~49.65 seconds at 116 BPM
DURATION = TOTAL_BARS * 4 * BEAT_SEC
NUM_SAMPLES = int(DURATION * SAMPLE_RATE)


def midi_to_freq(midi_note):
    return 440.0 * (2.0 ** ((midi_note - 69.0) / 12.0))


def clamp(x, lo=-1.0, hi=1.0):
    return max(lo, min(hi, x))


def main():
    os.makedirs("video/music", exist_ok=True)
    wav_path = "video/music/funky-cyber-groove.wav"
    mp3_path = "public/funky-cyber-groove.mp3"

    random.seed(77)
    left_buf = [0.0] * NUM_SAMPLES
    right_buf = [0.0] * NUM_SAMPLES

    # -------------------------------------------------------------------------
    # 1. Funky Slap / Synth Bassline (16 steps per bar, 4-bar phrase)
    # Notes in C Dorian / C Minor Funk (C2=36, Eb2=39, F2=41, F#2=42, G2=43, A2=45, Bb2=46, C3=48, D3=50, Eb3=51)
    # -------------------------------------------------------------------------
    bass_patterns = [
        # Bar 0 (Cm9 groove with octave slap pops)
        [36, 0, 48, 36, 0, 39, 41, 42, 43, 0, 55, 43, 46, 0, 48, 39],
        # Bar 1 (Cm9 -> Fm9 walkup)
        [36, 36, 48, 0, 39, 41, 43, 0, 41, 0, 53, 41, 43, 45, 46, 48],
        # Bar 2 (Fm9 -> Gm7 groove)
        [41, 0, 53, 41, 0, 44, 46, 48, 43, 0, 55, 43, 46, 43, 41, 39],
        # Bar 3 (G#maj7 -> Bb7 -> turnaround)
        [44, 0, 56, 44, 46, 0, 58, 46, 43, 46, 48, 51, 50, 48, 46, 43],
    ]

    # -------------------------------------------------------------------------
    # 2. Funky Clavinet / Rhodes Chord Stabs (16th-note syncopation)
    # -------------------------------------------------------------------------
    chords = [
        [60, 63, 67, 70, 74],  # Cm9
        [60, 63, 67, 70, 74],  # Cm9
        [65, 68, 72, 75, 79],  # Fm9
        [67, 70, 74, 77, 81],  # Gm9 / turnaround
    ]
    stab_steps = {0, 3, 6, 8, 11, 14}  # classic Tresillo / funk syncopation

    # -------------------------------------------------------------------------
    # 3. Catchy Synth-Funk Lead Hook (plays prominently on bars 4..11 and 16..23)
    # -------------------------------------------------------------------------
    lead_patterns = [
        [72, 0, 75, 77, 79, 0, 77, 75, 72, 0, 70, 72, 0, 67, 70, 0],
        [72, 0, 75, 77, 82, 0, 79, 77, 79, 0, 75, 72, 70, 0, 0, 0],
        [77, 0, 79, 80, 82, 0, 79, 77, 75, 0, 72, 75, 70, 0, 67, 0],
        [68, 72, 75, 79, 70, 74, 77, 82, 84, 0, 82, 79, 77, 75, 72, 70],
    ]

    total_steps = TOTAL_BARS * 16

    for step_idx in range(total_steps):
        bar = step_idx // 16
        step = step_idx % 16
        t_start = step_idx * STEP_SEC
        i_start = int(t_start * SAMPLE_RATE)

        # --- A. DRUMS (Punchy Four-on-the-Floor + Funk Ghost Snare + 16th Hats) ---
        # Kick on 0, 4, 8, 12 + funky syncopated kick on 10 or 14
        if step in (0, 4, 8, 12) or (step == 11 and bar % 2 == 1):
            kick_len = int(0.19 * SAMPLE_RATE)
            for k in range(kick_len):
                idx = i_start + k
                if idx >= NUM_SAMPLES:
                    break
                tk = k / SAMPLE_RATE
                # Pitch drop from 135Hz to 46Hz
                freq = 46.0 + 95.0 * math.exp(-tk * 38.0)
                env = math.exp(-tk * 14.0)
                click = 0.35 * math.exp(-tk * 180.0) * math.sin(2.0 * math.pi * 1200.0 * tk)
                sig = 0.52 * (math.sin(2.0 * math.pi * freq * tk) * env + click)
                left_buf[idx] += sig
                right_buf[idx] += sig

        # Snare + Clap on steps 4 and 12 (beats 2 and 4), plus ghost snares on 7, 15
        if step in (4, 12) or (step in (7, 15) and bar % 2 == 0):
            is_ghost = step in (7, 15)
            gain = 0.16 if is_ghost else 0.40
            sn_len = int(0.16 * SAMPLE_RATE)
            for k in range(sn_len):
                idx = i_start + k
                if idx >= NUM_SAMPLES:
                    break
                tk = k / SAMPLE_RATE
                tone = math.sin(2.0 * math.pi * 195.0 * tk) * math.exp(-tk * 28.0)
                noise = (random.random() * 2.0 - 1.0) * math.exp(-tk * (26.0 if is_ghost else 17.0))
                sig = gain * (0.45 * tone + 0.75 * noise)
                left_buf[idx] += sig * 0.96
                right_buf[idx] += sig * 1.04

        # 16th-note Hi-Hats (open on offbeats step 2, 6, 10, 14)
        hat_open = step in (2, 6, 10, 14)
        hat_len = int((0.11 if hat_open else 0.04) * SAMPLE_RATE)
        hat_gain = 0.12 if hat_open else (0.08 if step % 2 == 0 else 0.05)
        for k in range(hat_len):
            idx = i_start + k
            if idx >= NUM_SAMPLES:
                break
            tk = k / SAMPLE_RATE
            decay = 22.0 if hat_open else 65.0
            metallic = (
                math.sin(2.0 * math.pi * 6300.0 * tk)
                + math.sin(2.0 * math.pi * 8750.0 * tk)
                + (random.random() * 2.0 - 1.0)
            ) * 0.35
            sig = hat_gain * metallic * math.exp(-tk * decay)
            left_buf[idx] += sig * 1.1
            right_buf[idx] += sig * 0.85

        # --- B. FUNKY SLAP SYNTH BASS ---
        note = bass_patterns[bar % 4][step]
        if note > 0:
            is_pop = note >= 48
            freq = midi_to_freq(note)
            note_len = int(STEP_SEC * (0.82 if is_pop else 1.15) * SAMPLE_RATE)
            for k in range(note_len):
                idx = i_start + k
                if idx >= NUM_SAMPLES:
                    break
                tk = k / SAMPLE_RATE
                env = (1.0 - math.exp(-tk * 260.0)) * math.exp(-tk * (11.0 if is_pop else 7.5))
                # FM / Saw-like slap bass harmonic richness
                mod_index = (3.6 if is_pop else 2.1) * math.exp(-tk * 22.0)
                mod = math.sin(2.0 * math.pi * freq * 2.0 * tk)
                sub = math.sin(2.0 * math.pi * freq * 0.5 * tk)
                carrier = math.sin(2.0 * math.pi * freq * tk + mod_index * mod)
                sig = 0.36 * env * (0.68 * carrier + 0.32 * sub)
                left_buf[idx] += sig
                right_buf[idx] += sig

        # --- C. FUNKY CLAVINET / RHODES CHORD STABS ---
        if step in stab_steps:
            chord = chords[bar % 4]
            stab_len = int(STEP_SEC * (1.35 if step in (0, 6, 11) else 0.75) * SAMPLE_RATE)
            for k in range(stab_len):
                idx = i_start + k
                if idx >= NUM_SAMPLES:
                    break
                tk = k / SAMPLE_RATE
                env = (1.0 - math.exp(-tk * 190.0)) * math.exp(-tk * 9.5)
                acc = 0.0
                for n_midi in chord:
                    f = midi_to_freq(n_midi)
                    # Clavinet-style odd+even harmonics
                    acc += math.sin(2.0 * math.pi * f * tk + 0.8 * math.sin(2.0 * math.pi * f * 3.0 * tk) * math.exp(-tk * 18.0))
                sig = 0.055 * env * acc
                # Slight stereo chorus pan
                left_buf[idx] += sig * 1.08
                right_buf[idx] += sig * 0.92

        # --- D. CYBER-FUNK LEAD SYNTH RIFF ---
        lead_note = lead_patterns[bar % 4][step]
        if lead_note > 0 and (bar % 8 >= 2):
            f = midi_to_freq(lead_note)
            lead_len = int(STEP_SEC * 1.45 * SAMPLE_RATE)
            for k in range(lead_len):
                idx = i_start + k
                if idx >= NUM_SAMPLES:
                    break
                tk = k / SAMPLE_RATE
                env = (1.0 - math.exp(-tk * 140.0)) * math.exp(-tk * 6.5)
                vib = 1.0 + 0.004 * math.sin(2.0 * math.pi * 6.0 * tk)
                # Detuned dual-saw emulation (first 5 harmonics)
                s1 = (
                    math.sin(2.0 * math.pi * f * vib * tk)
                    + 0.5 * math.sin(2.0 * math.pi * f * 2.003 * tk)
                    + 0.33 * math.sin(2.0 * math.pi * f * 3.0 * tk)
                )
                s2 = (
                    math.sin(2.0 * math.pi * f * 0.996 * tk)
                    + 0.5 * math.sin(2.0 * math.pi * f * 1.995 * tk)
                )
                left_buf[idx] += 0.085 * env * s1
                right_buf[idx] += 0.085 * env * s2

    # Master soft-clip / limiter so the groove hits loud and warm without clipping
    pcm = bytearray(NUM_SAMPLES * 4)
    for i in range(NUM_SAMPLES):
        l = math.tanh(left_buf[i] * 1.25) * 0.92
        r = math.tanh(right_buf[i] * 1.25) * 0.92
        li = int(clamp(l) * 32767)
        ri = int(clamp(r) * 32767)
        struct.pack_into("<hh", pcm, i * 4, li, ri)

    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm)

    print(f"[music] Wrote {wav_path} ({os.path.getsize(wav_path)} bytes)")

    ffmpeg_exe = os.path.join("node_modules", "ffmpeg-static", "ffmpeg.exe")
    if os.path.exists(ffmpeg_exe):
        subprocess.run(
            [
                ffmpeg_exe,
                "-y",
                "-i",
                wav_path,
                "-codec:a",
                "libmp3lame",
                "-qscale:a",
                "2",
                mp3_path,
            ],
            check=True,
        )
        print(f"[music] Converted to {mp3_path} ({os.path.getsize(mp3_path)} bytes)")


if __name__ == "__main__":
    main()
