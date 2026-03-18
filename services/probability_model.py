import numpy as np

class ProbabilityModel:
    def __init__(self):
        pass

    def calculate_match_probability(self, match_data, team_stats_home, team_stats_away):
        """
        Calcula a probabilidade real de vitória/empate/derrota baseada em estatísticas.
        Usa uma versão simplificada de regressão de Poisson ou similar.
        """
        # Exemplo simplificado baseado em média de gols e forma recente
        home_strength = self._calculate_strength(team_stats_home)
        away_strength = self._calculate_strength(team_stats_away)
        
        # Diferença de força influencia a probabilidade
        total_strength = home_strength + away_strength + 0.5 # 0.5 para empate
        
        p_home = home_strength / total_strength
        p_draw = 0.25 # Simplificado: 25% de chance de empate
        p_away = away_strength / total_strength
        
        # Normalizar
        total = p_home + p_draw + p_away
        return {
            "home": round(p_home / total, 2),
            "draw": round(p_draw / total, 2),
            "away": round(p_away / total, 2)
        }

    def _calculate_strength(self, stats):
        # Baseado em forma recente (W=1, D=0.5, L=0) e média de gols
        points = sum([1 if r == 'W' else 0.5 if r == 'D' else 0 for r in stats['recent_form']])
        avg_goals = stats['avg_goals_scored']
        return (points / len(stats['recent_form'])) * 0.5 + (avg_goals / 3.0) * 0.5
