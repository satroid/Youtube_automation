import json
import os
from typing import List, Optional
from pydantic import BaseModel, Field
from config.settings import GEMINI_API_KEY
from core.feedback_critic import DatabaseManager, CriticAgent

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

class SceneCue(BaseModel):
    scene_id: int
    character: str = Field(description="Primary character or object, e.g., 'dancing_apple', 'happy_puppy', 'smiling_sun'")
    action: str = Field(description="Motion type: 'bounce', 'spin', 'wave', 'zoom_in', 'peekaboo'")
    background_theme: str = Field(description="Vibrant theme: 'sunny_sky', 'rainbow_meadow', 'starry_night', 'bubble_party'")
    narration: str = Field(description="The rhythmic rhyming line spoken in this 3-5 second clip")
    sound_effect: str = Field(description="Fun sound FX: 'boing', 'pop', 'giggle', 'whoosh', 'animal_sound'")
    interactive_prompt: Optional[str] = Field(default=None, description="Callout for toddler, e.g. 'Can you jump like the bunny?'")

class PoemSegment(BaseModel):
    poem_title: str
    target_bpm: int = 115
    scenes: List[SceneCue]

class VideoStoryboard(BaseModel):
    video_id: str
    title: str
    seo_keywords: List[str]
    target_age_group: str = "1-4 years"
    estimated_duration_sec: int
    segments: List[PoemSegment]

class ScriptGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.critic = CriticAgent(DatabaseManager())
        if genai and self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def generate_storyboard(self, topic: str, target_minutes: int = 2) -> VideoStoryboard:
        retention_rules = self.critic.format_rules_for_prompt()
        
        system_instructions = (
            "You are an expert YouTube Kids content creator and nursery rhyme composer specializing in toddler retention (ages 1-4).\n"
            "Your goal is to create a rhythmic, engaging, sensory-rich video storyboard.\n\n"
            "MANDATORY RETENTION RULES FROM CHANNEL PERFORMANCE:\n" + retention_rules + "\n\n"
            "PACING REQUIREMENTS:\n"
            "1. Every scene must be short: 3 to 4 seconds of narration.\n"
            "2. Every scene MUST have a clear character, a motion action ('bounce', 'spin', 'zoom_in', 'peekaboo'), and a fun SFX ('boing', 'pop', 'giggle').\n"
            "3. Include an interactive question for the toddler every 4 scenes ('Can you clap your hands?', 'Where is the red apple?').\n"
            "4. The rhyme meter must be bouncy and strictly rhythmic (AABB or ABAB).\n"
            "5. Output pure structured JSON matching the VideoStoryboard schema.\n"
        )

        user_prompt = f"Create a {target_minutes}-minute toddler compilation storyboard on the theme: '{topic}'. Include 2 distinct connected mini-poems/rhymes in the compilation."

        if self.client:
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instructions,
                        response_mime_type="application/json",
                        response_schema=VideoStoryboard,
                        temperature=0.7
                    )
                )
                data = json.loads(response.text)
                return VideoStoryboard.model_validate(data)
            except Exception as e:
                print(f"[Warning] Gemini API call encountered error: {e}. Using intelligent fallback storyboard.")

        return self._get_fallback_storyboard(topic)

    def _get_fallback_storyboard(self, topic: str) -> VideoStoryboard:
        return VideoStoryboard(
            video_id="sample_kids_001",
            title=f"{topic} | Fun Nursery Rhymes for Toddlers",
            seo_keywords=["nursery rhymes", "toddler sensory video", "kids songs", "animals for kids", "learning sounds"],
            target_age_group="1-4 years",
            estimated_duration_sec=60,
            segments=[
                PoemSegment(
                    poem_title="The Bouncing Farm Animals",
                    target_bpm=120,
                    scenes=[
                        SceneCue(
                            scene_id=1,
                            character="happy_puppy",
                            action="bounce",
                            background_theme="sunny_sky",
                            narration="The happy little puppy goes woof, woof, woof!",
                            sound_effect="boing",
                            interactive_prompt="Can you bark like a puppy?"
                        ),
                        SceneCue(
                            scene_id=2,
                            character="dancing_cow",
                            action="spin",
                            background_theme="rainbow_meadow",
                            narration="The friendly spotted cow goes moo on the roof!",
                            sound_effect="pop",
                            interactive_prompt=None
                        ),
                        SceneCue(
                            scene_id=3,
                            character="cute_duck",
                            action="zoom_in",
                            background_theme="sunny_sky",
                            narration="The tiny yellow duckling says quack, quack, quack!",
                            sound_effect="giggle",
                            interactive_prompt="Where is the yellow duck?"
                        ),
                        SceneCue(
                            scene_id=4,
                            character="smiling_star",
                            action="peekaboo",
                            background_theme="starry_night",
                            narration="And all the happy friends come bouncing right back!",
                            sound_effect="whoosh",
                            interactive_prompt="Clap your hands with the star!"
                        )
                    ]
                )
            ]
        )