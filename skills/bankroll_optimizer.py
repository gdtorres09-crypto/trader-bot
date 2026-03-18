from app_config.settings import DEFAULT_STAKE_PERCENT

class BankrollOptimizer:
    """
    Otimiza o tamanho da aposta (Stake) usando critérios matemáticos.
    """
    def __init__(self, bankroll):
        self.bankroll = bankroll

    def kelly_criterion(self, prob, odds, fraction=0.5):
        # b = odds - 1
        b = odds - 1
        p = prob
        q = 1 - p
        
        f = (b * p - q) / b
        return max(0, self.bankroll * f * fraction)

    def simple_stake(self):
        return self.bankroll * DEFAULT_STAKE_PERCENT
