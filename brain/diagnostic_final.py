
import sys
import os
from datetime import datetime
import json

# Adicionar diretorio atual ao path
sys.path.append(os.getcwd())

from agents.betting_analyst import BettingAnalyst

def diagnostic():
    print("--- INICIANDO DIAGNOSTICO FINAL ---")
    analyst = BettingAnalyst()
    
    # Teste 1: YouTube NBA
    print("\n[TESTE 1] YouTube NBA...")
    videos = analyst.yt_monitor.check_for_new_videos("NBA", datetime.now().date())
    print(f"Videos NBA encontrados: {len(videos)}")

    # Teste 2: API NBA
    print("\n[TESTE 2] API NBA (Hoje)...")
    matches = analyst.api.get_upcoming_matches(sport="nba", days_offset=0)
    print(f"Jogos NBA encontrados: {len(matches)}")

    # Teste 3: Oportunidades
    print("\n[TESTE 3] Gerando Oportunidades NBA...")
    opps = analyst.get_all_opportunities(sport_filter="NBA", target_date=datetime.now().date())
    print(f"Sinais Gerados: {len(opps)}")
    for o in opps[:2]:
        print(f"  Sinal: {o['home']} vs {o['away']} | Conf: {o['confidence']}")

if __name__ == "__main__":
    diagnostic()
