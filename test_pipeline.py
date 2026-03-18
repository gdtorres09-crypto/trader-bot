import os
import sys

# Adiciona o diretório raiz ao path para importar configurações
sys.path.append(os.getcwd())

from core.intent_parser import IntentParser
from skills.elite_intelligence_core import EliteIntelligenceCore
from integrations.llm_provider import LLMProvider
from integrations.sports_api import SportsAPI

def test_full_pipeline():
    api = SportsAPI()
    llm = LLMProvider()
    core = EliteIntelligenceCore()
    
    print("--- 1. Buscando Jogos Reais ---")
    matches = api.get_upcoming_matches("nba", days_offset=0)
    print(f"Jogos NBA: {len(matches)}")
    
    match_lines = []
    for rm in matches[:5]:
        match_lines.append(f"- {rm['home']} vs {rm['away']} | Liga: {rm['league']} | Data: {rm['date']} {rm['time']}")
    match_context = "\n".join(match_lines)
    
    print("\n--- 2. Chamando LLM com Contexto ---")
    user_text = "Dicas de NBA para hoje"
    full_ctx = (
        f"ESPORTE/LIGA SOLICITADO: NBA. "
        f"Data Hoje: 2026-03-17. "
        f"JOGOS REAIS DISPONÍVEIS NA API:\n{match_context}\n\n"
        f"FOCO BETANO. "
        f"INSTRUÇÃO ESPECÍFICA: Faça uma análise/previsão do jogo solicitado. "
        f"IMPORTANTE: Use APENAS os jogos listados acima. Mencione os times EXATAMENTE como escritos."
    )
    
    response = llm.chat(user_text, context=full_ctx, model_type="light")
    sys.stdout.reconfigure(encoding='utf-8')
    print(f"RESPOSTA LLM (NBA Hoje):\n{response}")
    
    print("\n--- 3. Validando Resposta (NBA Hoje) ---")
    final = core.process(user_id=123, user_text=user_text, intent="value_bet", raw_response=response)
    print(f"RESPOSTA FINAL CORE (NBA Hoje):\n{final}")

    print("\n--- 4. Testando Histórico (Sem jogos hoje) ---")
    user_text_hist = "Qual o histórico do Flamengo?"
    intent_hist = "history"
    full_ctx_hist = (
        f"ESPORTE: Futebol. "
        f"Data Hoje: 2026-03-17. "
        f"JOGOS REAIS DISPONÍVEIS NA API:\nNENHUM JOGO PARA HOJE.\n\n"
        f"INSTRUÇÃO: Se pedido histórico, apresente dados passados e não diga 'sem jogos'."
    )
    response_hist = llm.chat(user_text_hist, context=full_ctx_hist, model_type="light")
    print(f"RESPOSTA LLM (Histórico):\n{response_hist}")
    
    print("\n--- 5. Validando Resposta (Histórico) ---")
    final_hist = core.process(user_id=123, user_text=user_text_hist, intent=intent_hist, raw_response=response_hist)
    print(f"RESPOSTA FINAL CORE (Histórico):\n{final_hist}")

if __name__ == "__main__":
    test_full_pipeline()
