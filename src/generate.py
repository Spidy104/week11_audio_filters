"""Small audio generator (no external deps).

Creates 10-second WAV files in ../audio/:
- hum_60hz.wav         : 60 Hz sine hum (10s)
- music.wav            : simple synthesized music (10s)
- speech_like.wav      : a speech-like synthetic signal (10s)
- mixed_with_hum.wav   : music + speech_like + low-level 60Hz hum (10s)

Usage: python3 src/generate.py
"""
from __future__ import annotations
import math
import os
import random
import wave
import struct
from typing import List

SR = 44100
DURATION = 10.0


def write_wav(path: str, samples: List[float], sr: int = SR) -> None:
    # normalize to int16
    max_abs = max((abs(s) for s in samples), default=0.0)
    if max_abs < 1e-9:
        max_abs = 1.0
    scale = 0.9 * 32767 / max_abs
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        frames = struct.pack('<' + 'h' * len(samples), *[int(max(-32768, min(32767, s * scale))) for s in samples])
        wf.writeframes(frames)


def sine_wave(freq: float, length: float, sr: int = SR, phase: float = 0.0, amp: float = 1.0) -> List[float]:
    n = int(length * sr)
    two_pi_f = 2.0 * math.pi * freq
    return [amp * math.sin(two_pi_f * (i / sr) + phase) for i in range(n)]


def generate_hum(sr: int = SR, duration: float = DURATION, freq: float = 60.0, amp: float = 0.05) -> List[float]:
    # add harmonics to hum for more realistic electrical hum
    n = int(duration * sr)
    out = [0.0] * n
    for i in range(n):
        t = i / sr
        # fundamental + 2nd and 3rd harmonics
        out[i] = amp * (
            0.7 * math.sin(2 * math.pi * freq * t) +
            0.2 * math.sin(2 * math.pi * 2 * freq * t) +
            0.1 * math.sin(2 * math.pi * 3 * freq * t)
        )
    return out


def adsr_envelope(n: int, sr: int, a=0.01, d=0.05, s=0.6, r=0.1) -> List[float]:
    # a,d,r are seconds. s is sustain level.
    env = [0.0] * n
    a_n = max(1, int(a * sr))
    d_n = max(1, int(d * sr))
    r_n = max(1, int(r * sr))
    sustain_n = max(0, n - (a_n + d_n + r_n))
    # attack
    for i in range(a_n):
        env[i] = (i / a_n)
    # decay
    for i in range(d_n):
        env[a_n + i] = 1.0 - (1.0 - s) * (i / d_n)
    # sustain
    for i in range(sustain_n):
        env[a_n + d_n + i] = s
    # release
    for i in range(r_n):
        idx = a_n + d_n + sustain_n + i
        if idx < n:
            env[idx] = s * (1.0 - (i / r_n))
    return env


def generate_music(sr: int = SR, duration: float = DURATION) -> List[float]:
    # richer melody with chord progression and multiple harmonics
    melody = [
        (440.0, 0.8), (494.0, 0.6), (523.25, 0.7), (587.33, 0.9),
        (659.25, 1.0), (587.33, 0.8), (523.25, 0.7), (494.0, 0.6),
        (440.0, 0.9), (392.0, 0.7), (349.23, 0.8), (329.63, 0.75),
        (293.66, 0.85), (329.63, 0.7), (349.23, 0.8), (440.0, 1.0)
    ]
    note_dur = duration / len(melody)
    out: List[float] = []
    for freq, velocity in melody:
        n = int(note_dur * sr)
        env = adsr_envelope(n, sr, a=0.005, d=0.08, s=0.6, r=0.08)
        for i in range(n):
            t = i / sr
            # add 5 harmonics for richer timbre (piano-like)
            val = 0.0
            val += 0.5 * math.sin(2 * math.pi * freq * t)
            val += 0.25 * math.sin(2 * math.pi * 2 * freq * t + 0.3)
            val += 0.15 * math.sin(2 * math.pi * 3 * freq * t + 0.7)
            val += 0.08 * math.sin(2 * math.pi * 4 * freq * t + 1.1)
            val += 0.04 * math.sin(2 * math.pi * 5 * freq * t + 1.5)
            # add subtle vibrato
            vibrato = 1.0 + 0.004 * math.sin(2 * math.pi * 5.5 * t)
            out.append(val * env[i] * velocity * vibrato)
    return out


