import asyncio
import os
import time
from pathlib import Path
from typing import Dict, Any, List
import edge_tts
from config.settings import DEFAULT_VOICE, SECONDARY_VOICE

class VoiceSynthesizer:
    def __init__(self, voice: str = DEFAULT_VOICE):
        self.voice = voice

    async def _synthesize_async(self, text: str, output_path: Path, rate: str = "+0%", pitch: str = "+0Hz") -> Dict[str, Any]:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        last_error = None
        for attempt in range(3):
            try:
                communicate = edge_tts.Communicate(text, self.voice, rate=rate, pitch=pitch)
                audio_data = bytearray()
                sentence_boundaries = []
                
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data.extend(chunk["data"])
                    elif chunk["type"] == "SentenceBoundary":
                        sentence_boundaries.append({
                            "text": chunk["text"],
                            "offset_sec": chunk["offset"] / 1e7,
                            "duration_sec": chunk["duration"] / 1e7
                        })

                with open(output_path, "wb") as f:
                    f.write(audio_data)

                # Compute word timings based on sentence boundaries
                words = text.strip().split()
                total_duration = sentence_boundaries[-1]["offset_sec"] + sentence_boundaries[-1]["duration_sec"] if sentence_boundaries else 3.0
                
                word_timings = []
                start = sentence_boundaries[0]["offset_sec"] if sentence_boundaries else 0.1
                total_chars = sum(len(w) for w in words) or 1
                active_duration = (total_duration - start) * 0.95
                
                curr_time = start
                for w in words:
                    w_dur = max(0.2, (len(w) / total_chars) * active_duration)
                    word_timings.append({
                        "word": w,
                        "start": round(curr_time, 2),
                        "end": round(curr_time + w_dur, 2)
                    })
                    curr_time += w_dur

                return {
                    "file_path": str(output_path),
                    "total_duration": total_duration,
                    "word_timings": word_timings
                }
            except Exception as e:
                last_error = e
                await asyncio.sleep(1.0)
                
        raise RuntimeError(f"Failed to synthesize voice after 3 attempts: {last_error}")

    def synthesize(self, text: str, output_path: Path, rate: str = "+0%", pitch: str = "+0Hz") -> Dict[str, Any]:
        return asyncio.run(self._synthesize_async(text, output_path, rate=rate, pitch=pitch))