
import feedparser
import json
import os
from datetime import datetime
import time

def test_actual_config():
    config_path = "app_config/youtube_channels.json"
    if not os.path.exists(config_path):
        print(f"Erro: {config_path} não encontrado.")
        return

    with open(config_path, 'r') as f:
        channels = json.load(f)
    
    print(f"--- Testando {len(channels)} canais do arquivo de configuração ---")
    
    success_count = 0
    for ch in channels:
        print(f"\n>> {ch['name']} ({ch['type']})")
        feed = feedparser.parse(ch['url'])
        status = feed.get('status', 'N/A')
        entries = len(feed.entries)
        
        if status == 200 and entries > 0:
            print(f"   [OK] Status 200 | {entries} vídeos.")
            success_count += 1
            # Mostrar o mais recente
            top = feed.entries[0]
            print(f"   Último: {top.title[:50]}...")
        else:
            print(f"   [FALHA] Status {status} | {entries} vídeos.")

    print(f"\n--- Resumo: {success_count}/{len(channels)} canais OK ---")

if __name__ == "__main__":
    test_actual_config()
