from config.settings import MIN_VALUE_BET_THRESHOLD

class ValueBetDetector:
    def __init__(self):
        self.threshold = MIN_VALUE_BET_THRESHOLD

    def detect_value(self, calculated_probs, bookmaker_odds):
        """
        Compara probabilidade calculada com probabilidade implícita das odds.
        Value = (Probabilidade Real * Odds) - 1
        """
        value_bets = []
        
        # Mapeamento
        mappings = {
            "home": bookmaker_odds.get('home'),
            "draw": bookmaker_odds.get('draw'),
            "away": bookmaker_odds.get('away')
        }
        
        for selection, odd in mappings.items():
            if not odd: continue
            
            implied_prob = 1 / odd
            real_prob = calculated_probs.get(selection, 0)
            
            ev = (real_prob * odd) - 1 # Expected Value
            
            if ev > self.threshold:
                value_bets.append({
                    "selection": selection,
                    "odds": odd,
                    "real_prob": real_prob,
                    "implied_prob": round(implied_prob, 2),
                    "ev": round(ev, 3)
                })
        
        return value_bets
