import asyncio
from integrations.youtube_monitor import YouTubeMonitor
from integrations.knowledge_processor import KnowledgeProcessor
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

async def test_search_fallback():
    print("--- Testing YouTube Search Fallback ---")
    monitor = YouTubeMonitor()
    kp = KnowledgeProcessor()
    
    target_date = datetime(2026, 3, 18).date()
    
    # Forçar falha no RSS mockando o requests.get
    import requests
    original_get = requests.get
    def mock_get(url, **kwargs):
        class MockResponse:
            status_code = 403
            text = ""
            content = b""
        return MockResponse()
    
    requests.get = mock_get
    
    print(f"Buscando videos para {target_date} (RSS bloqueado)...")
    videos = monitor.check_for_new_videos("NBA", target_date)
    
    print(f"Videos encontrados: {len(videos)}")
    for v in videos[:2]:
        print(f"Canal: {v['channel']} | Titulo: {v['title']} | Link: {v['link']}")
        
        # Testar KP com fallback de metadados
        print(f"Processando {v['id']}...")
        res = kp.process_url(v['link'], title=v['title'])
        print(f"OK: {res['ok']} | Tipo: {res['type']}")
        print(f"Conteudo (primeiros 100 caracteres): {res['content'][:100]}")
        print("-" * 20)
    
    # Teste direto ddgs.videos se 0
    if len(videos) == 0:
        print("Testando DDGS.videos direto...")
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            v_res = list(ddgs.videos('site:youtube.com "NBA Brasil" palpites', max_results=5))
            for vr in v_res:
                print(f"Video DDG: {vr.get('title')} -> {vr.get('content')}")
    
    requests.get = original_get
    
    if len(videos) > 0 or (len(videos) == 0 and 'v_res' in locals() and len(v_res) > 0):
        print("\nSUCESSO: Alguma forma de busca funcionou!")
    else:
        print("\nFALHA: Nada funcionou.")

if __name__ == "__main__":
    asyncio.run(test_search_fallback())
