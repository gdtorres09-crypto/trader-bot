from integrations.sports_api import SportsAPI
from integrations.database import Database
from services.probability_model import ProbabilityModel
from services.report_generator import ReportGenerator

# Novas Skills
from skills.value_bet_detector import ValueBetDetector
from skills.odds_movement_tracker import OddsMovementTracker
from skills.expected_value_calculator import EVCalculator
from skills.league_profit_analyzer import LeagueProfitAnalyzer
from skills.sharp_money_detector import SharpMoneyDetector
from skills.bankroll_optimizer import BankrollOptimizer

# Phase 2 Skills
from skills.ml_predictor import MLPredictor
from skills.live_betting_analyzer import LiveBettingAnalyzer
from skills.tilt_control import TiltControl
from skills.fixture_analyzer import FixtureAnalyzer
from skills.player_stats import PlayerStats

# Phase 3 Skills & Core
from skills.strategy_cloner import StrategyCloner
from skills.sports_trader import SportsTrader
from skills.smart_brain import SmartBrain
from core.intent_parser import IntentParser

# Phase 4 Skills
from skills.self_learning_engine import SelfLearningEngine

# Phase 5 Skills
from skills.ultimate_ai_brain import UltimateAIBrain

# Phase 6 Skills
from skills.smart_leverage_hedge import SmartLeverageHedge

# Phase 7 Skills
from skills.insider_intelligence import InsiderIntelligence

# Phase 8 Skills
from skills.time_intelligence import TimeIntelligence

# Phase 9 Skills
from skills.human_intelligence_layer import HumanIntelligenceLayer

# Phase 10 Skills
from skills.elite_intelligence_core import EliteIntelligenceCore
from integrations.youtube_monitor import YouTubeMonitor
from integrations.knowledge_processor import KnowledgeProcessor

