# Autonomous YouTube Kids Automation Service (Zero-Cost Studio)

An autonomous, zero-cost pipeline for generating high-retention Kids' Nursery Rhymes & Sensory Animation Videos (ages 1–4) with AI scripting, neural voiceover, beat-synced rhythm motion, animated karaoke subtitles, high-CTR thumbnails, and a closed-loop retention feedback engine.

---

## Key Features

1. **Zero-Cost Operation:** 
   - **Google Gemini 2.5 Flash** (Free Tier via Google AI Studio) for scriptwriting, pacing, and retention critique.
   - **Microsoft Edge Neural Voices** (`edge-tts`) for warm, child-friendly narration (`en-US-AnaNeural`, `en-US-EmmaNeural`).
   - **Procedural Sound Effects & Music:** Mathematically tuned glockenspiel nursery melodies and cartoon sound effects (boings, pops, whooshes, giggles) with zero copyright issues.
   - **Bundled FFmpeg:** Automatic FFmpeg 7.1 binary included via `imageio-ffmpeg` — no system path configuration or manual installation needed.
2. **2.5D Sensory Rhythm Engine:**
   - Animated character bobs and scales synchronized to music tempo ($y = y_0 - h \cdot |\sin(2\pi \cdot \text{BPM}/60 \cdot t)|$).
   - High-contrast radiant backgrounds (sunny sky, rainbow meadow, starry night, bubble party).
   - Word-by-word karaoke subtitles in bright yellow and white with thick cartoon outlines.
3. **Closed-Loop Retention Feedback (Self-Optimization):**
   - Stores performance history in `data/channel_memory.db` (SQLite).
   - Critic Agent diagnoses drop-off points (0:15s, 1:00m, 3:00m, and CTR).
   - Automatically writes corrective rules that are dynamically injected into future Gemini prompts.

---

## Project Structure

```
kids_youtube_automation/
├── config/
│   └── settings.py          # Global paths, voice choices, FFmpeg resolution, IPv4 patch
├── core/
│   ├── script_generator.py  # Gemini prompt orchestrator with feedback rule injection
│   ├── voice_synthesizer.py # edge-tts neural voice synthesizer with retry logic
│   ├── subtitle_aligner.py  # Word-level karaoke .ass subtitle generator
│   ├── visual_engine.py     # High-saturation backgrounds & cute cartoon vector sprites
│   ├── audio_mixer.py       # Procedural nursery melody & SFX generator
│   ├── video_renderer.py    # FFmpeg beat-synced motion & assembly engine
│   ├── thumbnail_generator.py # High-CTR 1280x720 radiant thumbnail builder
│   ├── seo_packager.py      # Title, description, chapters, and tags generator
│   ├── youtube_client.py    # YouTube Data API upload & Analytics API client
│   └── feedback_critic.py   # Drop-off analysis & prompt mutation agent
├── assets/
│   ├── sprites/             # Transparent PNG character sprites
│   └── audio/               # Background tracks & SFX (.wav)
├── data/
│   └── channel_memory.db    # SQLite memory of videos and learned rules
├── output/                  # Generated MP4 videos, thumbnails, and SEO packages
├── tests/
│   └── test_pipeline.py     # Automated unit test suite
└── main.py                  # CLI entry point
```

---

## Quick Start & Usage

### 1. Activate Environment
```powershell
Set-Location "C:\Users\satya\.gemini\antigravity\scratch\kids_youtube_automation"
.\.venv\Scripts\Activate.ps1
```

### 2. Configure Free Gemini API Key (Optional but Recommended)
Create a `.env` file in the project root:
```env
GEMINI_API_KEY="your-gemini-api-key-here"
```
*(Get a free key in 30 seconds at [aistudio.google.com](https://aistudio.google.com/)). If omitted, the service uses an intelligent built-in nursery rhyme generator.*

### 3. CLI Commands

#### Generate Full Video, Thumbnail & SEO Package:
```bash
python main.py create --topic "Dancing Animals & Sounds" --duration 2
```

#### Render a Quick 30-Second Demonstration:
```bash
python main.py render-sample
```

#### Run Analytics Feedback & Retention Critic:
```bash
python main.py analyze --video-id sample_kids_001
```

#### View Active Learned Retention Rules:
```bash
python main.py rules
```

#### Run Automated Test Suite:
```bash
python -m unittest tests/test_pipeline.py
```