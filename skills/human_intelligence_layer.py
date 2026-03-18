import json
from datetime import datetime

class HumanIntelligenceLayer:
    """
    Skill para personalização, perfil de risco e comportamento humano do agente.
    """
    def __init__(self, agent):
        self.agent = agent
        self.default_profile = {
            "risk_level": "medium",  # safe, medium, aggressive
            "style": "consistent",   # consistent, fast_profit
            "preferred_markets": ["over 2.5", "match_odds"],
            "last_interaction": None,
            "win_streak": 0,
            "loss_streak": 0
        }

    def get_user_profile(self, user_id):
        """
        Recupera ou cria perfil do usuário na base.
        """
        # Por enquanto, simula via memória/DB (ajustaremos o DB depois)
        profile_json = self.agent.db.get_preference(user_id, "user_profile")
        if profile_json:
            return json.loads(profile_json)
        return self.default_profile

    def save_user_profile(self, user_id, profile):
        self.agent.db.save_preference(user_id, "user_profile", json.dumps(profile))

    def adapt_risk_preference(self, user_id, text):
        """
        Identifica se o usuário quer mudar o nível de risco.
        """
        text = text.lower()
        profile = self.get_user_profile(user_id)
        
        changed = False
        if any(w in text for w in ["seguro", "tranquilo", "conservador", "baixo risco"]):
            profile["risk_level"] = "safe"
            changed = True
        elif any(w in text for w in ["agressivo", "alto risco", "alavancar forte"]):
            profile["risk_level"] = "aggressive"
            changed = True
        elif any(w in text for w in ["normal", "padrão", "equilibrado"]):
            profile["risk_level"] = "medium"
            changed = True

        if changed:
            self.save_user_profile(user_id, profile)
        
        return profile["risk_level"]

    def format_human_response(self, user_id, response_data, intent):
        """
        Transforma dados brutos em uma resposta com 'tom' humano.
        """
        profile = self.get_user_profile(user_id)
        risk = profile["risk_level"]
        
        # Heurística de Tom Humano
        intro = ""
        if risk == "safe":
            intro = "Foquei em opções mais conservadoras para você hoje, priorizando a segurança da banca. 🛡️\n\n"
        elif risk == "aggressive":
            intro = "Busquei oportunidades de maior retorno, como você prefere, mas lembre-se do gerenciamento! 🚀\n\n"
        else:
            intro = "Análise concluída com foco em equilíbrio e valor. ⚖️\n\n"

        # Adiciona sugestões 'humanas' baseadas no mercado
        advice = ""
        if "vazio" in str(response_data).lower() or not response_data:
            advice = "\n⚠️ *Dica do Trader:* O mercado está um pouco 'seco' agora. Às vezes o melhor trade é não entrar. Recomendo aguardar uma oportunidade melhor."
        else:
            advice = f"\n👉 *Contexto:* Esta entrada foi filtrada pelo seu perfil de risco *{risk}*."

        return f"{intro}{response_data}{advice}"

    def update_streak(self, user_id, result):
        """
        Adapta comportamento baseado em acertos/erros.
        """
        profile = self.get_user_profile(user_id)
        if result == "win":
            profile["win_streak"] += 1
            profile["loss_streak"] = 0
        else:
            profile["loss_streak"] += 1
            profile["win_streak"] = 0
            
        # Sugestão automática de parada se loss streak >= 3
        if profile["loss_streak"] >= 3:
            profile["risk_level"] = "safe" # Força modo seguro
            
        self.save_user_profile(user_id, profile)
