from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import math
from typing import Tuple
from config.settings import SPRITES_DIR, VIDEO_WIDTH, VIDEO_HEIGHT

class VisualEngine:
    def __init__(self, sprites_dir: Path = SPRITES_DIR):
        self.sprites_dir = sprites_dir
        self.sprites_dir.mkdir(parents=True, exist_ok=True)
        self.ensure_default_sprites()

    def create_gradient_canvas(self, top_color: Tuple[int, int, int], bottom_color: Tuple[int, int, int]) -> Image.Image:
        base = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), top_color)
        top_img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), top_color)
        bottom_img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), bottom_color)
        mask = Image.linear_gradient("L").resize((VIDEO_WIDTH, VIDEO_HEIGHT))
        return Image.composite(bottom_img, top_img, mask)

    def generate_background(self, theme: str) -> Image.Image:
        theme = theme.lower()
        if "sunny" in theme or "sky" in theme:
            bg = self.create_gradient_canvas((100, 200, 255), (210, 245, 255))
            draw = ImageDraw.Draw(bg)
            # Big happy sun in top-right
            draw.ellipse([VIDEO_WIDTH - 300, -100, VIDEO_WIDTH + 100, 300], fill=(255, 230, 80))
            draw.ellipse([VIDEO_WIDTH - 270, -70, VIDEO_WIDTH + 70, 270], fill=(255, 245, 140))
            # Fluffy cartoon clouds
            for cx, cy in [(200, 150), (600, 220), (1200, 140), (1600, 200)]:
                draw.ellipse([cx, cy, cx + 180, cy + 90], fill=(255, 255, 255, 240))
                draw.ellipse([cx + 50, cy - 40, cx + 220, cy + 80], fill=(255, 255, 255, 240))
                draw.ellipse([cx + 120, cy, cx + 280, cy + 90], fill=(255, 255, 255, 240))
            # Rolling green hills at bottom
            draw.chord([-200, VIDEO_HEIGHT - 350, VIDEO_WIDTH // 2 + 200, VIDEO_HEIGHT + 300], 180, 360, fill=(120, 210, 80))
            draw.chord([VIDEO_WIDTH // 3, VIDEO_HEIGHT - 320, VIDEO_WIDTH + 300, VIDEO_HEIGHT + 300], 180, 360, fill=(95, 190, 60))
            return bg

        elif "star" in theme or "night" in theme:
            bg = self.create_gradient_canvas((20, 15, 55), (60, 40, 110))
            draw = ImageDraw.Draw(bg)
            # Glowing crescent moon
            draw.ellipse([150, 100, 320, 270], fill=(255, 245, 150))
            draw.ellipse([190, 80, 350, 250], fill=(22, 17, 58))
            # Twinkling stars
            import random
            rng = random.Random(42)
            for _ in range(70):
                sx = rng.randint(50, VIDEO_WIDTH - 50)
                sy = rng.randint(40, VIDEO_HEIGHT - 100)
                sr = rng.randint(3, 8)
                draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 255, 220))
            return bg

        elif "bubble" in theme or "rainbow" in theme or "meadow" in theme:
            bg = self.create_gradient_canvas((255, 180, 210), (170, 230, 255))
            draw = ImageDraw.Draw(bg)
            # Floating sensory pastel bubbles
            import random
            rng = random.Random(99)
            colors = [(255, 255, 255, 120), (255, 230, 150, 140), (180, 240, 255, 130), (230, 190, 255, 140)]
            for _ in range(25):
                bx = rng.randint(60, VIDEO_WIDTH - 60)
                by = rng.randint(60, VIDEO_HEIGHT - 60)
                br = rng.randint(35, 90)
                c = colors[rng.randint(0, len(colors) - 1)]
                draw.ellipse([bx - br, by - br, bx + br, by + br], outline=(255, 255, 255), width=4)
                draw.ellipse([bx - br + 10, by - br + 10, bx - br // 2, by - br // 2], fill=(255, 255, 255, 180))
            return bg

        # Default cheerful pastel
        return self.create_gradient_canvas((130, 210, 255), (255, 220, 240))

    def _draw_cartoon_eyes(self, draw: ImageDraw.Draw, lx: int, ly: int, rx: int, ry: int, size: int = 40):
        for cx, cy in [(lx, ly), (rx, ry)]:
            # Sclera
            draw.ellipse([cx - size, cy - size, cx + size, cy + size], fill=(255, 255, 255), outline=(40, 30, 30), width=4)
            # Pupil
            draw.ellipse([cx - size // 2, cy - size // 2, cx + size // 2, cy + size // 2], fill=(30, 25, 25))
            # Catchlight sparkle
            draw.ellipse([cx - size // 3, cy - size // 2, cx - size // 8, cy - size // 4], fill=(255, 255, 255))
            draw.ellipse([cx + size // 6, cy + size // 6, cx + size // 3, cy + size // 3], fill=(255, 255, 255))

    def _draw_rosy_cheeks(self, draw: ImageDraw.Draw, lx: int, ly: int, rx: int, ry: int, r: int = 25):
        for cx, cy in [(lx, ly), (rx, ry)]:
            draw.ellipse([cx - r, cy - r // 2, cx + r, cy + r // 2], fill=(255, 130, 140, 160))

    def generate_puppy_sprite(self, path: Path):
        img = Image.new("RGBA", (600, 600), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Floppy ears behind head
        draw.chord([80, 120, 260, 420], 90, 270, fill=(180, 110, 50), outline=(80, 45, 20), width=6)
        draw.chord([340, 120, 520, 420], 270, 90, fill=(180, 110, 50), outline=(80, 45, 20), width=6)
        # Head
        draw.ellipse([130, 110, 470, 450], fill=(245, 185, 110), outline=(80, 45, 20), width=8)
        # Snout
        draw.ellipse([210, 250, 390, 390], fill=(255, 235, 200), outline=(80, 45, 20), width=6)
        # Eyes & Cheeks
        self._draw_cartoon_eyes(draw, 220, 220, 380, 220, size=35)
        self._draw_rosy_cheeks(draw, 180, 300, 420, 300, r=30)
        # Cute black nose
        draw.ellipse([275, 280, 325, 320], fill=(40, 30, 30))
        # Happy smiling mouth with tongue
        draw.arc([250, 310, 350, 380], 10, 170, fill=(60, 30, 20), width=6)
        draw.chord([280, 345, 320, 385], 0, 180, fill=(255, 100, 130))
        img.save(path, "PNG")

    def generate_duck_sprite(self, path: Path):
        img = Image.new("RGBA", (600, 600), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Body
        draw.ellipse([140, 220, 480, 520], fill=(255, 220, 40), outline=(180, 130, 20), width=8)
        # Wing
        draw.chord([180, 280, 340, 460], 45, 225, fill=(255, 200, 20), outline=(180, 130, 20), width=6)
        # Head
        draw.ellipse([200, 100, 460, 360], fill=(255, 225, 50), outline=(180, 130, 20), width=8)
        # Eyes
        self._draw_cartoon_eyes(draw, 280, 200, 400, 200, size=30)
        self._draw_rosy_cheeks(draw, 250, 260, 420, 260, r=22)
        # Orange beak
        draw.polygon([(340, 230), (490, 255), (340, 285)], fill=(255, 120, 30), outline=(180, 80, 10))
        img.save(path, "PNG")

    def generate_cow_sprite(self, path: Path):
        img = Image.new("RGBA", (600, 600), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Horns
        draw.polygon([(160, 140), (120, 80), (200, 110)], fill=(230, 200, 120), outline=(80, 60, 30), width=4)
        draw.polygon([(440, 140), (480, 80), (400, 110)], fill=(230, 200, 120), outline=(80, 60, 30), width=4)
        # Head
        draw.ellipse([130, 110, 470, 450], fill=(250, 250, 250), outline=(40, 40, 40), width=8)
        # Black spot on forehead
        draw.chord([140, 115, 270, 250], 90, 360, fill=(45, 45, 55))
        # Snout
        draw.ellipse([180, 270, 420, 410], fill=(255, 190, 200), outline=(50, 40, 40), width=6)
        # Nostrils
        draw.ellipse([240, 320, 270, 360], fill=(60, 40, 50))
        draw.ellipse([330, 320, 360, 360], fill=(60, 40, 50))
        # Eyes
        self._draw_cartoon_eyes(draw, 220, 200, 380, 200, size=32)
        self._draw_rosy_cheeks(draw, 160, 280, 440, 280, r=26)
        img.save(path, "PNG")

    def generate_star_sprite(self, path: Path):
        img = Image.new("RGBA", (600, 600), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Draw 5-pointed star
        center = (300, 300)
        outer_r, inner_r = 230, 105
        pts = []
        for i in range(10):
            r = outer_r if i % 2 == 0 else inner_r
            angle = -math.pi / 2 + i * (math.pi / 5)
            pts.append((center[0] + r * math.cos(angle), center[1] + r * math.sin(angle)))
        draw.polygon(pts, fill=(255, 235, 60), outline=(210, 170, 20), width=10)
        # Big smiling eyes in center
        self._draw_cartoon_eyes(draw, 240, 280, 360, 280, size=28)
        self._draw_rosy_cheeks(draw, 210, 340, 390, 340, r=25)
        # Smile
        draw.arc([260, 320, 340, 380], 20, 160, fill=(60, 40, 20), width=6)
        img.save(path, "PNG")

    def ensure_default_sprites(self):
        sprites = {
            "happy_puppy.png": self.generate_puppy_sprite,
            "cute_duck.png": self.generate_duck_sprite,
            "dancing_cow.png": self.generate_cow_sprite,
            "smiling_star.png": self.generate_star_sprite,
        }
        for filename, fn in sprites.items():
            target = self.sprites_dir / filename
            if not target.exists():
                fn(target)

    def get_sprite_path(self, character_name: str) -> Path:
        char = character_name.lower()
        if "duck" in char:
            return self.sprites_dir / "cute_duck.png"
        elif "cow" in char:
            return self.sprites_dir / "dancing_cow.png"
        elif "star" in char or "sun" in char:
            return self.sprites_dir / "smiling_star.png"
        return self.sprites_dir / "happy_puppy.png"