import random

class SmartLeverageHedge:
    """
    Skill para alavancagem inteligente com proteção de risco e hedge automático.
    """
    def __init__(self, agent):
        self.agent = agent
        self.config = {
            "valor_inicial": 50,
            "dias_max": 5
        }
        self.current_cycle = {
            "day": 1,
            "bankroll": 50.0,
            "history": []
        }

    def get_leverage_opportunity(self):
        """
        Busca a melhor oportunidade de alavancagem baseada no risco/confiança.
        """
        # Simulação de busca usando Ultimate AI
        # Na vida real, iteraria sobre os jogos do value_bet_detector
        confidence = random.choice(["ALTA", "MÉDIA", "ALTA OPORTUNIDADE"])
        
        # Ajuste inteligente de Odd
        odd_range = (1.5, 1.7)
        if confidence == "MÉDIA":
            odd_range = (1.7, 1.85)
        elif confidence == "ALTA OPORTUNIDADE":
            odd_range = (1.85, 2.0)

        # Simulação de jogo encontrado
        match = "Real Madrid vs Barcelona"
        odd = round(random.uniform(odd_range[0], odd_range[1]), 2)
        investimento = self.current_cycle["bankroll"]
        
        return {
            "jogo": match,
            "aposta": "Vitória Casa",
            "odd": odd,
            "investimento": investimento,
            "confianca": confidence,
            "risco": "Baixo" if odd < 1.7 else "Moderado",
            "sugestao_hedge": "Monitorar aos 60 minutos para saída parcial."
        }

    def check_hedge_realtime(self, match_data):
        """
        Verifica se é necessário aplicar hedge em tempo real.
        """
        sport = match_data.get("sport", "futebol")
        score = match_data.get("score", [0, 0])
        time = match_data.get("minute", 0)
        
        if sport == "futebol":
            # Exemplo: 2x0 aos 60 minutos
            if score[0] >= 2 and time > 60:
                return "🛡️ *HEDGE RECOMENDADO:* Saída parcial disponível. Garanta lucro!"
        elif sport == "nba":
            # Exemplo: Vantagem de 15 pontos
            if abs(score[0] - score[1]) >= 15:
                return "🛡️ *NBA HEDGE:* Vantagem de 15 pontos. Proteja sua posição!"
        
        return None

    def should_stop_cycle(self, wins_in_row, next_match_risk):
        """
        Decisão de parada inteligente.
        """
        if wins_in_row >= 3 and next_match_risk == "ALTO":
            return True
        return False

    def get_leverage_report(self):
        opp = self.get_leverage_opportunity()
        report = "🚀 *ALAVANCAGEM & HEDGE HOJE*\n\n"
        report += f"Ciclo: Dia {self.current_cycle['day']}/5\n"
        report += f"Banco Atual: R$ {self.current_cycle['bankroll']}\n"
        report += f"----------------------------\n"
        report += f"🎮 Jogo: *{opp['jogo']}*\n"
        report += f"🎯 Aposta: {opp['aposta']}\n"
        report += f"📈 Odd Ideal: {opp['odd']}\n"
        report += f"💰 Entrada: R$ {opp['investimento']}\n"
        report += f"⭐ Confiança: {opp['confianca']}\n"
        report += f"⚠️ Risco: {opp['risco']}\n"
        report += f"🛡️ Hedge: {opp['sugestao_hedge']}\n"
        report += f"----------------------------\n"
        report += "Insight: Se atingir 3 vitórias, o sistema avaliará parada automática."
        return report