def generate_speech_like(sr: int = SR, duration: float = DURATION) -> List[float]:
    # More realistic speech-like signal using formant synthesis
    n = int(duration * sr)
    out: List[float] = [0.0] * n
    random.seed(42)
    
    # vowel formants (F1, F2, F3) for more natural vowel sounds
    vowels = [
        (730, 1090, 2440),  # /a/ as in "father"
        (270, 2290, 3010),  # /i/ as in "see"
        (300, 870, 2240),   # /u/ as in "too"
        (530, 1840, 2480),  # /e/ as in "bed"
        (640, 1190, 2390),  # /o/ as in "off"
    ]
    
    # create speech-like syllables with formant synthesis
    syllable_count = 18
    syll_dur = duration / syllable_count
    
    for s_idx in range(syllable_count):
        start = int(s_idx * syll_dur * sr)
        length = int(syll_dur * sr)
        
        # vary envelope for voiced/unvoiced
        is_voiced = s_idx % 3 != 0
        if is_voiced:
            env = adsr_envelope(length, sr, a=0.008, d=0.02, s=0.4, r=0.03)
            f1, f2, f3 = random.choice(vowels)
            f0 = random.uniform(110, 140)  # fundamental frequency (pitch)
        else:
            # unvoiced consonant
            env = adsr_envelope(length, sr, a=0.002, d=0.01, s=0.15, r=0.015)
            f1, f2, f3 = 1500, 2500, 3500
            f0 = 0
        
        for i in range(length):
            pos = start + i
            if pos >= n:
                break
            t = i / sr
            
            if is_voiced:
                # voiced: use harmonic source
                source = 0.0
                for h in range(1, 8):
                    amp = 1.0 / h
                    source += amp * math.sin(2 * math.pi * f0 * h * t + random.uniform(0, 0.3))
                source *= 0.15
            else:
                # unvoiced: use noise
                source = random.uniform(-1, 1) * 0.3
            
            # apply formants as resonances
            formant_response = (
                0.5 * math.sin(2 * math.pi * f1 * t) +
                0.3 * math.sin(2 * math.pi * f2 * t) +
                0.15 * math.sin(2 * math.pi * f3 * t)
            )
            
            signal = source * (1.0 + 0.6 * formant_response)
            out[pos] += signal * env[i]
    
    # add consonant bursts for realism
    for k in range(8):
        idx = int(random.uniform(0.1, duration - 0.1) * sr)
        burst_len = random.randint(50, 150)
        for j in range(burst_len):
            if idx + j < n:
                out[idx + j] += 0.3 * (1.0 - j / burst_len) * random.uniform(-1, 1)
    
    return out


def mix(signals: List[List[float]]) -> List[float]:
    # mix lists (they may have slightly different lengths)
    maxlen = max(len(s) for s in signals)
    out = [0.0] * maxlen
    for s in signals:
        for i, v in enumerate(s):
            out[i] += v
    # scale down to avoid clipping
    return [x / max(1.0, len(signals) * 0.9) for x in out]


def main() -> None:
    print("Generating input.wav (10s, speech + music + 60Hz hum)")
    hum = generate_hum(freq=60.0, amp=0.06)
    music = generate_music()
    speech = generate_speech_like()
    mixed = mix([music, speech, hum])
    write_wav(os.path.join(os.path.dirname(__file__), '..', 'audio', 'input.wav'), mixed)
    print("Done. Created: audio/input.wav")


if __name__ == '__main__':
    main()
