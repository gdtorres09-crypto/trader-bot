import asyncio
import logging
import sys
import os

# Ajustar path para importar módulos do projeto
sys.path.append(os.getcwd())

from integrations.youtube_monitor import YouTubeMonitor
from integrations.knowledge_processor import KnowledgeProcessor
from agents.betting_analyst import BettingAnalyst

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Diagnostic")

async def run_diagnostic():
    print("=== MONITOR DIAGNOSTIC ===")
    monitor = YouTubeMonitor()
    kp = KnowledgeProcessor()
    analyst = BettingAnalyst()
    
    target_date = "2026-03-18" 
    sport = "NBA" # Selecionar um
    
    # 1. Test Discovery
    print(f"\n1. Buscando videos de {sport} para {target_date}...")
    videos = monitor.check_for_new_videos(sport, target_date)
    print(f"Encontrados: {len(videos)} videos.")
    
    if not videos:
        print("AVISO: Nenhum video encontrado via RSS ou Search. Pulando processamento.")
        # Se 0, tentaremos forçar um ID conhecido para testar o resto
        videos = [{"id": "ib-hbFXkwC0", "title": "Teste Manual NBA", "link": "https://www.youtube.com/watch?v=ib-hbFXkwC0", "channel": "NBA Brasil"}]
        print(f"Usando video de teste manual: {videos[0]['id']}")

    # 2. Test Processing
    v = videos[0]
    try:
        print(f"\n2. Processando video {v['id']} ({v['title']})...")
    except:
        print(f"\n2. Processando video {v['id']}...")
    res = kp.process_url(v['link'], title=v['title'])
    print(f"Resultado KP: OK={res['ok']}, Tipo={res['type']}")
    print(f"Tamanho do conteúdo extraído: {len(res['content'])} caracteres.")
    if len(res['content']) < 100:
        print(f"CONTEÚDO: {res['content']}")

    # 3. Test Full Pipeline
    print(f"\n3. Executando BettingAnalyst.get_all_opportunities...")
    opportunities = analyst.get_all_opportunities(sport, target_date)
    print(f"Oportunidades geradas: {len(opportunities)}")
    
    for i, opp in enumerate(opportunities[:3]):
        print(f"[{i+1}] {opp['type']} | Match: {opp['match']} | Market: {opp.get('market', 'N/A')}")
        print(f"    Rerason: {opp['reason'][:100]}...")

    print("\n=== DIAGNOSTICO CONCLUÍDO ===")

if __name__ == "__main__":
    asyncio.run(run_diagnostic())
