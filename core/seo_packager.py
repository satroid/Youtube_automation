import json
from pathlib import Path
from typing import Dict, Any
from core.script_generator import VideoStoryboard

class SEOPackager:
    def package_metadata(self, storyboard: VideoStoryboard, output_path: Path) -> Dict[str, Any]:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 1. High-CTR Title with emojis
        title = f"{storyboard.title} 🐶🐮 | Nursery Rhymes for Toddlers | Kids Songs"
        if len(title) > 100:
            title = title[:97] + "..."

        # 2. Timestamped Chapters
        chapter_lines = ["⏱️ CHAPTERS:"]
        curr_time = 0
        for idx, seg in enumerate(storyboard.segments):
            m = curr_time // 60
            s = curr_time % 60
            chapter_lines.append(f"{m:02d}:{s:02d} - {seg.poem_title}")
            # Approximate each scene at ~4 seconds
            curr_time += len(seg.scenes) * 4
        
        chapters_text = "\n".join(chapter_lines)

        # 3. Full Lyrics
        lyrics_lines = ["🎵 LYRICS TO SING ALONG:"]
        for seg in storyboard.segments:
            lyrics_lines.append(f"\n[{seg.poem_title}]")
            for sc in seg.scenes:
                lyrics_lines.append(f"• {sc.narration}")
        lyrics_text = "\n".join(lyrics_lines)

        # 4. Description
        description = f"""Welcome to our fun, sensory learning adventure for babies and toddlers! 🌟
Sing, bounce, and learn with cute animals, bright colors, and cheerful nursery rhymes.

{chapters_text}

{lyrics_text}

✨ Perfect for: Toddler sensory development, preschool music time, learning animal sounds, and bedtime routines.
👶 Made with love for children ages 1-4.

#nurseryrhymes #kidssongs #toddlerlearning #babysongs #animalsounds #sensoryvideo #preschool
"""

        # 5. Tags (High search intent)
        tags = [
            "nursery rhymes", "kids songs", "toddler sensory video", "baby songs",
            "animal sounds for kids", "cocomelon songs", "super simple songs",
            "toddler learning", "educational videos for toddlers", "rhymes for children",
            "bouncing baby sensory", "kindergarten songs", "preschool learning"
        ]
        # Include custom keywords
        for kw in storyboard.seo_keywords:
            if kw.lower() not in [t.lower() for t in tags]:
                tags.append(kw)

        pack = {
            "title": title,
            "description": description.strip(),
            "tags": tags[:20],
            "category_id": "27", # Education
            "made_for_kids": True,
            "privacy_status": "public"
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(pack, f, indent=2)

        # Also write readable summary
        txt_path = output_path.with_suffix(".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"TITLE:\n{title}\n\nDESCRIPTION:\n{description}\n\nTAGS:\n{', '.join(tags[:20])}\n")

        return pack