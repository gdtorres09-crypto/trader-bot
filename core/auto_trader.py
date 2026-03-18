import logging
import json
import os
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)

class AutoTrader:
    """
    Núcleo de Automação do Trader Esportivo.
    Responsável por: 
    - Evitar sinais duplicados
    - Calcular EV (Expected Value)
    - Formatar sinais profissionais
    """
    
    def __init__(self, agent):
        self.agent = agent
        self.sent_signals = [] # Lista de dicionários (histórico completo)
        self.history_file = "data/signals_history.json"
        self._load_history()

    def _load_history(self):
        try:
            if not os.path.exists(self.history_file):
                self.sent_signals = []
                return
            with open(self.history_file, 'r') as f:
                self.sent_signals = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.sent_signals = []

    def _save_history(self):
        # Garantir diretório data/
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump(self.sent_signals, f, indent=4)

    def calculate_ev(self, probability: float, odd: float) -> float:
        """
        Calcula o Valor Esperado (EV).
        EV = (Probabilidade * Odd) - 1
        """
        if probability <= 0 or odd <= 0:
            return -1.0
        return (probability * odd) - 1

    def calculate_stake(self, ev: float, confidence: float, bankroll: float) -> float:
        """
        Calcula a stake sugerida conforme regras da Fase 25:
        - Alta Confiança -> 3%
        - Média Confiança -> 2%
        - Baixa Confiança -> 1%
        """
        base_percentage = 0.01 # 1% (Baixa)
        if ev > 0.15 or confidence > 0.8: 
            base_percentage = 0.03 # 3% (Alta)
        elif ev > 0.08 or confidence > 0.6: 
            base_percentage = 0.02 # 2% (Média)
        
        final_stake = bankroll * base_percentage
        return round(final_stake, 2)

    def format_signal(self, bet: Dict) -> str:
        """Formata o sinal no padrão profissional solicitado."""
        ev = bet.get('ev', 0.0)
        prob = bet.get('probability', 0.0)
        stake = bet.get('stake', 0.0)
        
        icon = "🔥" if ev > 0.15 else "📊"
        
        return (
            f"{icon} **VALUE BET DETECTADA**\n\n"
            f"🏀⚽ **Jogo:** {bet['home']} vs {bet['away']}\n"
            f"📊 **Mercado:** {bet['market']}\n"
            f"💰 **Odd:** {bet['odd']:.2f} (Betano)\n"
            f"📈 **Probabilidade:** {prob*100:.1f}%\n"
            f"⚖️ **EV:** {ev:+.2f}\n"
            f"💵 **Stake Sugerida:** R$ {stake:.2f}\n\n"
            f"🧠 **Análise Híbrida:** {bet['reason']}\n"
            f"_(Fontes: API Real-Time + YouTube Insights + Expert Context)_"
        )

    async def run_analysis_cycle(self) -> List[str]:
        """
        Executa um ciclo completo de análise.
        Retorna lista de strings prontas para enviar ao Telegram.
        """
        logger.info("Iniciando ciclo automático de 10 minutos...")
        
        # 1. Buscar jogos e odds
        # Usamos o BettingAnalyst para consolidar os dados
        opportunities = self.agent.get_all_opportunities() # Novo método que implementaremos
        
        signals = []
        for opt in opportunities:
            # Chave de deduplicação usando os dados básicos
            # Verificamos se já enviamos esse jogo/mercado/odd hoje
            already_sent = any(
                s['home'] == opt['home'] and 
                s['away'] == opt['away'] and 
                s['market'] == opt['market'] 
                for s in self.sent_signals
            )
            
            if already_sent:
                continue
                
            # 2. Calcular EV
            ev = self.calculate_ev(opt['probability'], opt['odd'])
            
            # 3. Filtrar apenas EV Positivo (Phase 24)
            if ev > 0.02: 
                opt['ev'] = ev
                opt['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Acessa o valor numérico dentro do objeto BankrollOptimizer
                current_bankroll = self.agent.bankroll.bankroll
                opt['stake'] = self.calculate_stake(ev, opt.get('confidence', 0.5), current_bankroll)
                
                # Formatar e adicionar
                signals.append(self.format_signal(opt))
                self.sent_signals.append(opt) # Salvar objeto completo no histórico
        
        if signals:
            self._save_history()
            
        return signals
