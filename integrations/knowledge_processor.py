import requests
from bs4 import BeautifulSoup
import re
import logging
# import lxml
from youtube_transcript_api import YouTubeTranscriptApi

logger = logging.getLogger(__name__)

class KnowledgeProcessor:
    """
    Processa informações externas (texto, URLs, relatórios) para 
    enriquecer o contexto do Agente Analista.
    """
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def detect_urls(self, text: str) -> list:
        """Encontra URLs em um texto."""
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*'
        return re.findall(url_pattern, text)

    def extract_youtube_id(self, url: str) -> str:
        """Extrai o ID do vídeo de um link do YouTube."""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/|v\/|youtu.be\/)([0-9A-Za-z_-]{11})',
            r'(?:shorts\/)([0-9A-Za-z_-]{11})'
        ]
        for p in patterns:
            match = re.search(p, url)
            if match:
                return match.group(1)
        return None

    def process_url(self, url: str) -> dict:
        """Decide se processa como web ou youtube."""
        yt_id = self.extract_youtube_id(url)
        if yt_id:
            return self.process_youtube(yt_id)
        return self.process_web(url)

    def process_youtube(self, video_id: str) -> dict:
        """Extrai a transcrição de um vídeo do YouTube."""
        try:
            # Tenta Português primeiro, depois Inglês
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
            text = " ".join([t['text'] for t in transcript_list])
            
            return {
                "ok": True,
                "title": f"YouTube (Video ID: {video_id})",
                "content": f"[CONTEÚDO DO VÍDEO]: {text[:8000]}...", # Limite de contexto
                "type": "youtube"
            }
        except Exception as e:
            logger.error(f"Erro ao processar vídeo do YouTube {video_id}: {e}")
            return {"ok": False, "error": str(e)}

    def process_web(self, url: str) -> dict:
        """Extrai conteúdo de uma URL e retorna um resumo estruturado."""
        try:
            print(f"DEBUG KP: Extraindo {url}...")
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return {"ok": False, "error": f"Status {response.status_code}"}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remover scripts e estilos
            for script in soup(["script", "style"]):
                script.extract()

            title = soup.title.string if soup.title else "Sem título"
            # Pegar parágrafos principais
            paragraphs = [p.get_text().strip() for p in soup.find_all('p') if len(p.get_text()) > 50]
            content = "\n".join(paragraphs[:5]) # Limita a 5 parágrafos para não estourar contexto
            
            return {
                "ok": True,
                "type": "url",
                "title": title,
                "content": content[:1500],
                "url": url
            }
        except Exception as e:
            logger.error(f"Erro ao processar URL {url}: {e}")
            return {"ok": False, "error": str(e)}

    def process_text(self, text: str, source: str = "Manual") -> dict:
        """Processa um bloco de texto (ex: colado do NotebookLM)."""
        return {
            "ok": True,
            "type": "text",
            "source": source,
            "content": text.strip()[:3000]
        }

    def search_web(self, query: str, max_results: int = 3) -> list:
        """
        Realiza uma busca na web usando DuckDuckGo (Gratuito).
        Retorna uma lista de conteúdos extraídos.
        """
        try:
            from duckduckgo_search import DDGS
            results = []
            with DDGS() as ddgs:
                ddgs_results = [r for r in ddgs.text(query, max_results=max_results)]
                
                for r in ddgs_results:
                    url = r.get('href')
                    if url:
                        content_data = self.process_web(url)
                        if content_data['ok']:
                            results.append({
                                "title": r.get('title'),
                                "snippet": r.get('body'),
                                "full_content": content_data['content'],
                                "url": url
                            })
            return results
        except Exception as e:
            logger.error(f"Erro na busca web DuckDuckGo: {e}")
            return []

    def detect_urls(self, text: str) -> list:
        """Detecta URLs em um texto."""
        return re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
