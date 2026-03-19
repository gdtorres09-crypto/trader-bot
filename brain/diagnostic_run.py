
import sys
import os
from datetime import datetime
import json

# Adicionar diretório atual ao path
sys.path.append(os.getcwd())

from agents.betting_analyst import BettingAnalyst
from core.auto_trader import AutoTrader

def diagnostic():
    print("--- INICIANDO DIAGNÓSTICO PROFUNDO ---")
    print(f"Data Atual: {datetime.now()}")
    
    analyst = BettingAnalyst()
    
    # Teste 1: YouTube Monitor
    print("\n[TESTE 1] Verificando Canais YouTube...")
    try:
        from integrations.youtube_monitor import YouTubeMonitor
        yt = YouTubeMonitor()
        # Testar especificamente NBA
        videos = yt.check_for_new_videos("NBA", datetime.now().date())
        print(f"Resultados YouTube (NBA): {len(videos)} vídeos encontrados.")
        for v in videos[:3]:
            print(f" - {v['title']} ({v['channel']})")
    except Exception as e:
        print(f"ERRO TESTE 1: {e}")

    # Teste 2: Sports API
    print("\n[TESTE 2] Verificando Sports API...")
    try:
        from integrations.sports_api import SportsAPI
        api = SportsAPI()
        # Testar NBA para hoje
        matches = api.get_upcoming_matches(sport="nba", days_offset=0)
        print(f"Resultados API (NBA): {len(matches)} jogos encontrados.")
        for m in matches[:3]:
            print(f" - {m['home']} vs {m['away']} (ID: {m['id']})")
    except Exception as e:
        print(f"ERRO TESTE 2: {e}")

    # Teste 3: Fluxo Completo do Analista
    print("\n[TESTE 3] Executando get_all_opportunities (NBA)...")
    try:
        def mock_log(msg): print(f"  LOG: {msg}")
        opps = analyst.get_all_opportunities(sport_filter="NBA", target_date=datetime.now().date(), log_callback=mock_log)
        print(f"OPORTUNIDADES GERADAS: {len(opps)}")
        for o in opps[:3]:
            print(f" - {o['home']} vs {o['away']} ({o['market']}) | Confiança: {o.get('confidence')}")
    except Exception as e:
        print(f"ERRO TESTE 3: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnostic()
