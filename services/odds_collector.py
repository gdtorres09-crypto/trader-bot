class OddsCollector:
    def __init__(self, api):
        self.api = api

    def fetch_latest_odds(self):
        # Wrapper para coletar odds via API
        return self.api.get_upcoming_matches()

class MatchAnalyzer:
    def __init__(self, prob_model):
        self.prob_model = prob_model

    def run_analysis(self, match, stats_home, stats_away):
        return self.prob_model.calculate_match_probability(match, stats_home, stats_away)
