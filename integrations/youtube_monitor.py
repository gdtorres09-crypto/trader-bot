import feedparser
import json
import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class YouTubeMonitor:
    def __init__(self, kp=None):
        self.kp = kp
        # Atualizado para o novo nome da pasta de config
        self.channels_file = "app_config/youtube_channels.json"
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

    def check_for_new_videos(self, sport_type: str = "TODOS", target_date = None) -> List[Dict]:
        """
        Verifica os feeds RSS dos canais e retorna novos vídeos filtrados por esporte e data.
        """
        new_videos = []
        seen = self._get_seen_videos()
        channels = self._get_channels()

        for ch in channels:
            # Filtro de Esporte
            ch_type = ch.get('type', 'football').upper()
            if sport_type != "TODOS" and ch_type != sport_type:
                continue

            feed_url = ch.get('url')
            if not feed_url: continue

            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]: # Checar um pouco mais para garantir que a data bata
                    # Verificar Data se fornecida
                    if target_date:
                        from datetime import datetime, timedelta
                        import time
                        # Converte struct_time para date
                        pub_time = entry.get('published_parsed')
                        if pub_time:
                            pub_date = datetime.fromtimestamp(time.mktime(pub_time)).date()
                            # Permitir vídeos de até 3 dias ANTES do alvo (previsões de rodada)
                            start_window = target_date - timedelta(days=3)
                            if pub_date < start_window or pub_date > target_date:
                                logger.info(f"Monitor: Pulando vídeo fora da janela ({pub_date})")
                                continue 

                    video_id = entry.get('yt_videoid')
                    if not video_id:
                         video_id = entry.link.split("v=")[-1] if "v=" in entry.link else entry.id
                    
                    # Para o modo "Análise de Data Centralizada", ignoramos o histórico "seen" 
                    # para permitir re-varredura do dia se o usuário quiser. 
                    # Mas para o monitor automático, mantemos.
                    # Aqui, como é gatilho manual do dashboard, vamos focar na data.
                    
                    logger.info(f"Monitor: Analisando vídeo em {ch['name']} -> {entry.title}")
                    new_videos.append({
                        "id": video_id,
                        "title": entry.title,
                        "link": entry.link,
                        "channel": ch['name'],
                        "sport": ch_type
                    })
            except Exception as e:
                logger.error(f"Erro no monitor YouTube ({ch.get('name')}): {e}")

        return new_videos
