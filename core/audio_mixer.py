import numpy as np
from scipy.io import wavfile
from pathlib import Path
from typing import Optional
from config.settings import AUDIO_DIR, DEFAULT_BPM

class AudioAssetManager:
    def __init__(self, audio_dir: Path = AUDIO_DIR):
        self.audio_dir = audio_dir
        self.sample_rate = 44100
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.generate_default_sfx()

    def generate_sfx_boing(self, output_path: Path):
        t = np.linspace(0, 0.4, int(self.sample_rate * 0.4), endpoint=False)
        freq = np.linspace(150, 450, len(t))
        envelope = np.exp(-4 * t)
        wave = np.sin(2 * np.pi * freq * t) * envelope
        wobble = np.sin(2 * np.pi * 15 * t)
        wave = wave * (0.8 + 0.2 * wobble)
        data = (wave * 32767).astype(np.int16)
        wavfile.write(output_path, self.sample_rate, data)

    def generate_sfx_pop(self, output_path: Path):
        t = np.linspace(0, 0.12, int(self.sample_rate * 0.12), endpoint=False)
        freq = np.linspace(700, 150, len(t))
        envelope = np.exp(-25 * t)
        wave = np.sin(2 * np.pi * freq * t) * envelope
        data = (wave * 32767).astype(np.int16)
        wavfile.write(output_path, self.sample_rate, data)

    def generate_sfx_twinkle(self, output_path: Path):
        t = np.linspace(0, 0.6, int(self.sample_rate * 0.6), endpoint=False)
        notes = [1046.5, 1318.5, 1567.98, 2093.0]
        wave = np.zeros_like(t)
        seg = len(t) // len(notes)
        for i, freq in enumerate(notes):
            idx_start = i * seg
            idx_end = (i + 1) * seg
            sub_t = t[idx_start:idx_end] - t[idx_start]
            env = np.exp(-6 * sub_t)
            wave[idx_start:idx_end] = np.sin(2 * np.pi * freq * sub_t) * env
        data = (wave * 32767).astype(np.int16)
        wavfile.write(output_path, self.sample_rate, data)

    def generate_sfx_whoosh(self, output_path: Path):
        t = np.linspace(0, 0.35, int(self.sample_rate * 0.35), endpoint=False)
        noise = np.random.normal(0, 0.5, len(t))
        envelope = np.sin(np.pi * (t / 0.35)) ** 2
        wave = noise * envelope
        data = (wave * 32767).astype(np.int16)
        wavfile.write(output_path, self.sample_rate, data)

    def generate_nursery_melody(self, duration_sec: float, output_path: Path, bpm: int = DEFAULT_BPM):
        total_samples = int(self.sample_rate * duration_sec)
        t = np.linspace(0, duration_sec, total_samples, endpoint=False)
        melody = np.zeros(total_samples, dtype=np.float32)

        scale = {
            'C': 523.25, 'D': 587.33, 'E': 659.25, 'F': 698.46,
            'G': 783.99, 'A': 880.00, 'B': 987.77, 'C6': 1046.50
        }
        notes = ['C', 'C', 'G', 'G', 'A', 'A', 'G', 'F', 'F', 'E', 'E', 'D', 'D', 'C']
        beat_duration = 60.0 / bpm

        current_time = 0.0
        idx = 0
        while current_time < duration_sec:
            note_name = notes[idx % len(notes)]
            freq = scale[note_name]
            note_len = beat_duration * (2 if idx % 7 == 6 else 1)
            start_sample = int(current_time * self.sample_rate)
            end_sample = min(total_samples, int((current_time + note_len) * self.sample_rate))
            
            note_t = t[start_sample:end_sample] - current_time
            envelope = np.exp(-4.5 * note_t)
            tone = (np.sin(2 * np.pi * freq * note_t) * 0.7 + 
                    np.sin(2 * np.pi * freq * 2 * note_t) * 0.3) * envelope
            
            melody[start_sample:end_sample] += tone
            current_time += note_len
            idx += 1

        bass_freqs = [261.63, 349.23, 392.00, 261.63]
        curr_bass_time = 0.0
        b_idx = 0
        while curr_bass_time < duration_sec:
            bfreq = bass_freqs[b_idx % len(bass_freqs)]
            start_s = int(curr_bass_time * self.sample_rate)
            end_s = min(total_samples, int((curr_bass_time + beat_duration) * self.sample_rate))
            bt = t[start_s:end_s] - curr_bass_time
            benv = np.exp(-3.0 * bt)
            bass_tone = np.sin(2 * np.pi * bfreq * bt) * benv * 0.35
            melody[start_s:end_s] += bass_tone
            curr_bass_time += beat_duration
            b_idx += 1

        max_val = np.max(np.abs(melody)) or 1.0
        melody = (melody / max_val) * 0.38
        data = (melody * 32767).astype(np.int16)
        wavfile.write(output_path, self.sample_rate, data)

    def generate_default_sfx(self):
        sfx_map = {
            "boing.wav": self.generate_sfx_boing,
            "pop.wav": self.generate_sfx_pop,
            "twinkle.wav": self.generate_sfx_twinkle,
            "whoosh.wav": self.generate_sfx_whoosh
        }
        for name, gen_fn in sfx_map.items():
            path = self.audio_dir / name
            if not path.exists():
                gen_fn(path)

    def get_sfx_path(self, effect_name: str) -> Optional[Path]:
        clean_name = effect_name.lower()
        if "boing" in clean_name:
            return self.audio_dir / "boing.wav"
        elif "pop" in clean_name:
            return self.audio_dir / "pop.wav"
        elif "giggle" in clean_name or "twinkle" in clean_name or "star" in clean_name:
            return self.audio_dir / "twinkle.wav"
        elif "whoosh" in clean_name:
            return self.audio_dir / "whoosh.wav"
        return self.audio_dir / "pop.wav"