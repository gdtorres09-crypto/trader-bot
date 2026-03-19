from integrations.sports_api import SportsAPI
import logging

logging.basicConfig(level=logging.INFO)

def test_web_discovery():
    api = SportsAPI()
    print("--- Testando Descoberta Web (Sem API de Odds) ---")
    
    # Tentamos buscar jogos de futebol para hoje
    matches = api.get_upcoming_matches(sport="football")
    
    print(f"Resultados encontrados via Web: {len(matches)}")
    for m in matches:
        print(f"- {m['home']} vs {m['away']} | Liga: {m['league']} | Odds: {m.get('odds')}")

if __name__ == "__main__":
    test_web_discovery()
