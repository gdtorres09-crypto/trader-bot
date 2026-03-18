class FixtureAnalyzer:
    """
    Analisa o calendário (agenda) para detectar fadiga e rotação.
    """
    def check_fatigue(self, team_id, last_match_date):
        # Mock de análise de calendário
        # Se o último jogo foi há menos de 3 dias, há fadiga alta
        return {
            "fatigue_level": "High" if "2026-03-14" in last_match_date else "Low",
            "rotation_risk": "Moderate" if "2026-03-14" in last_match_date else "Low"
        }

    def get_schedule_report(self):
        return "📅 *AGENDA DE JOGOS*\n\n- Arsenal: 3 jogos em 7 dias (Fadiga Crítica)\n- Man City: Folga no meio de semana (Descansado)"
