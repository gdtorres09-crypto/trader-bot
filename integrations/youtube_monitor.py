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
        channels = self._get_channels()

        for ch in channels:
            # Filtro de Esporte
            ch_type = ch.get('type', 'futebol').upper()
            if sport_type != "TODOS" and ch_type != sport_type:
                continue

            feed_url = ch.get('url')
            if not feed_url: continue

            try:
                feed = feedparser.parse(feed_url)
                if not feed.entries:
                    logger.warning(f"Monitor: Feed vazio ou erro de conexo para {ch['name']}")
                    continue

                for entry in feed.entries[:10]: # Pegar os últimos 10 de cada canal
                    video_id = entry.get('yt_videoid')
                    if not video_id:
                         video_id = entry.link.split("v=")[-1] if "v=" in entry.link else entry.id
                    
                    # Log de inspeção
                    logger.info(f"Monitor: Analisando {ch['name']} -> {entry.title}")
                    
                    # Filtro de Data (Opcional com Fallback)
                    is_date_ok = True
                    if target_date:
                        from datetime import datetime, timedelta
                        import time
                        pub_time = entry.get('published_parsed')
                        if pub_time:
                            pub_date = datetime.fromtimestamp(time.mktime(pub_time)).date()
                            # Janela de 7 dias (Previsões e Pós-jogo)
                            start_window = target_date - timedelta(days=5)
                            end_window = target_date + timedelta(days=2)
                            if not (start_window <= pub_date <= end_window):
                                is_date_ok = False
                                # logger.info(f"Monitor: Pulando {pub_date} (fora da janela de {target_date})")

                    if is_date_ok:
                        new_videos.append({
                            "id": video_id,
                            "title": entry.title,
                            "link": entry.link,
                            "channel": ch['name'],
                            "sport": ch_type
                        })
            except Exception as e:
                logger.error(f"Erro no monitor YouTube ({ch.get('name')}): {e}")

        # FALLBACK: Se não encontrou NADA na data, libera as últimas 5 de cada canal geral do esporte
        if not new_videos and target_date:
            logger.warning(f"⚠️ NENHUM VÍDEO PARA {target_date}. Liberando feed geral de {sport_type}...")
            return self.check_for_new_videos(sport_type=sport_type, target_date=None)

        return new_videos
