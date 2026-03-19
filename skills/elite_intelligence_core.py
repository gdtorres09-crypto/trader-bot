"""
elite_intelligence_core.py
--------------------------
OBJETIVO: Transformar o agente em um assistente nível elite com comportamento
de trader profissional. Combina:
  1. Pensamento antes de responder (Think-Before-Respond)
  2. Mentalidade trader (Value Bet, Risco vs Retorno, Comportamento do Mercado)
  3. Memória de contexto (jogo, análise, data, perfil)
  4. Validação de resposta (auto-correção antes de enviar)
  5. Aprendizado de padrões (o que funciona, o que falha)
  6. Personalidade profissional (direto, seguro, humano)
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional
from skills.real_match_validator import RealMatchValidator
from integrations.sports_api import SportsAPI
from integrations.knowledge_processor import KnowledgeProcessor
from integrations.llm_provider import LLMProvider

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# 1. CONTEXTO ELITE (Memória Profissional)
# ─────────────────────────────────────────────
class EliteContext:
    """
    Mantém a memória do trader: último jogo citado, última análise,
    perfil de risco, data alvo, e histórico de decisões.
    """
    def __init__(self):
        self.sessions: dict = {}   # user_id → estado

    def _default(self) -> dict:
        return {
            "last_game":        None,      # Último jogo mencionado
            "last_analysis":    None,      # Última análise emitida
            "last_intent":      None,      # Última intenção interpretada
            "target_date":      "hoje",    # Contexto de tempo atual
            "risk_profile":     "medium",  # safe / medium / aggressive
            "session_bets":     [],        # Apostas na sessão atual
            "corrections_made": 0,         # Quantas auto-correções foram feitas
            "updated_at":       datetime.now().isoformat(),
        }

    def get(self, user_id: int) -> dict:
        if user_id not in self.sessions:
            self.sessions[user_id] = self._default()
        return self.sessions[user_id]

    def update(self, user_id: int, **kwargs):
        ctx = self.get(user_id)
        ctx.update(kwargs)
        ctx["updated_at"] = datetime.now().isoformat()

    def set_game(self, user_id: int, game: str):
        self.update(user_id, last_game=game)

    def set_analysis(self, user_id: int, analysis: str):
        self.update(user_id, last_analysis=analysis[:300])  # limita tamanho

    def summary(self, user_id: int) -> str:
        ctx = self.get(user_id)
        parts = []
        if ctx.get("last_game"):
            parts.append(f"Último jogo: {ctx['last_game']}")
        if ctx.get("target_date"):
            parts.append(f"Horizonte: {ctx['target_date']}")
        if ctx.get("risk_profile"):
            parts.append(f"Perfil: {ctx['risk_profile']}")
        return " | ".join(parts) if parts else "Sem contexto anterior"


# ─────────────────────────────────────────────
# 2. MENTALIDADE TRADER (Value, Mercado, Risco)
# ─────────────────────────────────────────────
class TraderMindset:
    """
    Injeta frases e lógica de trader profissional nas respostas.
    Foca em valor, comportamento de mercado e risco vs retorno.
    """

    PHRASES_VALUE = [
        "Essa odd ainda tem valor — o mercado não ajustou.",
        "Existe edge aqui. A odd está acima do esperado.",
        "Valor identificado: a probabilidade real supera a implícita.",
    ]
    PHRASES_NO_VALUE = [
        "Mercado já ajustou essa odd. Melhor evitar.",
        "Não há valor claro aqui no momento. Aguarde.",
        "A bookmaker já precificou bem esse evento. Sem edge.",
    ]
    PHRASES_RISK = [
        "Entrada com risco controlado. Está dentro do esperado.",
        "Risco aceitável dado o retorno potencial.",
        "Operação dentro dos parâmetros do gerenciamento de banca.",
    ]
    PHRASES_STOP = [
        "Melhor parar por hoje. Preserve o capital.",
        "Sem oportunidade clara agora. Disciplina é diferencial.",
        "Mercado fraco no momento. Dia de observar, não de entrar.",
    ]
    PHRASES_HEDGE = [
        "Considere um hedge para proteger o lucro garantido.",
        "Posição ganha — hedge recomendado para travar lucro.",
        "Gestão: garanta parte do retorno com hedge agora.",
    ]

    def get_value_comment(self, has_value: bool) -> str:
        import random
        if has_value:
            return random.choice(self.PHRASES_VALUE)
        return random.choice(self.PHRASES_NO_VALUE)

    def get_risk_comment(self) -> str:
        import random
        return random.choice(self.PHRASES_RISK)

    def get_stop_comment(self) -> str:
        import random
        return random.choice(self.PHRASES_STOP)

    def get_hedge_comment(self) -> str:
        import random
        return random.choice(self.PHRASES_HEDGE)

    def market_analysis(self, odd: float, confidence: float) -> dict:
        """
        Avalia se uma odd tem valor dada uma confiança estimada.
        confidence: 0.0 → 1.0 (probabilidade real estimada)
        """
        implied_prob = 1.0 / odd if odd > 0 else 0.0
        edge = confidence - implied_prob
        has_value = edge > 0.03  # Edge mínimo de 3%

        return {
            "odd": odd,
            "implied_prob": round(implied_prob * 100, 1),
            "estimated_prob": round(confidence * 100, 1),
            "edge": round(edge * 100, 1),
            "has_value": has_value,
            "verdict": "VALOR" if has_value else "SEM VALOR",
        }

    def risk_level_advice(self, risk_profile: str) -> str:
        if risk_profile == "safe":
            return "📊 Priorizando segurança: odds entre 1.40–1.70 e mercados consolidados."
        elif risk_profile == "aggressive":
            return "🚀 Perfil agressivo: buscando retorno máximo com gestão rigorosa."
        return "⚖️ Equilíbrio entre risco e retorno. Foco em mercados com edge claro."


# ─────────────────────────────────────────────
# 3. VALIDADOR DE RESPOSTA (Anti-Erro)
# ─────────────────────────────────────────────
class ResponseValidator:
    """
    Verifica a qualidade da resposta antes de enviar.
    Detecta e corrige erros de data, jogos, odds e repetições.
    """

    FORBIDDEN_PHRASES = [
        "não sei", "não tenho informações", "desculpe",
        "como assistente de IA", "sou uma IA", "não posso",
    ]

    def validate(self, response: str, context: dict) -> dict:
        """
        Retorna dict com 'ok', 'issues' e 'corrected_response'.
        """
        issues = []
        corrected = response

        # 1. Verificar frases proibidas (respostas genéricas)
        for phrase in self.FORBIDDEN_PHRASES:
            if phrase.lower() in response.lower():
                issues.append(f"Frase genérica detectada: '{phrase}'")

        # 2. Verificar inconsistência de data
        target_date = context.get("target_date", "hoje")
        if target_date == "amanhã" and "hoje" in response.lower():
            # Tenta corrigir automaticamente
            corrected = f"⚠️ *Auto-correção:* Os dados abaixo são para **amanhã**, não hoje.\n\n{corrected}"
            issues.append("Inconsistência de data detectada — corrigida automaticamente.")

        # 3. Verificar se a resposta é muito curta (genérica)
        if len(response.strip()) < 30:
            issues.append("Resposta muito curta — pode ser incompleta.")

        # 4. Verificar se há repetição óbvia
        lines = response.strip().split("\n")
        seen = set()
        unique_lines = []
        for line in lines:
            normalized = line.strip().lower()
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_lines.append(line)
            elif normalized:
                issues.append("Linha duplicada removida.")
        corrected = "\n".join(unique_lines)

        return {
            "ok": len(issues) == 0,
            "issues": issues,
            "corrected_response": corrected,
            "correction_count": len(issues),
        }


# ─────────────────────────────────────────────
# 4. SISTEMA DE APRENDIZADO (Padrão de Sucesso/Falha)
# ─────────────────────────────────────────────
class PatternLearner:
    """
    Armazena e analisa padrões de sucesso e falha para
    melhorar decisões futuras.
    """

    def __init__(self):
        self.patterns: list = []    # [{type, market, odd_range, result, ts}]
        self.market_stats: dict = {}  # market → {wins, losses, total}

    def record(self, market: str, odd: float, result: str, confidence: str = "high"):
        """
        result: 'win' | 'loss' | 'void'
        """
        entry = {
            "market":     market,
            "odd":        odd,
            "odd_range":  self._odd_range(odd),
            "result":     result,
            "confidence": confidence,
            "ts":         datetime.now().isoformat(),
        }
        self.patterns.append(entry)

        # Atualiza stats por mercado
        if market not in self.market_stats:
            self.market_stats[market] = {"wins": 0, "losses": 0, "total": 0}
        stats = self.market_stats[market]
        stats["total"] += 1
        if result == "win":
            stats["wins"] += 1
        elif result == "loss":
            stats["losses"] += 1

    def _odd_range(self, odd: float) -> str:
        if odd < 1.5:
            return "1.00–1.49"
        elif odd < 1.75:
            return "1.50–1.74"
        elif odd < 2.0:
            return "1.75–1.99"
        elif odd < 2.5:
            return "2.00–2.49"
        return "2.50+"

    def get_insight(self) -> str:
        """
        Retorna um insight baseado nos padrões registrados.
        """
        if not self.patterns:
            return "Ainda sem dados suficientes para padrões. Vamos aprendendo juntos! 📊"

        # Melhores mercados
        best_market = None
        best_rate = 0.0
        for market, stats in self.market_stats.items():
            if stats["total"] >= 3:
                rate = stats["wins"] / stats["total"]
                if rate > best_rate:
                    best_rate = rate
                    best_market = market

        # Frequência por faixa de odd
        from collections import Counter
        winning_ranges = [p["odd_range"] for p in self.patterns if p["result"] == "win"]
        top_range = Counter(winning_ranges).most_common(1)
        top_range_str = f"Faixa de odd mais lucrativa: **{top_range[0][0]}**" if top_range else ""

        lines = ["📈 *Aprendizado do Sistema:*"]
        if best_market:
            lines.append(f"✅ Melhor mercado: **{best_market}** ({best_rate*100:.0f}% acerto)")
        if top_range_str:
            lines.append(top_range_str)
        total_bets = len(self.patterns)
        wins = sum(1 for p in self.patterns if p["result"] == "win")
        lines.append(f"📊 Total: {total_bets} apostas | {wins} acertos ({wins/total_bets*100:.0f}%)")

        return "\n".join(lines)

    def should_avoid(self, market: str, odd: float) -> bool:
        """
        Detecta padrão de falha recorrente para evitar.
        """
        if market in self.market_stats:
            stats = self.market_stats[market]
            if stats["total"] >= 5:
                loss_rate = stats["losses"] / stats["total"]
                if loss_rate > 0.6:
                    return True
        return False


# ─────────────────────────────────────────────
# 5. PERSONALIDADE PROFISSIONAL (Tom & Estilo)
# ─────────────────────────────────────────────
class ElitePersonality:
    """
    Define o estilo de comunicação: direto, seguro, inteligente.
    Evita respostas robóticas, genéricas ou repetitivas.
    """

    INTROS_ANALYSIS = [
        "Analisando o cenário...",
        "Vamos ao que importa:",
        "Aqui está minha leitura do mercado:",
        "Depois de revisar os dados:",
    ]
    INTROS_NO_BET = [
        "Minha leitura hoje é clara:",
        "Após análise, minha posição é:",
        "Sem rodeios:",
    ]

    def format_intro(self, intent: str) -> str:
        import random
        if intent in ["value_bet", "previsao", "leverage"]:
            return random.choice(self.INTROS_ANALYSIS)
        return random.choice(self.INTROS_NO_BET)

    def wrap(self, text: str, intent: str, risk_profile: str, mindset: TraderMindset) -> str:
        """
        Envolve a resposta com intro, contexto de risco e fechamento.
        """
        intro   = self.format_intro(intent)
        risk_fn = mindset.risk_level_advice(risk_profile)
        return f"{intro}\n\n{text}\n\n_{risk_fn}_"


# ─────────────────────────────────────────────
# 6. THINK-BEFORE-RESPOND ENGINE (Núcleo)
# ─────────────────────────────────────────────
class ThinkEngine:
    """
    Orquestra o processo de pensamento ANTES de formular resposta.
    Pipeline: entender → contextualizar → analisar → validar → responder
    """

    def __init__(self):
        self.think_log: list = []   # log de raciocínio (debug)

    def think(self, user_id: int, user_text: str, context: dict, intent: str) -> dict:
        """
        Executa o processo de raciocínio.
        Retorna um dicionário de 'pensamento' estruturado.
        """
        thought = {
            "user_id":      user_id,
            "user_text":    user_text,
            "intent":       intent,
            "target_date":  context.get("target_date", "hoje"),
            "risk_profile": context.get("risk_profile", "medium"),
            "last_game":    context.get("last_game"),
            "last_analysis":context.get("last_analysis"),
            "understand":   self._understand(user_text),
            "needs_clarification": False,
            "should_bet":   True,
            "reason":       "",
            "ts":           datetime.now().isoformat(),
        }

        # Verificar se precisa de mais contexto
        vague_phrases = ["e aí", "e agora", "o que acha", "tem algo", "vale"]
        if any(p in user_text.lower() for p in vague_phrases) and not context.get("last_game"):
            thought["needs_clarification"] = True
            thought["reason"] = "Pergunta vaga sem contexto de jogo anterior."

        self.think_log.append(thought)
        return thought

    def _understand(self, text: str) -> str:
        """
        Classifica a intenção de forma mais granular.
        """
        t = text.lower()
        if any(w in t for w in ["vale a pena", "entro", "apostar"]):
            return "solicitar_validacao"
        if any(w in t for w in ["parar", "chega", "stop"]):
            return "solicitar_parada"
        if any(w in t for w in ["hedge", "proteger", "garantir"]):
            return "solicitar_hedge"
        if any(w in t for w in ["aprendeu", "padrão", "evolução"]):
            return "solicitar_aprendizado"
        return "geral"


# ─────────────────────────────────────────────
# 8. AGREGADOR DE CONHECIMENTO (External Data)
# ─────────────────────────────────────────────
class KnowledgeAggregator:
    """
    Mantém informações extras fornecidas pelo usuário ou capturadas de links.
    NotebookLM, Notícias, Estatísticas manuais, etc.
    """
    def __init__(self):
        self.knowledge_base: dict = {} # user_id -> [lista de conhecimentos]

    def add(self, user_id: int, source: str, content: str):
        if user_id not in self.knowledge_base:
            self.knowledge_base[user_id] = []
        
        # Manter apenas as últimas 3 inserções significativas para não estourar contexto
        self.knowledge_base[user_id].append({
            "source": source,
            "content": content,
            "ts": datetime.now().isoformat()
        })
        if len(self.knowledge_base[user_id]) > 3:
            self.knowledge_base[user_id].pop(0)

    def get_context(self, user_id: int) -> str:
        items = self.knowledge_base.get(user_id, [])
        if not items:
            return ""
        
        context_str = "\n\n📚 CONHECIMENTO EXTERNO / EXPERT:\n"
        for item in items:
            snippet = item['content'][:500] + "..." if len(item['content']) > 500 else item['content']
            context_str += f"- [{item['source']}]: {snippet}\n"
        return context_str

    def clear(self, user_id: int):
        if user_id in self.knowledge_base:
            self.knowledge_base[user_id] = []


# ─────────────────────────────────────────────
# 7. ELITE INTELLIGENCE CORE (Facade Principal)
# ─────────────────────────────────────────────
class EliteIntelligenceCore:
    """
    Ponto de entrada único para toda a inteligência elite do agente.
    Integra: Contexto, Mindset, Validator, Learner, Personality, ThinkEngine.
    """

    def __init__(self):
        self.context    = EliteContext()
        self.mindset    = TraderMindset()
        self.validator  = ResponseValidator()
        self.learner    = PatternLearner()
        self.personality= ElitePersonality()
        self.think      = ThinkEngine()
        self.api        = SportsAPI()
        self.match_val  = RealMatchValidator(self.api)
        self.kp         = KnowledgeProcessor()
        self.knowledge = KnowledgeAggregator()
        self.llm_lite = LLMProvider() # Para processamento interno (YouTube, etc)
        logger.info("EliteIntelligenceCore iniciado. Modo: Trader Profissional + Knowledge Integration. ✅")

    # ── Processo principal ──
    def process(self, user_id: int, user_text: str, intent: str,
                raw_response: str) -> str:
        """
        Aplica o pipeline completo de elite ao raw_response.
        1. Atualiza contexto
        2. Pensa antes de agir
        3. Injeta mentalidade trader
        4. Valida e auto-corrige
        5. Aplica personalidade profissional
        6. Retorna resposta final
        """
        ctx = self.context.get(user_id)

        # 1. Pensar antes de responder
        thought = self.think.think(user_id, user_text, ctx, intent)

        # 2. Detectar jogo mencionado no texto do usuário para memória
        self._extract_game(user_id, user_text)

        # 3. Injetar comentário de mentalidade trader
        # Se a IA já gerou as opções de trader, não adicionamos o comentário genérico
        mindset_comment = self._get_mindset_comment(thought, raw_response)
        enriched = raw_response
        if mindset_comment and "Aposta" not in raw_response:
            enriched = f"{enriched}\n\n💡 *Trader:* _{mindset_comment}_"

        # 4. VALIDADOR DE JOGOS REAIS (Phase 11 - Anti-Erro) ───────────
        target_date_label = ctx.get("target_date", "Hoje")
        validation_real = self.match_val.validate_and_format(enriched, intent, date_label=target_date_label)
        final_response = validation_real["response"]
        
        # 5. Check Final Anti-Erro (Usa as novas regras do modo Trader Profissional)
        if not self.match_val.check_final(final_response):
            is_betting_intent = intent in ["value_bet", "leverage", "previsao", "trade", "live"]
            if is_betting_intent:
                # Bloqueio estratégico para apostas sem validação ou formato correto
                return "Não há jogos confiáveis disponíveis hoje."
            else:
                return final_response

        # 6. Salvar análise no contexto
        self.context.set_analysis(user_id, final_response)
        self.context.update(user_id, last_intent=intent)

        return final_response

    def _analyze_youtube_content(self, transcript: str, title: str = "") -> str:
        """Usa a IA para extrair palpites específicos de especialistas (Sempre em PORTUGUÊS)."""
        prompt = (
            "Você é um Especialista em Prognósticos de Apostas Profissional.\n"
            "INSTRUÇÃO CRÍTICA: Responda SEMPRE em PORTUGUÊS (Brasil).\n\n"
            "ABAIXO ESTÁ O CONTEÚDO DE UM VÍDEO DO YOUTUBE.\n"
            "SUA MISSÃO:\n"
            "1. Identifique se o vídeo contém PALPITES DE APOSTAS reais (ex: vitórias, gols, handicap).\n"
            "2. Se o vídeo for apenas notícias, curiosidades ou entretenimento sem dicas claras de entrada, responda EXATAMENTE: 'VÍDEO SEM PALPITES'.\n"
            "3. Se houver palpites, extraia-os traduzindo tudo para PORTUGUÊS.\n"
            "4. FORMATO DE SAÍDA (Obrigatoriamente por jogo):\n"
            "   JOGO: [Time A] vs [Time B]\n"
            "   PALPITE: [O que apostar em PT-BR]\n"
            "   RAZÃO: [1 frase da justificativa em PT-BR]\n"
            "   CONFIANÇA: [Alta/Média/Baixa]\n\n"
            f"TÍTULO DO VÍDEO: {title}\n"
            f"CONTEÚDO:\n{transcript[:10000]}"
        )
        return self.llm_lite.chat(prompt, model_type="pro")

    def generate_studio_content(self, content_type: str, game_data: dict) -> str:
        """Gera conteúdo real para o Estúdio usando o LLM."""
        if not game_data:
            return "Selecione um jogo para gerar o conteúdo."

        templates = {
            "audio": "Crie um roteiro de PODCAST de 1 minuto sobre este jogo, focando em análise tática e aposta sugerida. Seja empolgante e profissional.",
            "mindmap": "Gera um código MERMAID (graph TD) que represente um mapa mental da análise deste jogo (Força, Fraqueza, Mercado, Risco).",
            "flashcards": "Crie 3 perguntas e respostas (JSON format: [{'Q': '...', 'A': '...'}]) sobre os pontos chave deste confronto para estudo de apostas.",
            "slides": "Crie uma estrutura de 3 slides em texto para uma apresentação deste jogo.",
            "pdf": "Crie um resumo executivo profissional para um relatório PDF sobre este confronto."
        }

        prompt = (
            f"Aja como um Analista de Elite. {templates.get(content_type, 'Resuma o jogo.')}\n"
            f"DADOS DO JOGO: {json.dumps(game_data)}\n"
            "RESPONDA EM PORTUGUÊS."
        )
        
        return self.llm_lite.chat(prompt, model_type="light")

    def _extract_game(self, user_id: int, text: str):
        """
        Identifica e memoriza o último jogo mencionado (heurística simples).
        """
        keywords = ["vs", "x ", " x", "contra"]
        for kw in keywords:
            if kw in text.lower():
                # Tenta capturar entorno do keyword
                idx = text.lower().find(kw)
                snippet = text[max(0, idx-15):idx+20].strip()
                self.context.set_game(user_id, snippet)
                break

    def _get_mindset_comment(self, thought: dict, response: str) -> str:
        """
        Decide qual comentário de trader adicionar baseado no raciocínio.
        """
        understand = thought.get("understand", "geral")
        if understand == "solicitar_parada":
            return self.mindset.get_stop_comment()
        if understand == "solicitar_hedge":
            return self.mindset.get_hedge_comment()
        if "sem oportunidade" in response.lower() or "não há entrada" in response.lower():
            return self.mindset.get_value_comment(has_value=False)
        if any(w in response.lower() for w in ["value bet", "valor", "odd"]):
            return self.mindset.get_value_comment(has_value=True)
        return self.mindset.get_risk_comment()

    # ── Shortcuts públicos ──
    def update_risk_profile(self, user_id: int, risk: str):
        valid = {"safe", "medium", "aggressive"}
        if risk in valid:
            self.context.update(user_id, risk_profile=risk)

    def record_bet_result(self, user_id: int, market: str, odd: float, result: str):
        self.learner.record(market, odd, result)

    def get_learning_report(self) -> str:
        return self.learner.get_insight()

    def get_context_summary(self, user_id: int) -> str:
        return self.context.summary(user_id)

    def update_target_date(self, user_id: int, date_label: str):
        self.context.update(user_id, target_date=date_label)

    def get_knowledge_context(self, user_id: int) -> str:
        return self.knowledge.get_context(user_id)

    def inject_knowledge(self, user_id: int, text: str):
        """Detecta se é link ou texto e injeta no agregador."""
        urls = self.kp.detect_urls(text)
        if urls:
            for url in urls:
                res = self.kp.process_url(url)
                if res["ok"]:
                    content_to_save = res["content"]
                    
                    # Trata YouTube de forma especial (Phase 18)
                    if res.get("type") == "youtube":
                        print(f"DEBUG CORE: Analisando tática do YouTube...")
                        tactical_summary = self._analyze_youtube_content(res["content"])
                        print(f"DEBUG CORE: LLM Analysis for YouTube video: {tactical_summary[:200]}...")
                        # Relaxed 'BAIXA QUALIDADE' filter to ensure meta-analysis is always attempted
                        content_to_save = tactical_summary
                        
                    self.knowledge.add(user_id, source=res["title"], content=content_to_save)
        else:
            # Se for texto longo (>100 chars), assume como conhecimento
            if len(text) > 100:
                res = self.kp.process_text(text)
                self.knowledge.add(user_id, source="Manual Input", content=res["content"])

    def clear_knowledge(self, user_id: int):
        self.knowledge.clear(user_id)
