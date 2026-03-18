from app_config.settings import MIN_VALUE_BET_THRESHOLD

class ValueBetDetector:
    """
    Detecta apostas com valor esperado positivo (EV+).
    """
    def __init__(self, threshold=MIN_VALUE_BET_THRESHOLD):
        self.threshold = threshold

    def find_value(self, real_prob, odds):
        implied_prob = 1 / odds
        ev = (real_prob * odds) - 1
        
        return {
            "has_value": ev > self.threshold,
            "ev": round(ev, 4),
            "implied_prob": round(implied_prob, 4),
            "edge": round(real_prob - implied_prob, 4)
        }
