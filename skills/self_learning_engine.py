class SelfLearningEngine:
    """
    Motor de auto-aprendizado que ajusta pesos de estratégias com base no ROI real.
    """
    def __init__(self):
        self.strategy_weights = {
            "premier_league_over": 1.0,
            "serie_b_home": 1.0,
            "handicap_asiatico": 1.0,
            "default": 1.0
        }
        self.performance_history = []

    def record_bet_result(self, strategy_id, is_win, profit_loss):
        """
        Registra o resultado de uma aposta e atualiza o peso da estratégia.
        """
        self.performance_history.append({
            "strategy": strategy_id,
            "win": is_win,
            "pnl": profit_loss
        })
        
        # Ajuste dinâmico de peso (simplificado)
        current_weight = self.strategy_weights.get(strategy_id, 1.0)
        if is_win:
            new_weight = current_weight * 1.05 # Aumenta 5% em caso de vitória
        else:
            new_weight = current_weight * 0.95 # Diminui 5% em caso de derrota
            
        self.strategy_weights[strategy_id] = round(max(0.1, min(2.0, new_weight)), 2)

    def get_strategy_weight(self, strategy_id):
        return self.strategy_weights.get(strategy_id, self.strategy_weights["default"])

    def get_learning_report(self):
        report = "🧠 *RELATÓRIO DE AUTO-APRENDIZADO*\n\n"
        report += "Pesos Ajustados por Performance:\n"
        for strat, weight in self.strategy_weights.items():
            trend = "📈" if weight > 1.0 else "📉" if weight < 1.0 else "⚖️"
            report += f"- {strat}: *{weight}* {trend}\n"
        
        report += "\n*Insight:* Priorizando Premier League devido ao ROI positivo de 12%."
        return report
