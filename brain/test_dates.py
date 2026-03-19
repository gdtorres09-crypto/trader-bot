import feedparser
from datetime import datetime, date, timedelta
import time

url = "https://www.youtube.com/feeds/videos.xml?channel_id=UCv7uIDvSTpZ_UIdnshY8yWA"
target_date = date(2026, 3, 18)
start_window = target_date - timedelta(days=3)

print(f"DIAGNÓSTICO DE DATAS (Target: {target_date})")
print(f"Janela permitida: {start_window} até {target_date}")

feed = feedparser.parse(url)
print(f"Total de entradas: {len(feed.entries)}")

for i, entry in enumerate(feed.entries):
    pt = entry.get('published_parsed')
    if pt:
        pub_date = datetime.fromtimestamp(time.mktime(pt)).date()
        status = "✅ DENTRO" if start_window <= pub_date <= target_date else "❌ FORA"
        print(f"{i+1}. [{pub_date}] {status} - {entry.title}")
    else:
        print(f"{i+1}. Sem data - {entry.title}")
