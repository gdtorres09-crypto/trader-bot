from agents.betting_analyst import BettingAnalyst
import logging

logging.basicConfig(level=logging.INFO)

def test_youtube_fallback():
    agent = BettingAnalyst()
    print("--- Testando Fallback YouTube (Modo Analítico) ---")
    
    # Simulamos que a API falhou (já sabemos que a Odds API falha com 401)
    # E injetamos um "vídeo novo" manualmente para ver se gera Gem.
    
    # O monitor retornaria algo assim:
    new_vids = [
        {
            "id": "abc12345678",
            "title": "Flamengo vs Palmeiras - Análise Tática",
            "link": "https://www.youtube.com/watch?v=abc12345678",
            "channel": "TNT Sports",
            "type": "futebol"
        }
    ]
    
    # No main.py, o ciclo faria:
    # agent.elite.inject_knowledge(user_id, vid['link'])
    # Mas aqui queremos testar o get_all_opportunities diretamente.
    
    # Vamos mockar o yt_monitor para retornar nosso vídeo
    from unittest.mock import MagicMock
    agent.yt_monitor.check_for_new_videos = MagicMock(return_value=new_vids)
    
    # Mockar o processamento do vídeo para não depender de transcrição real agora
    agent.kp.process_url = MagicMock(return_value={"ok": True, "content": "Transcript mock: O Flamengo joga com pressão alta e o Palmeiras no contra-ataque.", "title": "Video Mock"})
    agent.elite._analyze_youtube_content = MagicMock(return_value="Insight tático: Intensidade alta do Flamengo.")

    opportunities = agent.get_all_opportunities(sport_filter="football")
    
    print(f"Oportunidades geradas via Fallback: {len(opportunities)}")
    for opt in opportunities:
        print(f"Gem: {opt['home']} vs {opt['away']} | Motivo: {opt['reason']}")

if __name__ == "__main__":
    test_youtube_fallback()
