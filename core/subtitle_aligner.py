from pathlib import Path
from typing import List, Dict, Any

class SubtitleAligner:
    def __init__(self, font_name: str = "Arial"):
        self.font_name = font_name

    def format_ass_time(self, seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int((seconds - int(seconds)) * 100)
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    def generate_ass_subtitles(self, word_timings: List[Dict[str, Any]], output_path: Path) -> Path:
        """
        Generates an Advanced SubStation Alpha (.ass) subtitle file with
        large rounded text, thick black outline, and bright yellow karaoke emphasis.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: KidsKaraoke,{self.font_name},52,&H0000FFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,5,0,2,100,100,90,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        if not word_timings:
            return output_path

        # Group words into short 4-6 word lines
        chunk_size = 5
        for i in range(0, len(word_timings), chunk_size):
            chunk = word_timings[i:i+chunk_size]
            line_start = chunk[0]["start"]
            line_end = chunk[-1]["end"]
            
            # For each word in chunk, show highlighted word in bright yellow and others in white
            for active_idx, active_word in enumerate(chunk):
                w_start = active_word["start"]
                w_end = active_word["end"]
                
                parts = []
                for w_idx, w in enumerate(chunk):
                    if w_idx == active_idx:
                        # Active word: Yellow and slightly larger bold
                        parts.append(f"{{\\c&H0000FFFF\\b1}}{w['word']}{{\\r}}")
                    else:
                        # Inactive words in current phrase: Crisp white
                        parts.append(f"{{\\c&H00FFFFFF\\b1}}{w['word']}{{\\r}}")
                
                text_line = " ".join(parts)
                events.append(f"Dialogue: 0,{self.format_ass_time(w_start)},{self.format_ass_time(w_end)},KidsKaraoke,,0,0,0,,{text_line}")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(header + "\n".join(events))

        return output_path