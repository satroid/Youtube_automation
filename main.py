import argparse
import sys
from pathlib import Path
from datetime import datetime

# UTF-8 stdout configuration for Windows console
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config.settings import OUTPUT_DIR, DB_PATH
from core.script_generator import ScriptGenerator
from core.video_renderer import VideoRenderer
from core.thumbnail_generator import ThumbnailGenerator
from core.seo_packager import SEOPackager
from core.youtube_client import YouTubeClient
from core.feedback_critic import DatabaseManager, CriticAgent

def cmd_create(args):
    print("=" * 65)
    print(f"🎬 [KIDS YOUTUBE STUDIO] GENERATING: '{args.topic}'")
    print("=" * 65)

    db = DatabaseManager()
    script_gen = ScriptGenerator()
    renderer = VideoRenderer()
    thumb_gen = ThumbnailGenerator()
    seo_gen = SEOPackager()
    yt_client = YouTubeClient()

    # 1. Script Generation with Feedback Injection
    print("\n[Step 1/5] 🧠 Generating Storyboard with Gemini (Retention Rules Injected)...")
    storyboard = script_gen.generate_storyboard(args.topic, target_minutes=args.duration)
    print(f"  [+] Title: {storyboard.title}")
    print(f"  [+] Segments: {len(storyboard.segments)}")
    total_scenes = sum(len(s.scenes) for s in storyboard.segments)
    print(f"  [+] Total Scenes: {total_scenes}")

    # 2. Render Full 1080p Video
    print("\n[Step 2/5] 🎨 Rendering 1080p Sensory Video (Beat-Synced Rhythm Motion)...")
    video_filename = f"{storyboard.video_id}_video.mp4"
    video_path = OUTPUT_DIR / video_filename
    renderer.assemble_storyboard(storyboard, video_path)

    # 3. High-CTR Thumbnail
    print("\n[Step 3/5] 🖼️ Creating High-CTR Radiant Thumbnail...")
    thumb_filename = f"{storyboard.video_id}_thumb.jpg"
    thumb_path = OUTPUT_DIR / thumb_filename
    hero_character = storyboard.segments[0].scenes[0].character if storyboard.segments and storyboard.segments[0].scenes else "happy_puppy"
    thumb_gen.generate_thumbnail(storyboard.title, hero_character, thumb_path)
    print(f"  [+] Thumbnail saved at: {thumb_path}")

    # 4. SEO Packaging
    print("\n[Step 4/5] 📦 Generating YouTube SEO & Chapters Package...")
    seo_path = OUTPUT_DIR / f"{storyboard.video_id}_seo.json"
    metadata = seo_gen.package_metadata(storyboard, seo_path)
    print(f"  [+] SEO metadata saved at: {seo_path}")

    # 5. Database Tracking & Optional Upload
    print("\n[Step 5/5] 📊 Registering Video in Self-Correction Database...")
    duration_sec = total_scenes * 4.0
    db.add_video(storyboard.video_id, storyboard.title, args.topic, duration_sec)

    if args.upload:
        print("\n🚀 Initiating YouTube Upload...")
        yt_id = yt_client.upload_video(video_path, thumb_path, metadata)
        with db.get_connection() as conn:
            conn.cursor().execute("UPDATE videos SET youtube_id = ? WHERE video_id = ?", (yt_id, storyboard.video_id))
            conn.commit()

    print("\n" + "=" * 65)
    print("✅ PRODUCTION COMPLETE!")
    print(f"📁 Video:     {video_path}")
    print(f"🖼️ Thumbnail: {thumb_path}")
    print(f"📝 Metadata:  {seo_path.with_suffix('.txt')}")
    print("=" * 65)

def cmd_sample(args):
    print("🎬 Rendering quick 30-second sensory demonstration...")
    script_gen = ScriptGenerator()
    renderer = VideoRenderer()
    thumb_gen = ThumbnailGenerator()
    seo_gen = SEOPackager()

    sb = script_gen._get_fallback_storyboard("Dancing Animals & Sounds")
    out_video = OUTPUT_DIR / "demo_sample_video.mp4"
    out_thumb = OUTPUT_DIR / "demo_sample_thumb.jpg"
    out_seo = OUTPUT_DIR / "demo_sample_seo.json"

    renderer.assemble_storyboard(sb, out_video)
    thumb_gen.generate_thumbnail(sb.title, "happy_puppy", out_thumb)
    seo_gen.package_metadata(sb, out_seo)

    print(f"\n✅ Demonstration ready at:\n  Video: {out_video}\n  Thumbnail: {out_thumb}")

def cmd_analyze(args):
    db = DatabaseManager()
    critic = CriticAgent(db)
    yt_client = YouTubeClient()

    print(f"\n🔍 Analyzing retention metrics for video: '{args.video_id}'...")
    stats = yt_client.fetch_retention_and_stats(args.video_id)
    
    if not stats:
        print("[-] No stats could be retrieved.")
        return

    print(f"  [+] Views:          {stats.get('views', 0):,}")
    print(f"  [+] CTR:            {stats.get('ctr', 0)*100:.1f}%")
    print(f"  [+] Retention @15s: {stats.get('retention_15s', 0)*100:.1f}%")
    print(f"  [+] Retention @1m:  {stats.get('retention_1m', 0)*100:.1f}%")
    print(f"  [+] Retention @3m:  {stats.get('retention_3m', 0)*100:.1f}%")

    db.update_metrics(
        video_id=args.video_id,
        ctr=stats.get("ctr", 0.0),
        ret_15s=stats.get("retention_15s", 0.0),
        ret_1m=stats.get("retention_1m", 0.0),
        ret_3m=stats.get("retention_3m", 0.0),
        ret_end=stats.get("retention_end", 0.0),
        views=stats.get("views", 0)
    )

    print("\n🧠 Critic Agent evaluating retention performance...")
    critique = critic.analyze_video_retention(args.video_id)
    for c in critique:
        print(f"  💡 {c}")
    print("\n[+] Updated rules successfully written to channel_memory.db!")

def cmd_rules(args):
    db = DatabaseManager()
    critic = CriticAgent(db)
    print("\n" + "=" * 60)
    print("🧠 ACTIVE CHANNEL RETENTION RULES (Injected into Script Prompts):")
    print("=" * 60)
    print(critic.format_rules_for_prompt())
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Autonomous YouTube Kids Video Studio")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Create command
    create_parser = subparsers.add_parser("create", help="Generate full video, thumbnail, and SEO package")
    create_parser.add_argument("--topic", type=str, default="Happy Farm Animals & Sounds", help="Theme or topic")
    create_parser.add_argument("--duration", type=int, default=2, help="Target duration in minutes")
    create_parser.add_argument("--upload", action="store_true", help="Upload directly to YouTube")
    create_parser.set_defaults(func=cmd_create)

    # Sample command
    sample_parser = subparsers.add_parser("render-sample", help="Render quick demonstration video")
    sample_parser.set_defaults(func=cmd_sample)

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze video retention and adapt prompt rules")
    analyze_parser.add_argument("--video-id", type=str, required=True, help="Video ID to analyze")
    analyze_parser.set_defaults(func=cmd_analyze)

    # Rules command
    rules_parser = subparsers.add_parser("rules", help="Display all active retention rules")
    rules_parser.set_defaults(func=cmd_rules)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()