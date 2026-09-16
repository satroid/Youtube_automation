import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from config.settings import YOUTUBE_CLIENT_SECRETS_FILE, BASE_DIR

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    import google.oauth2.credentials
    HAS_YT_SDK = True
except ImportError:
    HAS_YT_SDK = False

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/youtube.readonly"
]

class YouTubeClient:
    def __init__(self, client_secrets_file: str = YOUTUBE_CLIENT_SECRETS_FILE):
        self.client_secrets_file = Path(client_secrets_file)
        self.token_file = BASE_DIR / "token.json"
        self.youtube = None
        self.analytics = None

    def is_configured(self) -> bool:
        return self.client_secrets_file.exists() and HAS_YT_SDK

    def authenticate(self) -> bool:
        if not self.is_configured():
            print("[Info] YouTube client_secret.json not found. Operating in local / simulation mode.")
            return False

        creds = None
        if self.token_file.exists():
            creds = google.oauth2.credentials.Credentials.from_authorized_user_file(str(self.token_file), SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(str(self.client_secrets_file), SCOPES)
                creds = flow.run_local_server(port=0)
            with open(self.token_file, "w") as f:
                f.write(creds.to_json())

        self.youtube = build("youtube", "v3", credentials=creds)
        self.analytics = build("youtubeAnalytics", "v2", credentials=creds)
        print("[+] Authenticated with YouTube API successfully.")
        return True

    def upload_video(self, video_path: Path, thumbnail_path: Optional[Path], metadata: Dict[str, Any]) -> str:
        if not self.authenticate():
            sim_id = f"sim_yt_{video_path.stem}"
            print(f"[Simulation] Video saved locally. Upload simulated with ID: {sim_id}")
            return sim_id

        body = {
            "snippet": {
                "title": metadata["title"],
                "description": metadata["description"],
                "tags": metadata["tags"],
                "categoryId": metadata.get("category_id", "27")
            },
            "status": {
                "privacyStatus": metadata.get("privacy_status", "private"),
                "selfDeclaredMadeForKids": True
            }
        }

        media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True, mimetype="video/mp4")
        request = self.youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        
        print("[*] Uploading video to YouTube...")
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"  [-] Upload progress: {int(status.progress() * 100)}%")

        video_id = response["id"]
        print(f"[+] Video uploaded successfully! Video ID: {video_id}")

        if thumbnail_path and thumbnail_path.exists():
            print("[*] Uploading custom thumbnail...")
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(thumbnail_path), mimetype="image/jpeg")
            ).execute()
            print("[+] Custom thumbnail attached.")

        return video_id

    def fetch_retention_and_stats(self, video_id: str) -> Dict[str, Any]:
        """
        Fetches retention and performance metrics for a video.
        In simulation mode, generates realistic toddler metrics to exercise the critic loop.
        """
        if not self.authenticate() or not self.analytics:
            # Realistic simulation data for a toddler video
            import random
            rng = random.Random(hash(video_id))
            return {
                "video_id": video_id,
                "views": rng.randint(450, 12000),
                "ctr": round(rng.uniform(0.038, 0.082), 3),
                "retention_15s": round(rng.uniform(0.58, 0.78), 2),
                "retention_1m": round(rng.uniform(0.42, 0.65), 2),
                "retention_3m": round(rng.uniform(0.31, 0.52), 2),
                "retention_end": round(rng.uniform(0.22, 0.41), 2),
                "avg_view_duration_sec": 145.0
            }

        # Real YouTube Analytics query
        # Quota-friendly basic report
        try:
            report = self.analytics.reports().query(
                ids="channel==MINE",
                startDate="2026-01-01",
                endDate="2026-12-31",
                metrics="views,averageViewDuration",
                filters=f"video=={video_id}"
            ).execute()
            return {
                "video_id": video_id,
                "raw_report": report
            }
        except Exception as e:
            print(f"[Warning] Failed to fetch live analytics: {e}")
            return {}