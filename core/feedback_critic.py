import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from config.settings import DB_PATH, GEMINI_API_KEY
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

class DatabaseManager:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS videos (
                    video_id TEXT PRIMARY KEY,
                    youtube_id TEXT,
                    title TEXT,
                    topic TEXT,
                    duration_sec REAL,
                    published_at TIMESTAMP,
                    ctr REAL DEFAULT 0.0,
                    retention_15s REAL DEFAULT 0.0,
                    retention_1m REAL DEFAULT 0.0,
                    retention_3m REAL DEFAULT 0.0,
                    retention_end REAL DEFAULT 0.0,
                    avg_view_duration_sec REAL DEFAULT 0.0,
                    total_views INTEGER DEFAULT 0,
                    analyzed INTEGER DEFAULT 0
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS retention_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    rule_text TEXT,
                    confidence_score REAL DEFAULT 1.0,
                    source_video_id TEXT,
                    created_at TIMESTAMP
                )
            ''')
            # Seed default high-retention golden rules for toddlers if empty
            cursor.execute('SELECT COUNT(*) FROM retention_rules')
            if cursor.fetchone()[0] == 0:
                default_rules = [
                    ("hook", "Never use an intro logo or title card. Start immediately with high-energy sound effect and smiling character in the first 3 seconds.", 1.0),
                    ("pacing", "Shift visual camera zoom, bounce, or color every 3 to 4 seconds to prevent sensory adaptation.", 1.0),
                    ("audio", "Keep background music tempo between 110-125 BPM with playful glockenspiel or bouncy synth.", 1.0),
                    ("interactive", "Include direct toddler engagement questions every 45-60 seconds (e.g. 'Can you point to the yellow duck?').", 1.0),
                    ("transition", "Between different poems in the compilation, use a whoosh or giggle sound effect with zero silent pauses.", 1.0)
                ]
                for cat, rule, conf in default_rules:
                    cursor.execute('''
                        INSERT INTO retention_rules (category, rule_text, confidence_score, source_video_id, created_at)
                        VALUES (?, ?, ?, 'system_seed', ?)
                    ''', (cat, rule, conf, datetime.now()))
            conn.commit()

    def add_video(self, video_id: str, title: str, topic: str, duration_sec: float):
        with self.get_connection() as conn:
            conn.cursor().execute('''
                INSERT OR REPLACE INTO videos (video_id, title, topic, duration_sec, published_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (video_id, title, topic, duration_sec, datetime.now()))
            conn.commit()

    def update_metrics(self, video_id: str, ctr: float, ret_15s: float, ret_1m: float, ret_3m: float, ret_end: float, views: int):
        with self.get_connection() as conn:
            conn.cursor().execute('''
                UPDATE videos
                SET ctr = ?, retention_15s = ?, retention_1m = ?, retention_3m = ?, retention_end = ?, total_views = ?, analyzed = 0
                WHERE video_id = ?
            ''', (ctr, ret_15s, ret_1m, ret_3m, ret_end, views, video_id))
            conn.commit()

    def get_all_rules(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT category, rule_text, confidence_score FROM retention_rules ORDER BY id DESC LIMIT 15')
            return [dict(row) for row in cursor.fetchall()]

    def add_rule(self, category: str, rule_text: str, confidence_score: float = 1.0, source_video_id: str = ""):
        with self.get_connection() as conn:
            conn.cursor().execute('''
                INSERT INTO retention_rules (category, rule_text, confidence_score, source_video_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (category, rule_text, confidence_score, source_video_id, datetime.now()))
            conn.commit()


class CriticAgent:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def format_rules_for_prompt(self) -> str:
        rules = self.db.get_all_rules()
        if not rules:
            return "No historical rules yet."
        formatted = []
        for r in rules:
            formatted.append(f"- [{r['category'].upper()}] {r['rule_text']}")
        return "\n".join(formatted)

    def analyze_video_retention(self, video_id: str, script_summary: str = ""):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM videos WHERE video_id = ?', (video_id,))
            row = cursor.fetchone()
            if not row:
                return "Video not found in database."
            video = dict(row)

        critique_notes = []
        # Rule heuristics if below threshold
        if video['retention_15s'] < 0.65:
            rule = f"First 15s retention was low ({video['retention_15s']*100:.1f}%). Hook must deliver visual transformation within 4 seconds."
            self.db.add_rule("hook", rule, 0.9, video_id)
            critique_notes.append(rule)

        if video['retention_3m'] < 0.40:
            rule = f"Minute 3 drop-off observed ({video['retention_3m']*100:.1f}%). Insert a major interactive game or sound effect at 2:30."
            self.db.add_rule("pacing", rule, 0.85, video_id)
            critique_notes.append(rule)

        if video['ctr'] < 0.05 and video['total_views'] > 100:
            rule = f"CTR was low ({video['ctr']*100:.1f}%). Thumbnail needs larger smiling eye area and maximum 2 words of text."
            self.db.add_rule("thumbnail", rule, 0.8, video_id)
            critique_notes.append(rule)

        with self.db.get_connection() as conn:
            conn.cursor().execute('UPDATE videos SET analyzed = 1 WHERE video_id = ?', (video_id,))
            conn.commit()

        return critique_notes or ["Retention performance met target thresholds!"]
