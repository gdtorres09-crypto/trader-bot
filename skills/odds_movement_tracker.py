class OddsMovementTracker:
    """
    Monitora a mudança de odds no mercado (Betano).
    """
    def __init__(self):
        self.history = {}

    def track(self, match_id, current_odds):
        if match_id not in self.history:
            self.history[match_id] = []
        
        self.history[match_id].append(current_odds)
        
        if len(self.history[match_id]) > 1:
            prev = self.history[match_id][-2]
            # Simplificado: detecta queda ou subida brusca
            diff = {k: current_odds[k] - prev[k] for k in current_odds}
            return diff
        return None
