from datetime import datetime, timedelta
import re

class TimeIntelligence:
    """
    Skill para interpretação de tempo, fuso horário e validação de contexto temporal.
    """
    def __init__(self, agent):
        self.agent = agent
        self.user_contexts = {} # Memória de tempo por usuário

    def parse_time_intent(self, user_id, text):
        """
        Identifica a intenção temporal na mensagem do usuário.
        """
        text = text.lower()
        now = datetime.now() # Assume fuso correto do sistema/config
        
        target_date = None
        label = "hoje"

        if "amanhã" in text or "amanha" in text:
            target_date = now + timedelta(days=1)
            label = "amanhã"
        elif "hoje" in text:
            target_date = now
            label = "hoje"
        elif "depois de amanhã" in text or "depois de amanha" in text:
            target_date = now + timedelta(days=2)
            label = "depois de amanhã"
        elif "fim de semana" in text:
            # Lógica simples para próximo sábado
            days_to_sat = (5 - now.weekday()) % 7
            if days_to_sat == 0 and now.hour > 12: # Se já é sábado tarde, próximo
                days_to_sat = 7
            target_date = now + timedelta(days=days_to_sat)
            label = "fim de semana"
        elif "ao vivo" in text or "live" in text:
            label = "ao vivo"
            target_date = now
        
        # Se não detectou mas tem memória, mantém
        if not target_date and user_id in self.user_contexts:
            context = self.user_contexts[user_id]
            # Se a memória for recente (últimos 10 min), reutiliza
            if (datetime.now() - context["timestamp"]).total_seconds() < 600:
                target_date = context["date"]
                label = context["label"]

        # Atualiza memória
        if target_date:
            self.user_contexts[user_id] = {
                "date": target_date,
                "label": label,
                "timestamp": datetime.now()
            }
        else:
            # Default para hoje se nada for detectado/lembrado
            target_date = now
            label = "hoje"

        return target_date, label

    def validate_response_date(self, response_text, requested_label):
        """
        Garante que a resposta não contém datas conflitantes.
        Ex: Usuário pediu amanhã, mas bot retornou 'hoje'.
        """
        if requested_label == "amanhã" and "hoje" in response_text.lower():
            # Tenta corrigir ou limpa termos conflitantes
            return response_text.replace("hoje", "amanhã").replace("HOJE", "AMANHÃ")
        
        return response_text

    def get_date_string(self, date_obj):
        return date_obj.strftime("%d/%m/%Y")
