class LeagueProfitAnalyzer:
    """
    Analisa quais ligas estão trazendo mais lucro histórico.
    """
    def __init__(self, db):
        self.db = db

    def analyze(self):
        # Aqui conectaria com a tabela bet_history e matches
        # Mock de retorno para o agente
        return {
            "Premier League": {"roi": 12.5, "win_rate": 65},
            "La Liga": {"roi": 8.2, "win_rate": 58},
            "NBA": {"roi": 15.0, "win_rate": 70}
        }
