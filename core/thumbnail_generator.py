from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from config.settings import OUTPUT_DIR
from core.visual_engine import VisualEngine

class ThumbnailGenerator:
    def __init__(self):
        self.width = 1280
        self.height = 720
        self.visual_engine = VisualEngine()

    def generate_thumbnail(self, title: str, character_name: str, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 1. High saturation radiant background
        canvas = self.visual_engine.create_gradient_canvas((255, 220, 50), (255, 120, 30)).resize((self.width, self.height))
        draw = ImageDraw.Draw(canvas)

        # Starburst background pattern for extreme kid CTR
        cx, cy = self.width // 2, self.height // 2
        import math
        for i in range(16):
            if i % 2 == 0:
                a1 = i * (2 * math.pi / 16)
                a2 = (i + 1) * (2 * math.pi / 16)
                p1 = (cx, cy)
                p2 = (cx + 900 * math.cos(a1), cy + 900 * math.sin(a1))
                p3 = (cx + 900 * math.cos(a2), cy + 900 * math.sin(a2))
                draw.polygon([p1, p2, p3], fill=(255, 235, 90, 180))

        # 2. Add hero character (scaled up, focused on expressive face)
        sprite_file = self.visual_engine.get_sprite_path(character_name)
        if sprite_file.exists():
            sprite = Image.open(sprite_file).convert("RGBA")
            sprite = sprite.resize((540, 540))
            # Paste character on right side with drop shadow
            canvas.paste(sprite, (self.width - 560, self.height - 520), sprite)

        # 3. Big bold text overlay on the left side
        # Extract 2-3 punchy words
        words = [w for w in title.replace("|", " ").replace("-", " ").split() if len(w) > 2][:3]
        headline = " ".join(words).upper() or "KIDS SONGS!"

        # Try to load Arial or default font
        try:
            font = ImageFont.truetype("arialbd.ttf", 85)
        except Exception:
            font = ImageFont.load_default()

        # Render headline with thick black stroke and drop shadow
        tx, ty = 80, 180
        # Shadow
        draw.text((tx + 6, ty + 6), headline, font=font, fill=(20, 20, 20))
        # Stroke outline
        for dx in [-4, 0, 4]:
            for dy in [-4, 0, 4]:
                draw.text((tx + dx, ty + dy), headline, font=font, fill=(0, 0, 0))
        # Top color: bright white/cyan
        draw.text((tx, ty), headline, font=font, fill=(255, 255, 255))

        # Sub-badge: "FUN & DANCE!"
        draw.rounded_rectangle([tx, ty + 120, tx + 420, ty + 200], radius=20, fill=(255, 40, 80), outline=(255, 255, 255), width=4)
        try:
            sub_font = ImageFont.truetype("arialbd.ttf", 44)
        except Exception:
            sub_font = ImageFont.load_default()
        draw.text((tx + 30, ty + 135), "FUN & DANCE!", font=sub_font, fill=(255, 255, 255))

        canvas.save(output_path, "JPEG", quality=92)
        return output_path