from integrations.sports_api import SportsAPI
from integrations.database import Database
from services.probability_model import ProbabilityModel
from services.report_generator import ReportGenerator
import logging

logger = logging.getLogger(__name__)

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

    def generate_studio_content(self, content_type: str, game_data: dict = None) -> str:
        """
        Gera conteúdo específico para o 'Estúdio IA' (NotebookLM Style).
        """
        # Chamar o Elite Core para geração real via LLM
        return self.elite.generate_studio_content(content_type, game_data)

    def perform_deep_web_research(self, home: str, away: str) -> str:
        """
        Realiza uma pesquisa profunda na web sobre o confronto.
        """
        query = f"{home} x {away} provável escalação desfalques notícias hoje"
        results = self.kp.search_web(query)
        
        research_context = ""
        for r in results:
            research_context += f"\n--- FONTE: {r['title']} ---\n{r['full_content'][:1000]}\n"
        
        return research_context if research_context else "Nenhuma informação adicional encontrada na web."

    def get_all_opportunities(self, sport_filter: str = "TODOS", target_date = None, log_callback = None) -> list:
        """
        Busca todos os jogos disponíveis e extrai probabilidades 
        para alimentar o AutoTrader e o Painel Premium.
        """
        def log(msg):
            if log_callback: log_callback(msg)
            # Assuming logger is defined elsewhere, e.g., import logging; logger = logging.getLogger(__name__)
            # For this context, we'll just print if logger is not available.
            try:
                logger.info(msg)
            except NameError:
                print(msg) # Fallback if logger is not globally defined

        log(f"🔎 Iniciando Varredura Híbrida ({sport_filter} | {target_date})...")
        
        # 1. YouTube Monitoring (Fase 18)
        log("📺 Monitorando canais táticos do YouTube...")
        new_videos = self.yt_monitor.check_for_new_videos(sport_filter, target_date)
        log(f"✅ {len(new_videos)} novos vídeos detectados nos últimos feeds.")
        
        all_expert_picks = []
        for v in new_videos:
            res = self.kp.process_url(v['link'], title=v['title'])
            content = res.get('content', '') if res.get('ok') else f"Título: {v['title']}\n{v['channel']}"
            
            # Extrair palpites usando a IA Elite (Nova Fase Consensus)
            raw_picks = self.elite._analyze_youtube_content(content, title=v['title'])
            
            if "VÍDEO SEM PALPITES" not in raw_picks.upper():
                log(f"✅ Palpites extraídos de {v['channel']}: {v['title'][:30]}...")
                # Parser simples para extrair os blocos da IA
                import re
                blocks = re.split(r'JOGO:', raw_picks)
                for block in blocks[1:]:
                    lines = block.strip().split('\n')
                    match_name = lines[0].strip() if lines else "Desconhecido"
                    palpite = ""
                    razao = ""
                    for line in lines:
                        if "PALPITE:" in line: palpite = line.replace("PALPITE:", "").strip()
                        if "RAZÃO:" in line: razao = line.replace("RAZÃO:", "").strip()
                    
                    all_expert_picks.append({
                        "video_id": v['id'],
                        "channel": v['channel'],
                        "match_name": match_name,
                        "pick": palpite,
                        "reason": razao
                    })

        log(f"⚽ Buscando odds reais no mercado ({sport_filter})...")
        all_matches = []
        try:
            from datetime import datetime
            if target_date:
                today = datetime.now().date()
                diff = (target_date - today).days
                # Permitir busca para a data alvo exata, mesmo que seja ontem (diff = -1)
                for offset in [diff]:
                     matches = self.api.get_upcoming_matches(sport=sport_filter.lower() if sport_filter != "TODOS" else "football", days_offset=offset)
                     if matches: all_matches.extend(matches)
            else:
                for offset in [0, 1]:
                    matches = self.api.get_upcoming_matches(sport=sport_filter.lower() if sport_filter != "TODOS" else "football", days_offset=offset)
                    if matches: all_matches.extend(matches)
        except Exception as e:
            if "CRÉDITOS" in str(e):
                log(f"⚠️ {str(e)}")
            else:
                log(f"❌ Erro na API: {e}")
        
        opportunities = []
        
        # 3. Gerir CONSENSO entre especialistas
        # 3. Gerir CONSENSO entre especialistas (se houver apenas picks, sem mercado ainda)
        # Observação: Esta seção foi integrada no item "5. Cruzamento de Dados" para melhor fluxo lógico.

        # 5. Cruzamento de Dados (Oportunidades com base em mercado real)
        matched_picks_ids = set()
        for match in all_matches:
            match_name = f"{match['home']} vs {match['away']}" # Usando chaves do get_upcoming_matches
            
            # Encontrar picks para este jogo (Fuzzy match)
            from difflib import SequenceMatcher
            match_picks = []
            for p in all_expert_picks:
                ratio = SequenceMatcher(None, match_name.lower(), p['match_name'].lower()).ratio()
                if ratio > 0.7:
                    match_picks.append(p)
                    matched_picks_ids.add(id(p))
            
            if match_picks:
                consensus_count = len(match_picks)
                channels = [p['channel'] for p in match_picks]
                
                if consensus_count >= 2:
                    opportunities.append({
                        "id": f"consensus_{match['id']}",
                        "match": match_name,
                        "market": match_picks[0]['pick'],
                        "type": "CONSENSO ELITE",
                        "confidence": "ALTA" if consensus_count > 2 else "MÉDIA",
                        "reason": f"{consensus_count} especialistas concordam: {', '.join(channels)}",
                        "is_consensus": True,
                        "extra": {"channels": channels, "picks": match_picks}
                    })
                else:
                    opportunities.append({
                        "id": f"expert_{match['id']}",
                        "match": match_name,
                        "market": match_picks[0]['pick'],
                        "type": "EXPERT INSIGHT",
                        "confidence": "MÉDIA",
                        "reason": f"Dica de {match_picks[0]['channel']}: {match_picks[0]['reason']}",
                        "is_expert": True
                    })

        # 6. Fallback: Mostrar Experts mesmo sem dados de mercado (API LIMITE)
        for p in all_expert_picks:
            if id(p) not in matched_picks_ids:
                opportunities.append({
                    "id": f"raw_expert_{p['video_id']}_{hash(p['match_name'])}",
                    "match": p['match_name'],
                    "market": p['pick'],
                    "type": "EXPERT INSIDER",
                    "confidence": "ALTA",
                    "reason": f"Análise do Canal {p['channel']}: {p['reason']}",
                    "is_expert": True,
                    "is_consensus": False
                })

        log(f"📈 {len(opportunities)} oportunidades identificadas (Expert + Mercado).")
        return opportunities
