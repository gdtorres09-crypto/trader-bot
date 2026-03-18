class MatchAnalyzer:
    def __init__(self, prob_model):
        self.prob_model = prob_model

    def run_analysis(self, match, stats_home, stats_away):
        """
        Executa a análise detalhada de uma partida.
        """
        return self.prob_model.calculate_match_probability(match, stats_home, stats_away)
