class SportsTrader:
    """
    Motor de trading esportivo: Scalping, Swing e Hedge.
    """
    def __init__(self):
        pass

    def evaluate_trade(self, entry_odd, current_odd, side="back"):
        """
        Calcula se deve sair (cash out) ou fazer hedge.
        """
        if current_odd < entry_odd:
            profit_pct = (entry_odd / current_odd) - 1
            return {"action": "EXIT_PROFIT", "profit": round(profit_pct * 100, 2)}
        
        elif current_odd > entry_odd * 1.2:
            return {"action": "HEDGE_LOSS", "advice": "Reduzir exposição"}
            
        return {"action": "WAIT", "status": "Estável"}

    def get_trade_signals(self):
        # Mock de sinais de trading
        return "💹 *SINAIS DE TRADING LIVE*\n\n- Arsenal: Odd caiu (2.00 -> 1.85). Sugestão: *FECHAR LUCRO*.\n- Chelsea: Movimento Swing detectado."
