import math
import os
import random
import struct
import subprocess
import wave

SAMPLE_RATE = 44100
BPM = 124.0  # Deep Melodic / Slap House tempo (Alok & Daniel Blume - Rapture vibe)
BEAT_SEC = 60.0 / BPM
STEP_SEC = BEAT_SEC / 4.0  # 16th note
TOTAL_BARS = 24  # ~46.45 seconds at 124 BPM
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

    random.seed(124)
    left_buf = [0.0] * NUM_SAMPLES
    right_buf = [0.0] * NUM_SAMPLES

    # -------------------------------------------------------------------------
    # 1. Slap House / Brazilian Bass Pattern in F# Minor (F#m -> Dmaj7 -> Bm7 -> C#7)
    # F#1=30, A1=33, B1=35, C#2=37, D2=38, E2=40, F#2=42, G#2=44, A2=45, B2=47, C#3=49, D3=50
    # -------------------------------------------------------------------------
    bass_patterns = [
        # Bar 0: F#m deep slap-house bounce (offbeat & syncopated plucks)
        [42, 0, 42, 54, 0, 42, 45, 0, 42, 0, 54, 42, 0, 40, 42, 44],
        # Bar 1: Dmaj7 deep bounce
        [38, 0, 38, 50, 0, 38, 42, 0, 38, 0, 50, 38, 0, 40, 42, 45],
        # Bar 2: Bm7 groove
        [35, 0, 35, 47, 0, 35, 38, 0, 35, 0, 47, 35, 0, 38, 40, 42],
        # Bar 3: C#7sus4 -> C#7 turnaround
        [37, 0, 37, 49, 0, 37, 42, 0, 37, 0, 49, 44, 42, 40, 37, 35],
    ]

    # -------------------------------------------------------------------------
    # 2. Lush Sidechained Vocal-Formant / Supersaw Chords (F#m9 -> Dmaj9 -> Bm9 -> C#7)
    # -------------------------------------------------------------------------
    chords = [
        [54, 57, 61, 64, 68],  # F#m9
        [50, 54, 57, 61, 64],  # Dmaj9
        [47, 50, 54, 57, 61],  # Bm9
        [49, 53, 56, 59, 64],  # C#7(#9)
    ]

    # -------------------------------------------------------------------------
    # 3. Hypnotic "Rapture"-Style Euphoric Minor Vocal/Pluck Lead Hook
    # F#4=66, G#4=68, A4=69, B4=71, C#5=73, D5=74, E5=76, F#5=78
    # -------------------------------------------------------------------------
    lead_patterns = [
        # Bar 0: Euphoric rising & falling minor motif
        [69, 0, 69, 73, 0, 71, 69, 68, 66, 0, 66, 69, 0, 68, 66, 64],
        # Bar 1: Answer phrase over Dmaj7
        [66, 0, 66, 74, 0, 73, 71, 69, 68, 0, 69, 71, 0, 69, 68, 66],
        # Bar 2: Climactic phrase over Bm7
        [71, 0, 71, 74, 0, 73, 71, 69, 73, 0, 73, 76, 0, 74, 73, 71],
        # Bar 3: Resolution over C#7
        [68, 0, 69, 71, 0, 69, 68, 66, 68, 0, 73, 0, 71, 69, 68, 66],
    ]

    total_steps = TOTAL_BARS * 16

    for step_idx in range(total_steps):
        bar = step_idx // 16
        step = step_idx % 16
        t_start = step_idx * STEP_SEC
        i_start = int(t_start * SAMPLE_RATE)

        # --- A. 124 BPM DEEP HOUSE DRUMS ---
        # Four-on-the-floor punchy deep house kick on steps 0, 4, 8, 12
        if step in (0, 4, 8, 12):
            kick_len = int(0.21 * SAMPLE_RATE)
            for k in range(kick_len):
                idx = i_start + k
                if idx >= NUM_SAMPLES:
                    break
                tk = k / SAMPLE_RATE
                # Fast punchy pitch sweep from 150Hz down to 44Hz sub
                freq = 44.0 + 110.0 * math.exp(-tk * 42.0)
                env = math.exp(-tk * 13.5)
                click = 0.28 * math.exp(-tk * 220.0) * math.sin(2.0 * math.pi * 1650.0 * tk)
                sig = 0.56 * (math.sin(2.0 * math.pi * freq * tk) * env + click)
                left_buf[idx] += sig
                right_buf[idx] += sig

        # Tight House Clap + Snare on beats 2 & 4 (steps 4, 12)
        if step in (4, 12):
            sn_len = int(0.15 * SAMPLE_RATE)
            for k in range(sn_len):
                idx = i_start + k
                if idx >= NUM_SAMPLES:
                    break
                tk = k / SAMPLE_RATE
                # Multi-tap clap transient + crisp white noise tail
                clap_env = (
                    0.4 * math.exp(-max(0.0, tk) * 90.0)
                    + 0.4 * math.exp(-max(0.0, tk - 0.008) * 90.0)
                    + 0.8 * math.exp(-max(0.0, tk - 0.016) * 24.0)
                )
                body = math.sin(2.0 * math.pi * 210.0 * tk) * math.exp(-tk * 35.0)
                noise = (random.random() * 2.0 - 1.0) * clap_env
                sig = 0.32 * (0.3 * body + 0.7 * noise)
                left_buf[idx] += sig * 0.94
                right_buf[idx] += sig * 1.06

        # Signature Off-Beat Open House Hi-Hat (steps 2, 6, 10, 14) + subtle closed 16th shaker
        is_open_hat = step in (2, 6, 10, 14)
        hat_len = int((0.13 if is_open_hat else 0.035) * SAMPLE_RATE)
        hat_gain = 0.14 if is_open_hat else 0.045
        for k in range(hat_len):
            idx = i_start + k
            if idx >= NUM_SAMPLES:
                break
            tk = k / SAMPLE_RATE
            decay = 20.0 if is_open_hat else 75.0
            sizzle = (
                math.sin(2.0 * math.pi * 7100.0 * tk)
                + math.sin(2.0 * math.pi * 9850.0 * tk)
                + (random.random() * 2.0 - 1.0) * 1.2
            ) * 0.33
            sig = hat_gain * sizzle * math.exp(-tk * decay)
            left_buf[idx] += sig * 1.08
            right_buf[idx] += sig * 0.88

        # --- B. BRAZILIAN BASS / SLAP HOUSE PLUCK BASS ---
        note = bass_patterns[bar % 4][step]
        if note > 0:
            freq = midi_to_freq(note)
            note_len = int(STEP_SEC * 1.15 * SAMPLE_RATE)
            for k in range(note_len):
                idx = i_start + k
                if idx >= NUM_SAMPLES:
                    break
                tk = k / SAMPLE_RATE
                # Sidechain ducking when note lands on kick (steps 0, 4, 8, 12)
                sc = (1.0 - 0.78 * math.exp(-tk * 18.0)) if (step % 4 == 0) else 1.0
                env = (1.0 - math.exp(-tk * 320.0)) * math.exp(-tk * 10.5) * sc
                # Metallic FM Slap-House Pluck (2:1 and 3:1 ratios with fast decay)
                fm_env = math.exp(-tk * 32.0)
                mod = math.sin(2.0 * math.pi * freq * 2.0 * tk) + 0.45 * math.sin(2.0 * math.pi * freq * 3.0 * tk)
                carrier = math.sin(2.0 * math.pi * freq * tk + 2.8 * fm_env * mod)
                sub = math.sin(2.0 * math.pi * freq * 0.5 * tk)
                sig = 0.38 * env * (0.62 * carrier + 0.38 * sub)
                left_buf[idx] += sig
                right_buf[idx] += sig

        # --- C. PUMPING SIDECHAINED VOCAL-FORMANT SUPERSAW PAD (Rendered per beat) ---
        if step in (0, 4, 8, 12):
            chord = chords[bar % 4]
            beat_len = int(BEAT_SEC * SAMPLE_RATE)
            for k in range(beat_len):
                idx = i_start + k
                if idx >= NUM_SAMPLES:
                    break
                tk = k / SAMPLE_RATE
                # Classic Alok / Slap House pumping sidechain envelope on every beat
                pump = (1.0 - math.exp(-tk * 11.0)) * math.exp(-tk * 1.2)
                acc_l = 0.0
                acc_r = 0.0
                for n_midi in chord:
                    f = midi_to_freq(n_midi)
                    # Vocal-formant warm detuned stereo pad
                    acc_l += math.sin(2.0 * math.pi * f * 0.998 * tk) + 0.4 * math.sin(2.0 * math.pi * f * 2.002 * tk)
                    acc_r += math.sin(2.0 * math.pi * f * 1.002 * tk) + 0.4 * math.sin(2.0 * math.pi * f * 1.998 * tk)
                left_buf[idx] += 0.042 * pump * acc_l
                right_buf[idx] += 0.042 * pump * acc_r

        # --- D. HYPNOTIC "RAPTURE" MELODIC VOCAL-PLUCK HOOK ---
        lead_note = lead_patterns[bar % 4][step]
        if lead_note > 0:
            f = midi_to_freq(lead_note)
            lead_len = int(STEP_SEC * 1.65 * SAMPLE_RATE)
            for k in range(lead_len):
                idx = i_start + k
                if idx >= NUM_SAMPLES:
                    break
                tk = k / SAMPLE_RATE
                sc = (1.0 - 0.65 * math.exp(-tk * 16.0)) if (step % 4 == 0) else 1.0
                env = (1.0 - math.exp(-tk * 180.0)) * math.exp(-tk * 6.2) * sc
                vib = 1.0 + 0.0025 * math.sin(2.0 * math.pi * 5.5 * tk)
                # Silky vocal-formant lead (fundamental + 2nd + 3rd harmonic formant peak)
                formant = math.exp(-tk * 14.0)
                w_l = (
                    math.sin(2.0 * math.pi * f * vib * tk)
                    + 0.55 * math.sin(2.0 * math.pi * f * 2.003 * tk)
                    + 0.35 * formant * math.sin(2.0 * math.pi * f * 3.0 * tk)
                )
                w_r = (
                    math.sin(2.0 * math.pi * f * 0.997 * vib * tk)
                    + 0.55 * math.sin(2.0 * math.pi * f * 1.997 * tk)
                    + 0.35 * formant * math.sin(2.0 * math.pi * f * 3.004 * tk)
                )
                left_buf[idx] += 0.095 * env * w_l
                right_buf[idx] += 0.095 * env * w_r

    # Master warm club limiter
    pcm = bytearray(NUM_SAMPLES * 4)
    for i in range(NUM_SAMPLES):
        l = math.tanh(left_buf[i] * 1.28) * 0.92
        r = math.tanh(right_buf[i] * 1.28) * 0.92
        li = int(clamp(l) * 32767)
        ri = int(clamp(r) * 32767)
        struct.pack_into("<hh", pcm, i * 4, li, ri)

    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm)

    print(f"[music] Wrote 124 BPM Rapture-style Deep Slap House WAV: {wav_path} ({os.path.getsize(wav_path)} bytes)")

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
