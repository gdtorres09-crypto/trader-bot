from config.settings import DEFAULT_BANKROLL, STAKE_STRATEGY, DEFAULT_STAKE_PERCENT

class BankrollManager:
    def __init__(self, current_bankroll=DEFAULT_BANKROLL):
        self.bankroll = current_bankroll
        self.strategy = STAKE_STRATEGY

    def calculate_stake(self, odds, real_prob):
        """
        Calcula a stake baseada na estratégia (Fixed ou Kelly).
        """
        if self.strategy == "fixed":
            return self.bankroll * DEFAULT_STAKE_PERCENT
        
        elif self.strategy == "kelly":
            # Kelly Criterion: f* = (bp - q) / b
            # b = odds - 1, p = real_prob, q = 1 - p
            b = odds - 1
            p = real_prob
            q = 1 - p
            kelly_f = (b * p - q) / b
            
            # Usar Half-Kelly para ser mais conservador (50% do sugerido)
            return max(0, self.bankroll * (kelly_f * 0.5))
        
        return self.bankroll * 0.01 # Default 1%

    def update_bankroll(self, profit_loss):
        self.bankroll += profit_loss
        return self.bankroll
