import random

class InsiderIntelligence:
    """
    Skill para detecção de sinais antecipados via notícias, insiders e movimentação de odds.
    """
    def __init__(self, agent):
        self.agent = agent
        self.reliable_sources = ["Jornalista X", "Fonte Oficial", "Insider Premier"]

    def detect_early_signals(self):
        """
        Simula o monitoramento de fontes e cruza com odds.
        """
        # Exemplo de sinais detectados (Simulação)
        signals = [
            {
                "evento": "Manchester City vs Arsenal",
                "noticia": "Haaland sentiu no aquecimento (Rumor Twitter)",
                "fonte": "Twitter News",
                "confiabilidade": "BAIXA",
                "odds_moving": False
            },
            {
                "evento": "Lakers vs Celtics",
                "noticia": "LeBron James poupado para amanhã (Confirmado)",
                "fonte": "Jornalista NBA Pro",
                "confiabilidade": "ALTA",
                "odds_moving": True
            },
            {
                "evento": "Flamengo vs Palmeiras",
                "noticia": "Escalação vazada: Tite vai com reservas",
                "fonte": "Insider Gávea",
                "confiabilidade": "MÉDIA",
                "odds_moving": True
            }
        ]
        
        # Filtro de Anti-Fake e Cruzamento
        processed_signals = []
        for s in signals:
            if s["confiabilidade"] == "ALTA" and s["odds_moving"]:
                s["status"] = "ALTO VALOR - ENTRAR AGORA"
                s["confianca_final"] = "95%"
            elif s["confiabilidade"] == "MÉDIA" or s["odds_moving"]:
                s["status"] = "MÉDIA - AGUARDAR CONFIRMAÇÃO"
                s["confianca_final"] = "60%"
            else:
                s["status"] = "IGNORAR - RUMOR FRACO"
                s["confianca_final"] = "10%"
            
            if s["status"] != "IGNORAR - RUMOR FRACO":
                processed_signals.append(s)

        return processed_signals

    def get_insider_report(self):
        signals = self.detect_early_signals()
        if not signals:
            return "🕵️‍♂️ *INSIDER INTEL:* Nenhum sinal forte detectado no momento."

        report = "🕵️‍♂️ *SINAIS ANTECIPADOS (INSIDER INTEL)*\n\n"
        for s in signals:
            report += f"🎮 Evento: *{s['evento']}*\n"
            report += f"📰 Notícia: {s['noticia']}\n"
            report += f"✅ Confiança: {s['confiabilidade']} ({s['confianca_final']})\n"
            report += f"🚀 Ação: {s['status']}\n"
            report += "----------------------------\n"
        
        return report
