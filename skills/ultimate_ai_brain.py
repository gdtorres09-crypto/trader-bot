class UltimateAIBrain:
    """
    O Cérebro Supremo: Unifica todos os sistemas e decide a estratégia de inteligência.
    Classifica apostas em ALTA, MÉDIA e BAIXA confiança.
    """
    def __init__(self, agent):
        self.agent = agent

    def process_match(self, match_id, prob, odds, strategy_id="default"):
        """
        Analisa uma oportunidade usando IA LEVE e decide se ativa a IA PESADA.
        """
        # 1. IA LEVE: Regras fixas e cálculos matemáticos
        ev = self.agent.ev_calculator.calculate_ev(prob, odds)
        weight = self.agent.learner.get_strategy_weight(strategy_id)
        
        # Filtros de confiança
        score = ev * weight
        
        confidence = "BAIXA"
        if score > 0.15:
            confidence = "ALTA"
        elif score > 0.05:
            confidence = "MÉDIA"
            
        # 2. Decisão: Usar IA PESADA?
        # Apenas para ALTA confiança ou ROI esperado muito alto
        should_use_heavy_ai = (confidence == "ALTA" or score > 0.2)
        
        return {
            "match_id": match_id,
            "confidence": confidence,
            "score": round(score, 4),
            "ev": round(ev, 4),
            "strategy_weight": weight,
            "use_heavy_ai": should_use_heavy_ai
        }

    def get_ultimate_status(self):
        return "💎 *ULTIMATE AI BRAIN STATUS*\n\n- Unificação: 100%\n- Modo: Automático/Sinais\n- Classificação de Risco Ativa\n- Otimização de Custo (Lei de Pareto) Ativa"
