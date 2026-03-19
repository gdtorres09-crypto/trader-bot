from integrations.sports_api import SportsAPI
import logging

logging.basicConfig(level=logging.INFO)

def test_clearsports():
    api = SportsAPI()
    print("--- Testando Fallback ClearSports ---")
    # Forçamos o erro 401 na Odds API (ou apenas chamamos a função que agora tem fallback)
    # Como a Odds API já está dando 401, o get_upcoming_matches deve cair no ClearSports automaticamente.
    matches = api.get_upcoming_matches(sport="football")
    
    print(f"Resultados encontrados: {len(matches)}")
    for m in matches[:3]:
        print(f"- {m['home']} vs {m['away']} | Liga: {m['league']}")

if __name__ == "__main__":
    test_clearsports()
