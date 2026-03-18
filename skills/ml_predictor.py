import random

class MLPredictor:
    """
    Prevê resultados baseado em dados históricos e modelos estatísticos.
    """
    def __init__(self):
        # Em produção, carregaríamos um modelo (ex: scikit-learn, tensorflow)
        pass

    def predict_result(self, home_team, away_team):
        # Simulação de predição ML
        win_prob = random.uniform(0.3, 0.7)
        draw_prob = random.uniform(0.1, 0.3)
        away_prob = 1.0 - win_prob - draw_prob
        
        return {
            "prediction": "Home Win" if win_prob > away_prob else "Away Win",
            "confidence": round(max(win_prob, away_prob) * 100, 2),
            "probs": {
                "home": round(win_prob, 4),
                "draw": round(draw_prob, 4),
                "away": round(away_prob, 4)
            }
        }
