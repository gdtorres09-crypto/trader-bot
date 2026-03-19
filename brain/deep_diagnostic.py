import sys
import os
import sys

# Forçar UTF-8 para evitar erro de charmap no Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from datetime import date
import logging
import json

# Setup paths
root_path = os.getcwd()
sys.path.insert(0, root_path)

from agents.betting_analyst import BettingAnalyst
from core.auto_trader import AutoTrader
from integrations.youtube_monitor import YouTubeMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DIAGNOSTIC")

def test_everything():
    print("\n--- INICIANDO DIAGNÓSTICO PROFUNDO ---")
    
    # 1. Testar Monitor Diretamente
    print("\n1. Testando YouTubeMonitor...")
    monitor = YouTubeMonitor()
    target = date(2026, 3, 18)
    print(f"Buscando vídeos para FUTEBOL em {target}...")
    
    # Ver o que tem no feed sem filtros primeiro
    channels = monitor._get_channels()
    football_channels = [c for c in channels if c.get('type') == 'futebol']
    print(f"Canais de Futebol configurados: {len(football_channels)}")
    
    # Testar com um canal específico para ver o que vem no XML
    import feedparser
    if football_channels:
        ch = football_channels[0]
        print(f"Lendo feed de {ch['name']}: {ch['url']}")
        feed = feedparser.parse(ch['url'])
        print(f"Vídeos no feed: {len(feed.entries)}")
        for entry in feed.entries[:3]:
            print(f" - [{entry.get('published')}] {entry.title}")
    
    videos = monitor.check_for_new_videos("FUTEBOL", target)
    print(f"Vídeos encontrados após filtros: {len(videos)}")
    
    # 2. Testar BettingAnalyst
    print("\n2. Testando BettingAnalyst.get_all_opportunities...")
    analyst = BettingAnalyst()
    def log_cb(msg):
        print(f" [ANALYST LOG] {msg}")
    
    # Simular o loop interno para ver onde falha
    print("Iniciando monitoramento manual no teste...")
    videos = analyst.yt_monitor.check_for_new_videos("FUTEBOL", target)
    print(f"Monitor encontrou {len(videos)} vídeos para a data {target}.")
    
    tactical_insights = []
    for v in videos:
        print(f"Processando vídeo: {v['title']} ({v['channel']})")
        res = analyst.kp.process_url(v['link'])
        if not res.get('ok'):
            print(f"  ❌ Falha no processamento da URL: {res.get('error', 'Unknown')}")
            continue
            
        print(f"  AI analisando conteúdo ({len(res['content'])} caracteres)...")
        tactical_res = analyst.elite._analyze_youtube_content(res['content'])
        print(f"  Resultado AI: {tactical_res[:100]}...")
        
        if "VÍDEO DE BAIXA QUALIDADE" in tactical_res:
            print(f"  ⚠️ Filtro: Vídeo ignorado por baixa qualidade tática.")
        else:
            tactical_insights.append(v)
            print(f"  ✅ Insight Adicionado!")

    print(f"Total de Insights Táticos após AI: {len(tactical_insights)}")
    
    # 3. Testar AutoTrader (O filtro final)
    print("\n3. Testando AutoTrader.run_analysis_cycle...")
    trader = AutoTrader(analyst)
    import asyncio
    signals = asyncio.run(trader.run_analysis_cycle(sport_filter="FUTEBOL", target_date=target, log_callback=log_cb))
    print(f"Sinais (GEMS) gerados pelo AutoTrader: {len(signals)}")
    for s in signals:
        print("\n--- SINAL GERADO ---")
        print(s)

if __name__ == "__main__":
    test_everything()
