import subprocess
import shutil
from pathlib import Path
from typing import List
from config.settings import FFMPEG_EXE, OUTPUT_DIR, DEFAULT_BPM
from core.script_generator import VideoStoryboard, SceneCue
from core.visual_engine import VisualEngine
from core.voice_synthesizer import VoiceSynthesizer
from core.subtitle_aligner import SubtitleAligner
from core.audio_mixer import AudioAssetManager

class VideoRenderer:
    def __init__(self):
        self.visual_engine = VisualEngine()
        self.voice_synthesizer = VoiceSynthesizer()
        self.subtitle_aligner = SubtitleAligner()
        self.audio_manager = AudioAssetManager()

    def _escape_path(self, path: Path) -> str:
        return str(path.resolve()).replace("\\", "/").replace(":", "\\:")

    def render_scene(
        self,
        scene: SceneCue,
        bg_path: Path,
        sprite_path: Path,
        voice_path: Path,
        melody_path: Path,
        sfx_path: Path,
        sub_path: Path,
        output_clip: Path,
        bpm: int = DEFAULT_BPM
    ) -> bool:
        freq = bpm / 60.0
        action = scene.action.lower()

        # Motion formula for character sprite
        if "spin" in action or "dance" in action:
            motion_expr = f"x=(W-w)/2+sin(2*PI*{freq}*t)*70:y=(H-h)/2+60-abs(sin(2*PI*{freq}*t))*70"
        elif "peekaboo" in action:
            motion_expr = f"x=(W-w)/2:y=(H-h)/2+60+max(0\\,350*exp(-2.2*t)-abs(sin(2*PI*{freq}*t))*50)"
        else:
            # Default energetic toddler bounce
            motion_expr = f"x=(W-w)/2:y=(H-h)/2+70-abs(sin(2*PI*{freq}*t))*85"

        sub_escaped = self._escape_path(sub_path)
        
        # FFmpeg filter complex:
        # 1. Scale sprite to 520x520
        # 2. Overlay sprite onto background with motion
        # 3. Burn styled subtitles
        # 4. Mix voice + ducked melody + SFX
        filter_str = (
            f"[1:v]scale=520:520[sp];"
            f"[0:v][sp]overlay={motion_expr}:shortest=1[comp];"
            f"[comp]subtitles='{sub_escaped}'[v];"
            f"[2:a]volume=1.0[v_aud];"
            f"[3:a]volume=0.18[m_aud];"
            f"[4:a]adelay=150|150,volume=0.55[s_aud];"
            f"[v_aud][m_aud][s_aud]amix=inputs=3:duration=first:dropout_transition=2[a]"
        )

        cmd = [
            FFMPEG_EXE, "-y",
            "-loop", "1", "-i", str(bg_path.resolve()),
            "-loop", "1", "-i", str(sprite_path.resolve()),
            "-i", str(voice_path.resolve()),
            "-stream_loop", "-1", "-i", str(melody_path.resolve()),
            "-i", str(sfx_path.resolve()),
            "-filter_complex", filter_str,
            "-map", "[v]",
            "-map", "[a]",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(output_clip.resolve())
        ]

        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"[Error] Rendering scene {scene.scene_id} failed:\n{res.stderr[-400:]}")
            return False
        return True

    def assemble_storyboard(self, storyboard: VideoStoryboard, final_output_path: Path) -> Path:
        temp_dir = OUTPUT_DIR / f"temp_{storyboard.video_id}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        final_output_path.parent.mkdir(parents=True, exist_ok=True)

        clip_files: List[Path] = []
        global_scene_idx = 1

        print(f"[*] Beginning assembly for '{storyboard.title}'...")

        for seg_idx, segment in enumerate(storyboard.segments):
            print(f"[*] Processing Segment {seg_idx+1}: {segment.poem_title} (BPM: {segment.target_bpm})")
            
            # Generate shared melody for this segment
            seg_melody = temp_dir / f"melody_seg_{seg_idx}.wav"
            self.audio_manager.generate_nursery_melody(60.0, seg_melody, bpm=segment.target_bpm)

            for scene in segment.scenes:
                scene_prefix = f"s_{global_scene_idx}"
                print(f"  [-] Scene {global_scene_idx}: {scene.character} ({scene.action}) -> '{scene.narration}'")

                # 1. Voice narration & word timestamps
                voice_file = temp_dir / f"{scene_prefix}_voice.mp3"
                voice_data = self.voice_synthesizer.synthesize(scene.narration, voice_file)

                # 2. Subtitle file
                sub_file = temp_dir / f"{scene_prefix}_sub.ass"
                self.subtitle_aligner.generate_ass_subtitles(voice_data["word_timings"], sub_file)

                # 3. Background canvas
                bg_img = self.visual_engine.generate_background(scene.background_theme)
                bg_file = temp_dir / f"{scene_prefix}_bg.png"
                bg_img.save(bg_file)

                # 4. Sprite
                sprite_file = self.visual_engine.get_sprite_path(scene.character)

                # 5. SFX
                sfx_file = self.audio_manager.get_sfx_path(scene.sound_effect)

                # 6. Render individual scene clip
                clip_path = temp_dir / f"{scene_prefix}_clip.mp4"
                success = self.render_scene(
                    scene=scene,
                    bg_path=bg_file,
                    sprite_path=sprite_file,
                    voice_path=voice_file,
                    melody_path=seg_melody,
                    sfx_path=sfx_file,
                    sub_path=sub_file,
                    output_clip=clip_path,
                    bpm=segment.target_bpm
                )
                if success:
                    clip_files.append(clip_path)
                global_scene_idx += 1

        # Concatenate all rendered scenes into final video
        if not clip_files:
            raise RuntimeError("No scene clips were generated successfully.")

        concat_txt = temp_dir / "concat_list.txt"
        with open(concat_txt, "w", encoding="utf-8") as f:
            for c in clip_files:
                f.write(f"file '{c.resolve().as_posix()}'\n")

        print("[*] Concatenating scenes into final video...")
        concat_cmd = [
            FFMPEG_EXE, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_txt.resolve()),
            "-c", "copy",
            str(final_output_path.resolve())
        ]
        res = subprocess.run(concat_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg concatenation failed:\n{res.stderr[-400:]}")

        print(f"[+] Final Video Ready at: {final_output_path} ({final_output_path.stat().st_size} bytes)")
        
        # Cleanup temporary files
        shutil.rmtree(temp_dir, ignore_errors=True)
        return final_output_path