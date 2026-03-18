import feedparser
import json
import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class YouTubeMonitor:
    def __init__(self, kp=None):
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
                    {"name": "TNT Sports Brasil", "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCv7uIDvSTpZ_UIdnshY8yWA"},
                    {"name": "NBA Brasil", "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UC_t-X1P9Z86wD6xJ9h_qY2A"}
                ], f)
        if not os.path.exists(self.history_file):
            if not os.path.exists(os.path.dirname(self.history_file)):
                os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, 'w') as f:
                json.dump([], f)

    def _get_channels(self) -> List[Dict]:
        try:
            with open(self.channels_file, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    def _get_seen_videos(self) -> List[str]:
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    def _save_seen_video(self, video_id: str):
        seen = self._get_seen_videos()
        if video_id not in seen:
            seen.append(video_id)
            # Mantém apenas os últimos 500
            with open(self.history_file, 'w') as f:
                json.dump(seen[-500:], f)

    def check_for_new_videos(self) -> List[Dict]:
        """
        Verifica os feeds RSS dos canais e retorna novos vídeos.
        """
        new_videos = []
        seen = self._get_seen_videos()
        channels = self._get_channels()

        for ch in channels:
            # Usa a URL direta do config (deve ser o link do feed xml)
            feed_url = ch.get('url')
            if not feed_url: continue

            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:2]: # Checar os 2 mais recentes para maior velocidade
                    video_id = entry.get('yt_videoid')
                    if not video_id:
                         # Tenta extrair da URL se não estiver no meta
                         video_id = entry.link.split("v=")[-1] if "v=" in entry.link else entry.id
                    
                    if video_id not in seen:
                        logger.info(f"Monitor: Novo vídeo em {ch['name']} -> {entry.title}")
                        new_videos.append({
                            "id": video_id,
                            "title": entry.title,
                            "link": entry.link,
                            "channel": ch['name']
                        })
                        self._save_seen_video(video_id)
            except Exception as e:
                logger.error(f"Erro no monitor YouTube ({ch.get('name')}): {e}")

        return new_videos
