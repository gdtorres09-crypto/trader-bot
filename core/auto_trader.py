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
        # 1. Identificar se é um sinal de CONSENSO ou EXPERT (YouTube)
        is_expert_only = bet.get('is_expert_only', False)
        market_upper = bet['market'].upper()
        is_consensus = "CONSENSO" in market_upper
        is_expert = "EXPERT" in market_upper or is_expert_only

        if is_consensus:
             return (
                f"🏆 **[CONSENSO ELITE - YOUTUBE]** 🏆\n"
                f"🏀⚽ **Evento:** {bet['home']}\n"
                f"🔥 **RECOMENDAÇÃO:** {bet['market']}\n"
                f"👥 **Especialistas em Acordo:** {bet.get('insights_count', 0)}\n\n"
                f"📑 **RELATÓRIO DE CONSENSO:**\n{bet['reason']}\n\n"
                f"💎 _Este sinal vem da convergência de múltiplos canais de elite._"
            )
        
        if is_expert:
            return (
                f"👤 **[EXPERT INSIGHT (YouTube)]**\n"
                f"🏀⚽ **Evento:** {bet['home']}\n"
                f"📝 **Análise:** {bet['market']}\n"
                f"📊 **Confiança:** {bet.get('confidence', 0.5)*100:.0f}%\n\n"
                f"💡 **Detalhes Expert:**\n{bet['reason']}\n\n"
                f"_(Fonte: Monitoramento de Canais Estratégicos)_"
            )

        # 2. Formatação Padrão (Market/Value)
        prob = bet['probability']
        odd = bet['odd']
        ev = bet.get('ev', (prob * odd) - 1)
        stake = bet.get('stake', 10.0)
        
        return (
            f"💰 **[SINAL DE VALOR DETECTADO]**\n"
            f"🏀⚽ **Jogo:** {bet['home']} vs {bet['away']}\n"
            f"📊 **Mercado:** {bet['market']}\n"
            f"💰 **Odd:** {bet['odd']:.2f} (Betano)\n"
            f"📈 **Probabilidade:** {prob*100:.1f}%\n"
            f"⚖️ **EV:** {ev:+.2f}\n"
            f"💵 **Stake Sugerida:** R$ {stake:.2f}\n\n"
            f"🧠 **Análise Híbrida:** {bet['reason']}\n"
            f"_(Fontes: API Real-Time + YouTube Insights + Expert Context)_"
        )

    async def run_analysis_cycle(self, sport_filter: str = "TODOS", target_date = None, log_callback = None, debug_mode: bool = False) -> List[str]:
        """
        Executa um ciclo completo de análise com filtros de esporte e data.
        """
        def log(msg):
            if log_callback: log_callback(msg)
            logger.info(msg)

        log(f"🚀 Iniciando ciclo: Sport={sport_filter}, Data={target_date} (Debug={debug_mode})")
        
        # 1. Buscar jogos e odds com filtros (passando log_callback)
        opportunities = self.agent.get_all_opportunities(sport_filter, target_date, log_callback=log)
        
        log(f"🔎 Encontradas {len(opportunities)} oportunidades brutas.")
        
        signals = []
        for opt in opportunities:
            # Chave de deduplicação
            already_sent = any(
                s['home'] == opt['home'] and 
                s['away'] == opt['away'] and 
                s['market'] == opt['market'] 
                for s in self.sent_signals
            )
            
            if already_sent and not debug_mode:
                log(f"⏩ Pulando sinal duplicado: {opt['home']} vs {opt['away']}")
                continue
                
            # 2. Calcular EV
            ev = self.calculate_ev(opt['probability'], opt['odd'])
            
            # 3. Filtrar apenas EV Positivo (ou todos em modo debug, ou Informacionais/Expert)
            is_informational = opt.get('odd', 1.0) == 1.0
            is_expert = opt.get('is_expert_only')
            should_keep = ev > 0.02 or debug_mode or is_informational or is_expert
            
            if should_keep:
                type_label = 'EXPERT' if is_expert else ('INFO' if is_informational else 'VALUE')
                log(f"✅ ANALISADO: {opt['home']} vs {opt['away']} (EV: {ev:+.2f} | Tipo: {type_label})")
                opt['ev'] = ev
                opt['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                current_bankroll = self.agent.bankroll.bankroll
                opt['stake'] = self.calculate_stake(ev, opt.get('confidence', 0.5), current_bankroll)
                
                msg = self.format_signal(opt)
                if debug_mode and ev <= 0.02 and not is_informational and not is_expert:
                    msg = "⚠️ **RELATÓRIO DEBUG: EV BAIXO**\n" + msg
                
                signals.append(msg)
                # Sempre salvar Informacionais/Expert no histórico para o painel ver
                if not debug_mode or is_informational or is_expert: 
                    self.sent_signals.append(opt)
            else:
                log(f"❌ DESCARTADO: {opt['home']} vs {opt['away']} (EV: {ev:+.2f} insuficiente)")
        
        if signals:
            log(f"💎 FIM: {len(signals)} NOVAS GEMS GERADAS!")
            self._save_history()
        else:
            log(f"⚠️ FIM: Nenhuma gem nova encontrada nos parâmetros atuais.")
            
        return signals
