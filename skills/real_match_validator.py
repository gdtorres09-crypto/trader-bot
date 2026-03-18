"""
real_match_validator.py
--------------------------
OBJETIVO: Garantir que o agente nunca invente jogos (alucinação).
Cross-references a resposta do LLM com os dados reais da SportsAPI.
"""

import re
import logging
from datetime import datetime
from integrations.sports_api import SportsAPI

logger = logging.getLogger(__name__)

class RealMatchValidator:
    def __init__(self, api: SportsAPI):
        self.api = api
        # Padrões para extrair jogos da resposta (ex: "Arsenal vs Chelsea" ou "Lakers - Warriors")
        self.match_patterns = [
            r"([A-Za-z\s]+)\s+vs\.?\s+([A-Za-z\s]+)",
            r"([A-Za-z\s]+)\s+x\s+([A-Za-z\s]+)",
            r"([A-Za-z\s]+)\s+\-\s+([A-Za-z\s]+)"
        ]

    def validate_and_format(self, raw_response: str, intent: str, date_label: str = "Hoje") -> dict:
        """
        Analisa a resposta, valida jogos e aplica o formato mandatório.
        Retorna: { 'ok': bool, 'response': str, 'error': str }
        """
        # 1. Extrair confrontos mencionados
        matches_found = self._extract_matches(raw_response)
        print(f"DEBUG VAL: Jogos extraídos: {matches_found}")
        
        # Bypass for chat/history if no matches found
        if not matches_found and intent not in ["value_bet", "leverage", "previsao", "trade"]:
             return {
                 "ok": True,
                 "response": raw_response,
                 "error": None
             }

        if not matches_found and intent in ["value_bet", "leverage", "previsao", "trade"]:
             print(f"DEBUG VAL: Bloqueado - Nenhum jogo achado para intent '{intent}'")
             return {
                 "ok": False,
                 "response": "Não há jogos confiáveis disponíveis hoje.",
                 "error": "No matches found in response for betting intent."
             }

        # 2. Validar cada confronto com a API
        validated_matches = []
        for home, away in matches_found:
            query = f"{home} {away}"
            print(f"DEBUG VAL: Validando '{query}' em '{date_label}'...")
            real_match = self.api.search_matches(query, date_context=date_label)
            if real_match:
                print(f"DEBUG VAL: Jogo VALIDADO: {real_match['home']} vs {real_match['away']}")
                validated_matches.append(real_match)
            else:
                print(f"DEBUG VAL: Jogo NÃO encontrado: {query}")
                logger.warning(f"Jogo não validado: {home} vs {away}")

        # 3. Se houve jogos mas nenhum foi validado
        if matches_found and not validated_matches:
            return {
                "ok": False,
                "response": "Não há jogos confiáveis disponíveis hoje.",
                "error": "Matches found but none validated against real data."
            }

        # 4. Formatar a resposta no novo padrão obrigatório se houver jogos validados
        final_response = raw_response
        if validated_matches:
            final_response = self._apply_mandatory_format(raw_response, validated_matches)

        return {
            "ok": True,
            "response": final_response,
            "error": None
        }

    def _extract_matches(self, text: str):
        """Extrai pares de times da resposta de forma mais robusta."""
        found = []
        # Limpar markdown e emojis para facilitar o regex
        clean_text = re.sub(r'[^\w\s\.\-x]', ' ', text)
        clean_text = clean_text.replace("**", " ").replace("__", " ")
        
        for pattern in self.match_patterns:
            matches = re.findall(pattern, clean_text)
            for m in matches:
                home, away = m[0].strip(), m[1].strip()
                # Limpar espaços duplos e resíduos de markdown
                home = ' '.join(home.split())
                away = ' '.join(away.split())
                
                # Filtro simples para evitar falsos positivos
                if len(home) > 3 and len(away) > 3:
                    found.append((home, away))
        return list(set(found)) # Remove duplicatas

    def check_final(self, text: str):
        """
        Valida se o formato mandatório (Regra 3 - Trader Mode) está presente.
        Se for uma resposta de histórico ou chat, permitimos maior flexibilidade.
        """
        mandatory_options = [
            "1️⃣ Aposta SEGURA",
            "2️⃣ Aposta de VALOR",
            "3️⃣ Aposta OUSADA"
        ]
        
        # Bypass de Histórico/Estatísticas
        if any(kw in text.lower() for kw in ["histórico", "estatísticas", "desempenho", "médias"]):
             return "ANÁLISE" in text or "RESULTADOS" in text

        # Para análises de jogo, checa o template de 3 opções
        found_options = [s for s in mandatory_options if s in text]
        if len(found_options) < len(mandatory_options):
            print(f"DEBUG VAL: Falta opções de trader. Achadas: {found_options}")
            return False
            
        return True

    def _apply_mandatory_format(self, text: str, validated_matches: list) -> str:
        """
        A IA agora gera o formato completo.
        Apenas garantimos que se validamos algo, a resposta é liberada.
        """
        return text
