import requests
import json
import logging
from datetime import datetime, timedelta, timezone

from app_config.settings import (
    CLEARSPORTS_API_KEY, THE_ODDS_API_KEY, 
    CLEARSPORTS_BASE_URL, THE_ODDS_API_BASE_URL
)

logger = logging.getLogger(__name__)

class SportsAPI:
    def __init__(self):
        self.cs_key = CLEARSPORTS_API_KEY
        self.odds_key = THE_ODDS_API_KEY
        self.cs_url = CLEARSPORTS_BASE_URL
        self.odds_url = THE_ODDS_API_BASE_URL
        # Timezone Brasil (UTC-3)
        self.tz_br = timezone(timedelta(hours=-3))

    def _get_now_br(self):
        return datetime.now(self.tz_br)

    def get_upcoming_matches(self, sport="football", date_str=None):
        """
        Coleta jogos usando pesquisa na web e análise por IA (Independente de APIs pagas).
        """
        if not date_str:
            now = self._get_now_br()
            date_str = now.strftime("%Y-%m-%d")
        
        print(f"DEBUG: Iniciando Descoberta Web para {sport} em {date_str}...")
        matches = self._fetch_web_games(sport, date_str)
        
        return matches

    def _fetch_web_games(self, sport, date_str):
        """Busca jogos usando read_url_content em sites especializados (Melhor para LLM)."""
        import requests
        # Usar read_url_content não é acessível via import direto, mas o agente tem a ferramenta.
        # No entanto, como código Python, usaremos o fallback de busca se não pudermos automatizar a ferramenta.
        # Mas o Agente pode 'ler' o conteúdo de URLs conhecidas.
        
        target_urls = []
        if "nba" in sport.lower():
            target_urls = ["https://www.espn.com.br/nba/calendario/_/data/" + date_str.replace("-", "")]
        else:
            target_urls = [
                "https://www.placardefutebol.com.br/jogos-de-hoje",
                "https://ge.globo.com/agenda/"
            ]
            
        combined_text = ""
        # Simulando o que o Agente faria: Usar a ferramenta para ler e passar para a IA
        # Mas aqui é o código rodando no servidor. 
        # Vou tentar uma abordagem hibrida: Buscar e ler os principais resultados via BeautifulSoup melhorado.
        
        from integrations.knowledge_processor import KnowledgeProcessor
        kp = KnowledgeProcessor()
        
        for url in target_urls:
            try:
                print(f"DEBUG: Tentando extração direta de {url}...")
                res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                if res.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(res.text, 'html.parser')
                    # Pega todo o texto visível se for site de placar
                    text = soup.get_text(separator=' | ', strip=True)
                    combined_text += f"\n--- FONTE DIRETA: {url} ---\n{text[:5000]}\n"
            except Exception as e:
                print(f"ERRO EXTRAÇÃO DIRETA {url}: {e}")
                
        # Fallback para busca se falhar tudo
        if not combined_text:
            search_results = kp.search_web(f"jogos de {sport} hoje {date_str} placar", max_results=3)
            for r in search_results:
                combined_text += f"\n--- {r['title']} ---\n{r['snippet']}\n"
            
        if not combined_text:
            return []
            
        return self._parse_games_from_text(combined_text, sport, date_str)

    def _parse_games_from_text(self, text, sport, date_str):
        """Usa a IA para extrair jogos estruturados de um bloco de texto bruto."""
        from integrations.llm_provider import LLMProvider
        llm = LLMProvider()
        
        prompt = (
            f"Você é um extrator de dados esportivos. Extraia os jogos de {sport} para a data {date_str} do texto abaixo.\n"
            "Formato de saída: JSON LIST de objetos com: "
            "{'id': 'slug', 'home': 'Time Casa', 'away': 'Time Fora', 'league': 'Liga', 'time': '00:00', 'odds': {'home': 1.0, 'draw': 1.0, 'away': 1.0}}\n"
            "Se não houver odds, deixe 1.0. Se não encontrar jogos, retorne [].\n\n"
            f"TEXTO:\n{text}"
        )
        
        try:
            res_text = llm.chat(prompt, model_type="light")
            # Limpar possível markdown do JSON
            json_str = res_text.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
                
            matches = json.loads(json_str)
            
            # Adicionar campos de sistema
            for m in matches:
                m['sport'] = sport
                m['date'] = date_str
                m['fallback'] = True
                if 'id' not in m or not m['id']:
                    m['id'] = f"{m['home']}_{m['away']}_{date_str}".lower().replace(" ", "_")
                if 'odds' not in m:
                    m['odds'] = {"home": 1.0, "draw": 1.0, "away": 1.0}
                    
            return matches
        except Exception as e:
            print(f"ERRO AO PARSEAR JOGOS WEB: {e}")
            return []

    def _fetch_clearsports_games(self, sport_label, date_str):
        """Mantido como backup secundário se necessário."""
        try:
            url = f"{self.cs_url}/fixtures"
            params = {"api_key": self.cs_key, "date": date_str, "sport": sport_label}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200: return []
            data = response.json()
            matches = []
            for g in data.get('data', []):
                matches.append({
                    "id": str(g.get('id', '')), "sport": sport_label, "league": g.get('league_name', 'ClearSports'),
                    "home": g.get('home_name'), "away": g.get('away_name'), "date": date_str,
                    "time": g.get('time', '00:00'), "odds": g.get('odds', {}), "fallback": True
                })
            return matches
        except: return []


    def _extract_betano_odds(self, game_data):
        """Extrai odds da Betano (Kaizen) dos dados da Odds API."""
        for bookie in game_data.get("bookmakers", []):
            if bookie.get("key") in ["betano", "kaizen"]:
                odds = {}
                for market in bookie.get("markets", []):
                    m_key = market.get("key")
                    for outcome in market.get("outcomes", []):
                        label = f"{m_key}_{outcome['name']}"
                        if "description" in outcome:
                            label = f"{m_key}_{outcome['description']}_{outcome['name']}"
                        odds[label] = outcome["price"]
                return odds
        return {}

    def search_matches(self, query: str, date_context: str = "Hoje"):
        """Busca real através das APIs de odds com fallback inteligente."""
        now_br = self._get_now_br()
        days = 0 if date_context.lower() == "hoje" else 1
        target_date = (now_br + timedelta(days=days)).strftime("%Y-%m-%d")
        
        leagues_to_check = ["nba", "epl", "ucl", "football"]
        all_found = []
        for l in leagues_to_check:
            # get_upcoming_matches já tem a lógica de cascade (0-48h) se days=0
            all_found.extend(self.get_upcoming_matches(l, days_offset=days))
        
        query_clean = query.lower()
        for m in all_found:
            home_parts = m["home"].lower().split()
            away_parts = m["away"].lower().split()
            if any(p in query_clean for p in home_parts if len(p) > 2) and \
               any(p in query_clean for p in away_parts if len(p) > 2):
                return m
        return None

    def get_betano_odds(self, match_id, sport="football"):
        now_br = self._get_now_br()
        target_date_str = now_br.strftime("%Y-%m-%d")
        
        sport_map = {
            "nba": "basketball_nba",
            "football": "soccer_brazil_campeonato",
            "epl": "soccer_epl",
            "ucl": "soccer_uefa_champs_league"
        }
        sport_key = sport_map.get(sport.lower(), "soccer_epl")
        
        matches = self._fetch_odds_api_games(sport, target_date_str, sport_key)
        for m in matches:
            if m["id"] == match_id:
                return m["odds"]
        return {}

