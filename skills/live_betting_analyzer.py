class LiveBettingAnalyzer:
    """
    Analisa jogos ao vivo (In-Play) buscando valor imediato.
    """
    def analyze_live(self, score, minute, attacks_home, attacks_away):
        # Lógica de pressão ofensiva
        pressure_home = attacks_home / max(minute, 1)
        pressure_away = attacks_away / max(minute, 1)
        
        suggestion = "Sem entrada forte"
        if pressure_home > 1.5 and minute > 60:
            suggestion = "Próximo Gol: Time da Casa"
        elif pressure_away > 1.5 and minute > 60:
            suggestion = "Próximo Gol: Time Visitante"
            
        return {
            "pressure": {"home": round(pressure_home, 2), "away": round(pressure_away, 2)},
            "suggestion": suggestion
        }
