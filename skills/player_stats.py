class PlayerStats:
    """
    Analisa estatísticas individuais de jogadores.
    """
    def get_top_performance(self):
        # Mock de estatísticas de jogadores
        return [
            {"name": "Haaland", "goals": 25, "form": "Excellent"},
            {"name": "Salah", "goals": 18, "form": "Good"},
            {"name": "Vinicius Jr", "goals": 12, "form": "Inconsistent"}
        ]

    def get_player_report(self):
        stats = self.get_top_performance()
        report = "⚽ *ESTATÍSTICAS DE JOGADORES*\n\n"
        for p in stats:
            report += f"- *{p['name']}*: {p['goals']} gols | Forma: {p['form']}\n"
        return report
