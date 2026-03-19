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

    def get_upcoming_matches(self, sport="football", league_id=None, days_offset=0):
        """
        Coleta jogos usando APIs reais com fallback de data.
        """
        now = self._get_now_br()
        target_date_str = (now + timedelta(days=days_offset)).strftime("%Y-%m-%d")
        
        # Mapeamento de chaves da Odds API
        sport_map = {
            "nba": "basketball_nba",
            "futebol": "soccer_brazil_campeonato",
            "football": "soccer_brazil_campeonato",
            "epl": "soccer_epl",
            "ucl": "soccer_uefa_champs_league"
        }
        
        sport_key = sport_map.get(sport.lower(), "soccer_epl")
        matches = self._fetch_odds_api_games(sport, target_date_str, sport_key)
        
        # MODO FLEXÍVEL: Se não achou nada hoje, tenta amanhã (até 48h)
        if not matches and days_offset == 0:
            print(f"DEBUG: Nenhum jogo de {sport} achado para hoje. Tentando próximos dias...")
            for i in range(1, 3):
                next_date = (now + timedelta(days=i)).strftime("%Y-%m-%d")
                matches = self._fetch_odds_api_games(sport, next_date, sport_key)
                if matches:
                    print(f"DEBUG: Jogos achados para +{i} dia(s): {next_date}")
                    break
        
        return matches

    def _fetch_odds_api_games(self, sport_label, date_str, sport_key):
        """Busca jogos na The Odds API (Debug Mode On)."""
        try:
            # Usar múltiplas regiões para cobrir NBA (us) e Soccer (eu)
            regions = "us,eu" if "nba" in sport_key or "basketball" in sport_key else "eu"
            
            url = f"{self.odds_url}/sports/{sport_key}/odds"
            # Mapeamento de mercados para NBA
            markets = "h2h"
            if sport_label.lower() == "nba":
                # Revertendo para mercados básicos suportados pelo endpoint /odds
                markets = "h2h,totals"
            
            params = {
                "apiKey": self.odds_key,
                "regions": regions,
                "markets": markets,
                "dateFormat": "iso"
            }
            print(f"DEBUG API: Chamando {url} para {sport_key} em {date_str} (Regiões: {regions})")
            response = requests.get(url, params=params, timeout=10)
            
            # LOGAR RESPOSTA COMPLETA (MODO DEBUG)
            if response.status_code == 401:
                msg = "LIMITE DE CRÉDITOS DA API ATINGIDO (Status 401). Por favor, verifique seu plano no the-odds-api.com"
                print(f"CRITICAL ERROR: {msg}")
                raise Exception(msg)
            
            if response.status_code != 200:
                print(f"ERRO COMPLETO API: Status {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            matches = []
            for g in data:
                commence_time = g.get("commence_time")
                if commence_time and date_str in commence_time:
                    matches.append({
                        "id": g.get("id"),
                        "sport": sport_label,
                        "league": g.get("sport_title"),
                        "home": g.get("home_team"),
                        "away": g.get("away_team"),
                        "date": date_str,
                        "time": commence_time.split("T")[1][:5],
                        "odds": self._extract_betano_odds(g),
                        "fallback": (date_str != self._get_now_br().strftime("%Y-%m-%d"))
                    })
            return matches
        except Exception as e:
            print(f"ERRO COMPLETO: {str(e)}")
            logger.error(f"Erro Odds API ({sport_key}): {e}")
            return []

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

