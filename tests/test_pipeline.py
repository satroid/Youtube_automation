import unittest
from pathlib import Path
from core.feedback_critic import DatabaseManager, CriticAgent
from core.script_generator import ScriptGenerator
from core.visual_engine import VisualEngine
from core.subtitle_aligner import SubtitleAligner
from core.seo_packager import SEOPackager
from core.thumbnail_generator import ThumbnailGenerator
from config.settings import OUTPUT_DIR

class TestKidsAutomationPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = DatabaseManager()
        cls.critic = CriticAgent(cls.db)
        cls.script_gen = ScriptGenerator()
        cls.visual_engine = VisualEngine()
        cls.sub_aligner = SubtitleAligner()
        cls.seo_packager = SEOPackager()
        cls.thumb_gen = ThumbnailGenerator()

    def test_database_and_rules(self):
        rules = self.db.get_all_rules()
        self.assertGreater(len(rules), 0)
        formatted = self.critic.format_rules_for_prompt()
        self.assertIn("[", formatted)

    def test_script_storyboard_generation(self):
        sb = self.script_gen.generate_storyboard("Farm Animals")
        self.assertIsNotNone(sb.title)
        self.assertGreater(len(sb.segments), 0)
        self.assertGreater(len(sb.segments[0].scenes), 0)

    def test_visual_engine_sprites(self):
        puppy_path = self.visual_engine.get_sprite_path("happy_puppy")
        self.assertTrue(puppy_path.exists())
        bg = self.visual_engine.generate_background("sunny_sky")
        self.assertEqual(bg.size, (1920, 1080))

    def test_subtitle_aligner(self):
        words = [{"word": "Hello", "start": 0.0, "end": 0.5}]
        out_sub = OUTPUT_DIR / "unit_test_sub.ass"
        res = self.sub_aligner.generate_ass_subtitles(words, out_sub)
        self.assertTrue(res.exists())

    def test_seo_packager(self):
        sb = self.script_gen._get_fallback_storyboard("Puppies & Stars")
        out_seo = OUTPUT_DIR / "unit_test_seo.json"
        pack = self.seo_packager.package_metadata(sb, out_seo)
        self.assertTrue(out_seo.exists())
        self.assertIn("title", pack)
        self.assertTrue(pack["made_for_kids"])

    def test_thumbnail_generator(self):
        out_thumb = OUTPUT_DIR / "unit_test_thumb.jpg"
        res = self.thumb_gen.generate_thumbnail("Dancing Animals", "happy_puppy", out_thumb)
        self.assertTrue(res.exists())
        self.assertGreater(res.stat().st_size, 10000)

if __name__ == "__main__":
    unittest.main()