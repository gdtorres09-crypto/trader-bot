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
        Verifica os feeds RSS dos canais e retorna novos vídeos. 
        FALLBACK: Usa DuckDuckGo se o RSS falhar.
        """
        new_videos = []
        channels = self._get_channels()
        seen_ids = set()

        for ch in channels:
            # 1. Filtro de Esporte (Case-insensitive)
            ch_item_type = ch.get('type', 'futebol').upper() # Renomeado para evitar conflito
            target_sport = sport_type.upper()
            if target_sport != "TODOS" and ch_item_type != target_sport:
                continue

            videos_for_ch = []
            
            # TENTATIVA 1: RSS Feed
            feed_url = ch.get('url')
            if feed_url:
                try:
                    import requests
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                    response = requests.get(feed_url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        feed = feedparser.parse(response.content)
                        for entry in feed.entries[:10]:
                            v_id = entry.get('yt_videoid') or (entry.link.split("v=")[-1] if "v=" in entry.link else entry.id)
                            videos_for_ch.append({
                                "id": v_id,
                                "title": entry.title,
                                "link": entry.link,
                                "pub_parsed": entry.get('published_parsed')
                            })
                except Exception as e:
                    logger.warning(f"Monitor: RSS Falhou para {ch['name']}: {e}")

            # TENTATIVA 2: DuckDuckGo Fallback (Se RSS vazio ou falhou)
            if not videos_for_ch:
                logger.warning(f"Monitor: Iniciando Busca Web Fallback para {ch['name']}...")
                try:
                    import re
                    from duckduckgo_search import DDGS
                    # Busca de VÍDEOS: Focada em PALPITES e PROGNÓSTICOS (PT-BR)
                    query = f'site:youtube.com "{ch["name"]}" palpites prognosticos {ch_item_type} hoje'
                    with DDGS() as ddgs:
                        try:
                            results = list(ddgs.videos(query, max_results=8))
                        except:
                            results = []
                        
                        for r in results:
                            link = r.get('content', r.get('href', ''))
                            title = r.get('title', 'Vídeo via Search')
                            
                            if "youtube.com" in link or "youtu.be" in link:
                                # Extração de ID
                                import re
                                yt_id_match = re.search(r"(?:v=|\/)([A-Za-z0-9_-]{11})", link)
                                if yt_id_match:
                                    v_id = yt_id_match.group(1)
                                    if v_id not in [vid['id'] for vid in videos_for_ch]:
                                        videos_for_ch.append({
                                            "id": v_id,
                                            "title": title,
                                            "link": f"https://www.youtube.com/watch?v={v_id}",
                                            "pub_parsed": None 
                                        })
                except Exception as ex:
                    logger.error(f"Monitor: Fallback Search (Videos) falhou para {ch['name']}: {ex}")

            # 3. Filtragem e Deduplicação Final do Canal
            from datetime import datetime
            if isinstance(target_date, str):
                target_dt = datetime.strptime(target_date, "%Y-%m-%d")
            else:
                target_dt = target_date

            for v in videos_for_ch:
                if v['id'] in seen_ids: continue
                seen_ids.add(v['id'])
                
                # Bater data apenas se disponível (RSS)
                if v['pub_parsed']:
                    v_date = datetime(*v['pub_parsed'][:3])
                    if v_date.date() == target_dt.date():
                        new_videos.append({
                            "id": v['id'],
                            "title": v['title'],
                            "link": v['link'],
                            "channel": ch['name'],
                            "sport": ch_item_type
                        })
                else:
                    # Se busca web, assumimos que é relevante se veio na busca de 'palpites'
                    new_videos.append({
                        "id": v['id'],
                        "title": v['title'],
                        "link": v['link'],
                        "channel": ch['name'],
                        "sport": ch_item_type
                    })

        return new_videos