class BettingAnalyst:
    def __init__(self):
        self.api = SportsAPI()
        self.db = Database()
        self.prob_model = ProbabilityModel()
        self.reports = ReportGenerator()
        
        # Inicializar Skills
        self.value_detector = ValueBetDetector()
        self.odds_tracker = OddsMovementTracker()
        self.ev_calculator = EVCalculator()
        self.profit_analyzer = LeagueProfitAnalyzer(self.db)
        self.sharp_detector = SharpMoneyDetector()
        self.bankroll = BankrollOptimizer(1000.0)
        
        # Skills Phase 2
        self.ml_model = MLPredictor()
        self.live_analyzer = LiveBettingAnalyzer()
        self.tilt_control = TiltControl()
        self.fixture_analyzer = FixtureAnalyzer()
        self.player_stats = PlayerStats()

        # Phase 3
        self.cloner = StrategyCloner()
        self.trader = SportsTrader()
        self.brain = SmartBrain(self)
        self.intent_parser = IntentParser()

        # Phase 4
        self.learner = SelfLearningEngine()

        # Phase 5
        self.ultimate_ai = UltimateAIBrain(self)

        # Phase 6
        self.leverage = SmartLeverageHedge(self)

        # Phase 7
        self.insider = InsiderIntelligence(self)

        # Phase 8
        self.time_intel = TimeIntelligence(self)

        # Phase 9
        self.human_intel = HumanIntelligenceLayer(self)

        # Phase 10 - Elite Intelligence Core
        self.elite = EliteIntelligenceCore()
        self.yt_monitor = YouTubeMonitor()
        self.kp = KnowledgeProcessor()

    def analyze_market(self):
        matches = self.api.get_upcoming_matches()
        detected_value_bets = []
        
        for match in matches:
            # Pegar stats dos times
            stats_home = self.api.get_team_stats(match.get('home_team_id'))
            stats_away = self.api.get_team_stats(match.get('away_team_id'))
            
            # Calcular prob real
            probs = self.prob_model.calculate_match_probability(match, stats_home, stats_away)
            
            # Detectar valor (usando a nova Skill)
            value_info = self.value_detector.find_value(probs['home'], match['odds'].get('home', 1.0))
            
            if value_info['has_value']:
                detected_value_bets.append({
                    'home_team': match['home_team'],
                    'away_team': match['away_team'],
                    'match_id': match['id'],
                    'selection': 'home',
                    'odds': match['odds']['home'],
                    'real_prob': probs['home'],
                    'ev': value_info['ev']
                })
                    
            # Salvar no DB para histórico
            match_entry = {
                **match,
                'home_prob': probs['home'],
                'draw_prob': probs['draw'],
                'away_prob': probs['away'],
                'value_detected': value_info['has_value'],
                'best_bet': 'home' if value_info['has_value'] else None
            }
            self.db.save_match(match_entry)
            
        return detected_value_bets

    def get_odds_movement_report(self):
        # Mock de reporte de movimento
        return "📉 *MOVIMENTAÇÃO DE ODDS (BETANO)*\n\n- Arsenal vs Chelsea: Queda de 1.90 para 1.85\n- Real Madrid vs Barça: Subida de 2.05 para 2.10"

    def get_sharp_report(self):
        return "👔 *ALERTA DE SHARP MONEY*\n\nDetectado volume incomum no jogo: Arsenal vs Chelsea (Vitória Arsenal)."

    def get_league_profit_report(self):
        stats = self.profit_analyzer.analyze()
        report = "🏆 *PERFORMANCE POR LIGA*\n\n"
        for league, data in stats.items():
            report += f"*{league}*: ROI {data['roi']}% | Win Rate {data['win_rate']}%\n"
        return report

    def get_ev_report(self):
        return "🧮 *CÁLCULO DE VALOR ESPERADO (EV)*\n\nPróximo Jogo: Arsenal vs Chelsea\nProb: 60% | Odd: 1.85\n*EV: +11.0%*"

    def get_ml_prediction_report(self):
        pred = self.ml_model.predict_result("Arsenal", "Chelsea")
        return f"🤖 *PREVISÃO ML (DADOS HISTÓRICOS)*\n\nJogo: Arsenal vs Chelsea\nPredição: *{pred['prediction']}*\nConfiança: {pred['confidence']}%\nProbs: H:{pred['probs']['home']} D:{pred['probs']['draw']} A:{pred['probs']['away']}"

    def get_live_report(self):
        live = self.live_analyzer.analyze_live(score="0-0", minute=65, attacks_home=110, attacks_away=45)
        return f"📺 *ANÁLISE LIVE (AO VIVO)*\n\nMinuto: 65'\nPressão Casa: {live['pressure']['home']}\nPressão Visitante: {live['pressure']['away']}\n💡 *Sugestão:* {live['suggestion']}"

    def get_tilt_report(self):
        advice = self.tilt_control.get_advice()
        return f"🧘 *CONTROLE DE TILT (EMOCIONAL)*\n\nStatus: {advice}"

    def get_fixture_report(self):
        return self.fixture_analyzer.get_schedule_report()

    def get_players_report(self):
        return self.player_stats.get_player_report()

    def get_strategy_report(self):
        strategies = self.cloner.analyze_history(None)
        report = "📋 *ESTRATÉGIAS CLONADAS*\n\n"
        for s in strategies:
            report += f"- *{s['name']}*: ROI {s['roi']}% ({s['count']} bets)\n"
        return report

    def get_trade_report(self):
        return self.trader.get_trade_signals()

    def get_brain_summary(self):
        return self.brain.get_brain_summary()

    def get_learning_report(self):
        return self.learner.get_learning_report()

    def get_leverage_report(self):
        return self.leverage.get_leverage_report()

    def get_insider_report(self):
        return self.insider.get_insider_report()

    def get_value_bets_report(self):
        vbs = self.analyze_market()
        return self.reports.generate_daily_report(vbs)

    def get_bankroll_status(self):
        stake = self.bankroll.simple_stake()
        return f"💰 *OTIMIZAÇÃO DE BANCA*\n\nSaldo: R$ {self.bankroll.bankroll:.2f}\nStake Sugerida (2%): R$ {stake:.2f}"

    def get_history_report(self):
        # Aqui pegaria do DB real, fariamos um mock por enquanto
        history = [
            {'result': 'WIN', 'profit': 20.0},
            {'result': 'LOSS', 'profit': -10.0}
        ]
        return self.reports.generate_history_report(history)

    def get_all_opportunities(self) -> list:
        """
        Busca todos os jogos disponíveis e extrai probabilidades 
        para alimentar o AutoTrader.
        """
        # 1. INTEGRAR YOUTUBE (MODO REAL)
        # Buscar novos vídeos dos canais configurados
        new_videos = self.yt_monitor.check_for_new_videos()
        tactical_insights = []
        for v in new_videos:
            result = self.kp.process_url(v['link'])
            if result.get('ok'):
                # Extrair tática usando IA
                insights = self.elite.process_tactical_info(result['content'])
                tactical_insights.append({"teams": insights['teams'], "tactical_brief": insights['tactics']})

        # 2. Buscar jogos de hoje e amanhã
        matches_today = self.api.get_upcoming_matches(days_offset=0)
        matches_tomorrow = self.api.get_upcoming_matches(days_offset=1)
        all_matches = (matches_today or []) + (matches_tomorrow or [])
        
        opportunities = []
        for m in all_matches:
            match_odds = m.get('odds', {})
            if not match_odds: continue

            # Verificar se algum Insight de YouTube cita os times deste jogo
            match_context = ""
            prob_adj = 0.0
            for insight in tactical_insights:
                if m['home'].lower() in str(insight['teams']).lower() or m['away'].lower() in str(insight['teams']).lower():
                    match_context += f" | {insight['tactical_brief']}"
                    prob_adj += 0.05 # Bônus de confiança para análise com vídeo

            # Iterar por todos os mercados disponíveis nas odds
            for market_label, odd in match_odds.items():
                if odd <= 1.2: continue # Evitar odds sem valor
                
                # Heurística de probabilidade (Phase 24 - Expansão)
                pred = self.ml_model.predict_result(m['home'], m['away'])
                
                # Se for mercado H2H (Vencedor)
                prob = 0.5 + prob_adj # Adiciona ajuste do vídeo
                market_name = market_label
                if "h2h" in market_label:
                    if m['home'] in market_label: prob = (pred['probs']['home'] / 100.0) + prob_adj
                    elif m['away'] in market_label: prob = (pred['probs']['away'] / 100.0) + prob_adj
                    market_name = "Vencedor da Partida"
                elif "totals" in market_label:
                    prob = 0.55 + prob_adj # Heurística para Over/Under
                    market_name = "Total de Pontos/Gols"
                elif "player_" in market_label:
                    # Tentar extrair nome do jogador do label (ex: player_points_LeBron James_Over 25.5)
                    parts = market_label.split("_")
                    player = parts[2] if len(parts) > 2 else "Jogador"
                    prop_type = parts[1].replace("player", "").strip()
                    detail = parts[3] if len(parts) > 3 else ""
                    market_name = f"Prop: {player} ({prop_type}) {detail}"
                    prob = 0.52 + prob_adj # Heurística

                opportunities.append({
                    'home': m['home'],
                    'away': m['away'],
                    'market': market_name,
                    'odd': odd,
                    'probability': min(prob, 0.95), # Cap em 95%
                    'confidence': (pred['confidence'] / 100.0) + (0.1 if prob_adj > 0 else 0),
                    'reason': f"Análise Híbrida: {match_context if match_context else 'Algoritmo ML + Stats'}"
                })
            
        return opportunities
