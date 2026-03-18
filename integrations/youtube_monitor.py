import feedparser
import json
import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class YouTubeMonitor:
    def __init__(self, kp):
        self.kp = kp
        self.channels_file = "config/youtube_channels.json"
        self.history_file = "data/youtube_seen_videos.json"
        self._ensure_files()

    def _ensure_files(self):
        os.makedirs("config", exist_ok=True)
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.channels_file):
            with open(self.channels_file, 'w') as f:
                json.dump([
                    {"name": "Apostador Profissional", "id": "UC77aF4_oV0vSxe87nxsW-wQ"},
                    {"name": "NBA Análises", "id": "UC0mYxHk3xnzYp-ZToT0vX8A"}
                ], f)
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w') as f:
                json.dump([], f)

    def _get_channels(self) -> List[Dict]:
        with open(self.channels_file, 'r') as f:
            return json.load(f)

    def _get_seen_videos(self) -> List[str]:
        with open(self.history_file, 'r') as f:
            return json.load(f)

    def _save_seen_video(self, video_id: str):
        seen = self._get_seen_videos()
        seen.append(video_id)
        # Keep only last 100 to save space
        with open(self.history_file, 'w') as f:
            json.dump(seen[-100:], f)

    def check_for_new_videos(self) -> List[Dict]:
        """
        Verifica os feeds RSS dos canais e retorna novos vídeos para processamento.
        """
        new_videos = []
        seen = self._get_seen_videos()
        channels = self._get_channels()

        for ch in channels:
            feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={ch['id']}"
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:3]: # Checar os 3 últimos
                    video_id = entry.yt_videoid
                    if video_id not in seen:
                        logger.info(f"Novo vídeo detectado: {entry.title} ({ch['name']})")
                        new_videos.append({
                            "id": video_id,
                            "title": entry.title,
                            "url": entry.link,
                            "channel": ch['name']
                        })
                        self._save_seen_video(video_id)
            except Exception as e:
                logger.error(f"Erro ao monitorar canal {ch['name']}: {e}")

        return new_videos
