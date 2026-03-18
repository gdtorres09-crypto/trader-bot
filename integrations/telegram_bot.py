import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_USER_ID
from integrations.llm_provider import LLMProvider
import os

# Config de Log
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

class TelegramBot:
    def __init__(self, agent):
        self.agent = agent
        self.token = TELEGRAM_BOT_TOKEN
        self.user_id = int(TELEGRAM_USER_ID) if TELEGRAM_USER_ID else None
        self.llm = LLMProvider()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        incoming_id = update.effective_user.id
        print(f"DEBUG: START recebido de ID {incoming_id}")
        
        if self.user_id and incoming_id != self.user_id:
            print(f"DEBUG: Acesso NEGADO para ID {incoming_id}. O ID configurado é {self.user_id}")
            await update.message.reply_text("Acesso negado.")
            return

        keyboard = [
            ['/jogos_hoje', '/valuebets'],
            ['/banca', '/historico'],
            ['/relatorio', '/menu']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "🤖 *SPORTS_BETTING_ANALYST_AI*\n\n"
            "Olá! Sou seu analista pessoal. Além dos comandos, você pode conversar comigo normalmente ou me mandar áudios!",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa mensagens de texto normais usando o LLM com histórico e mindset trader."""
        incoming_id = update.effective_user.id
        user_text = update.message.text
        print(f"DEBUG: Recebida mensagem de {incoming_id}: {user_text}")

        if self.user_id and incoming_id != self.user_id:
            print(f"DEBUG: Id {incoming_id} EXCLUÍDO (Permitido: {self.user_id})")
            return

        try:
            print("DEBUG: Enviando digitando...")
            await update.message.chat.send_action(action="typing")
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.agent.db.save_chat_message, incoming_id, "user", user_text)
            history = await loop.run_in_executor(None, self.agent.db.get_chat_history, incoming_id, 6)
            
            intent = self.agent.intent_parser.parse(user_text)
            target_date, time_label = self.agent.time_intel.parse_time_intent(incoming_id, user_text)
            risk_level = self.agent.human_intel.adapt_risk_preference(incoming_id, user_text)
            date_str = self.agent.time_intel.get_date_string(target_date)
            print(f"DEBUG: Intent: {intent}, Time: {time_label}, Risk: {risk_level}")
            
            # Atualiza perfil no Core
            self.agent.elite.update_risk_profile(incoming_id, risk_level)
            self.agent.elite.update_target_date(incoming_id, time_label)

            # ── INJEÇÃO DE CONHECIMENTO (Phase 17) ─────────────────────────
            # Se o usuário mandou link ou texto longo, alimenta a base de expert
            self.agent.elite.inject_knowledge(incoming_id, user_text)

            # ── FLUXO DE RESPOSTA ───────────────────────────────────────────
            response_to_send = ""
            
            if intent == "bankroll":
                response_to_send = self.agent.get_bankroll_status()
            
            elif intent != "chat":
                # MODO ANALÍTICO / TRADER
                sport_context = self._extract_sport_context(user_text)
                bankroll_info = self.agent.get_bankroll_status()
                
                # Buscar jogos reais
                match_context_str = "NENHUM JOGO PARA HOJE (CONSULTE HISTÓRICO)."
                if intent != "history":
                    api_sport = "football"
                    if "nba" in sport_context.lower(): api_sport = "nba"
                    elif "ucl" in sport_context.lower(): api_sport = "ucl"
                    elif "epl" in sport_context.lower(): api_sport = "epl"
                    
                    days_off = 0 if time_label == "hoje" else 1
                    raw_matches = self.agent.elite.api.get_upcoming_matches(api_sport, days_offset=days_off)
                    if raw_matches:
                        match_lines = [f"- {rm['home']} vs {rm['away']} | Liga: {rm['league']} | Data: {rm['date']} {rm['time']}" for rm in raw_matches[:10]]
                        match_context_str = "\n".join(match_lines)

                elite_rules = (
                    "SISTEMA: TRADER ESPORTIVO PROFISSIONAL AUTOMÁTICO\n"
                    "1. MÚLTIPLOS MERCADOS: Analise Gols, Escanteios, Cartões e Handicap (Futebol). "
                    "Analise Ritmo (Pace), Props de Jogadores, Double-Double e Handicap (NBA).\n"
                    "2. PROCESSO DE ANÁLISE: Avalie forma recente, médias, odds e identifique Valor (EV+).\n"
                    "3. FORMATO MANDATÓRIO (ESCOLHA 3 OPÇÕES): Toda análise deve entregar:\n"
                    "   1️⃣ Aposta SEGURA (Alta probabilidade/Green)\n"
                    "   2️⃣ Aposta de VALOR (EV+ identificado)\n"
                    "   3️⃣ Aposta OUSADA (Alto retorno/Risco alto)\n"
                    "4. JUSTIFICATIVA: Use raciocínio de trader profissional. Proibido templates."
                )

                full_context = (
                    f"{elite_rules}\n"
                    f"ESPORTE: {sport_context}. Data: {date_str} ({time_label}).\n"
                    f"JOGOS REAIS DISPONÍVEIS:\n{match_context_str}\n"
                    f"{self.agent.elite.get_knowledge_context(incoming_id)}\n\n"
                    f"Perfil: {risk_level}. Banca: {bankroll_info}."
                )

                # Loop de regeneração com Timeout
                max_retries = 2
                for attempt in range(max_retries + 1):
                    try:
                        raw_ai_response = await asyncio.wait_for(
                            asyncio.to_thread(self.llm.chat, user_text, history=history, context=full_context, model_type="light"),
                            timeout=45.0
                        )
                        # Passar pelo processamento do Core (Validação/Mindset)
                        processed_response = self.agent.elite.process(
                            user_id=incoming_id,
                            user_text=user_text,
                            intent=intent,
                            raw_response=raw_ai_response
                        )
                        
                        if "Não há jogos confiáveis disponíveis hoje." in processed_response:
                            if "NENHUM JOGO PARA HOJE" in match_context_str: break
                            continue
                        
                        response_to_send = processed_response
                        break
                    except asyncio.TimeoutError:
                        if attempt == max_retries:
                            response_to_send = "O servidor de IA está lento. Por favor, tente novamente em alguns segundos."
                        continue

            else:
                # MODO CONVERSA
                profile = self.agent.human_intel.get_user_profile(incoming_id)
                bankroll_info = self.agent.get_bankroll_status()
                full_context = f"Saldo: {bankroll_info}. Perfil Risco: {profile['risk_level']}. Data Hoje: {date_str}."
                raw_ai_response = self.llm.chat(user_text, history=history, context=full_context, model_type="light")
                response_to_send = self.agent.elite.process(incoming_id, user_text, intent, raw_ai_response)

            # ── ENVIAR RESPOSTA ──────────────────────────────────────────────
            print(f"DEBUG: Enviando resposta final ({len(response_to_send)} chars)...")
            try:
                await update.message.reply_text(response_to_send, parse_mode='Markdown')
            except:
                await update.message.reply_text(response_to_send)

            await loop.run_in_executor(None, self.agent.db.save_chat_message, incoming_id, "assistant", response_to_send)

        except Exception as e:
            print(f"DEBUG ERROR: {str(e)}")
            import traceback
            traceback.print_exc()

    def _extract_sport_context(self, text: str) -> str:
        """
        Detecta o esporte/liga mencionado pelo usuário para guiar o LLM.
        Se nenhum esporte for detectado, assume futebol (padrão).
        """
        text_lower = text.lower()
        sports_map = [
            # Basquete
            (["nba", "basketball", "basquete", "basquetbol", "lakers", "celtics", "warriors", "bulls",
              "knicks", "nets", "heat", "bucks", "nuggets"], "NBA - Basketball Americano"),
            # Futebol Americano
            (["nfl", "super bowl", "futebol americano", "patriots", "cowboys", "chiefs", "rams",
              "touchdown", "quarterback"], "NFL - Futebol Americano"),
            # Tênis
            (["tênis", "atp", "wta", "wimbledon", "roland garros", "us open", "australian open",
              "federer", "djokovic", "nadal", "alcaraz", "sinner"], "Tênis - ATP/WTA"),
            # Baseball
            (["mlb", "baseball", "beisebol", "yankees", "dodgers", "red sox"], "MLB - Baseball"),
            # Hockey
            (["nhl", "hockey", "gelo"], "NHL - Hockey no Gelo"),
            # Fórmula 1
            (["f1", "fórmula 1", "formula 1", "grande prêmio", "gp", "hamilton", "verstappen",
              "alonso", "ferrari", "mercedes"], "Fórmula 1"),
            # MMA/UFC
            (["ufc", "mma", "luta", "octógono", "boxe", "boxing", "fight"], "MMA/UFC"),
            # Futebol Europeu específico
            (["premier league", "epl", "arsenal", "chelsea", "manchester", "liverpool"], "EPL - Premier League"),
            (["champions league", "ucl", "liga dos campeões", "liga dos campeos"], "UCL - Champions League"),
            (["la liga", "barcelona", "real madrid"], "La Liga"),
            (["serie a", "juventus", "milan", "inter"], "Serie A"),
            # Futebol Brasileiro
            (["brasileirão", "brasileirao", "série a", "copa do brasil", "libertadores",
              "flamengo", "palmeiras", "corinthians", "são paulo", "fluminense", "vasco",
              "atlético", "cruzeiro", "internacional", "grêmio", "botafogo"], 
             "Futebol Brasileiro"),
        ]
        for keywords, label in sports_map:
            if any(kw in text_lower for kw in keywords):
                return label
        # Padrão: futebol geral
        return "Football"

    async def strategies(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.user_id and update.effective_user.id != self.user_id:
            return
        report = self.agent.get_strategy_report()
        await update.message.reply_text(report, parse_mode='Markdown')


    async def trade(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.user_id and update.effective_user.id != self.user_id:
            return
        report = self.agent.get_trade_report()
        await update.message.reply_text(report, parse_mode='Markdown')

    async def learning(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.user_id and update.effective_user.id != self.user_id:
            return
        report = self.agent.get_learning_report()
        await update.message.reply_text(report, parse_mode='Markdown')

    async def leverage(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.user_id and update.effective_user.id != self.user_id:
            return
        report = self.agent.get_leverage_report()
        await update.message.reply_text(report, parse_mode='Markdown')

    async def insider(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.user_id and update.effective_user.id != self.user_id:
            return
        report = self.agent.get_insider_report()
        await update.message.reply_text(report, parse_mode='Markdown')

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa mensagens de voz."""
        if self.user_id and update.effective_user.id != self.user_id:
            return
            
        await update.message.reply_text("🎙️ Recebi seu áudio! Estou processando...")
        
        file = await context.bot.get_file(update.message.voice.file_id)
        file_path = "voice_msg.ogg"
        await file.download_to_drive(file_path)
        
        transcription = self.llm.transcribe_audio(file_path)
        # Por enquanto, mostramos a transcrição e respondemos
        response = self.llm.chat(f"[Transcrição de Áudio]: {transcription}")
        await update.message.reply_text(f"📝 *O que eu entendi:* {transcription}\n\n🤖 *Minha resposta:* {response}", parse_mode='Markdown')
        
        if os.path.exists(file_path):
            os.remove(file_path)

    async def send_broadcast(self, bot, message: str):
        """Envia uma mensagem direta para o administrador (user_id)."""
        if self.user_id:
            try:
                await bot.send_message(chat_id=self.user_id, text=message, parse_mode='Markdown')
            except Exception as e:
                print(f"Erro ao enviar broadcast: {e}")

    async def send_scheduled_tips(self, bot):
        """Envia as dicas diárias agendadas."""
        if not self.user_id:
            return
            
        report = self.agent.get_value_bets_report()
        personalized_intro = "☀️ *BOM DIA! Dicas da Betano para hoje (08:00):*\n\n"
        await bot.send_message(chat_id=self.user_id, text=personalized_intro + report, parse_mode='Markdown')

    async def value_bets(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.user_id and update.effective_user.id != self.user_id:
            return
        report = self.agent.get_value_bets_report()
        await update.message.reply_text(report, parse_mode='Markdown')

    async def bankroll(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.user_id and update.effective_user.id != self.user_id:
            return
        status = self.agent.get_bankroll_status()
        await update.message.reply_text(status, parse_mode='Markdown')

    async def odds(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.user_id and update.effective_user.id != self.user_id:
            return
        report = self.agent.get_odds_movement_report()
        await update.message.reply_text(report, parse_mode='Markdown')

    async def ev(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.user_id and update.effective_user.id != self.user_id:
            return
        report = self.agent.get_ev_report()
        await update.message.reply_text(report, parse_mode='Markdown')

    async def ligas(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.user_id and update.effective_user.id != self.user_id:
            return
        report = self.agent.get_league_profit_report()
        await update.message.reply_text(report, parse_mode='Markdown')

    async def sharp(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.user_id and update.effective_user.id != self.user_id:
            return
        report = self.agent.get_sharp_report()
        await update.message.reply_text(report, parse_mode='Markdown')

    async def prevision(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.user_id and update.effective_user.id != self.user_id:
            return
        report = self.agent.get_ml_prediction_report()
        await update.message.reply_text(report, parse_mode='Markdown')

    async def live(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.user_id and update.effective_user.id != self.user_id:
            return
        report = self.agent.get_live_report()
        await update.message.reply_text(report, parse_mode='Markdown')

    async def control(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.user_id and update.effective_user.id != self.user_id:
            return
        report = self.agent.get_tilt_report()
        await update.message.reply_text(report, parse_mode='Markdown')

    async def agenda(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.user_id and update.effective_user.id != self.user_id:
            return
        report = self.agent.get_fixture_report()
        await update.message.reply_text(report, parse_mode='Markdown')

    async def players(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.user_id and update.effective_user.id != self.user_id:
            return
        report = self.agent.get_players_report()
        await update.message.reply_text(report, parse_mode='Markdown')

    async def history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        h_report = self.agent.get_history_report()
        await update.message.reply_text(h_report, parse_mode='Markdown')

    async def debug_all(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"DEBUG: UPDATE RECEBIDA: {update.to_dict()}")

    def run(self):
        if not self.token:
            print("TELEGRAM_BOT_TOKEN não configurado!")
            return
            
        app = ApplicationBuilder().token(self.token).build()
        
        app.add_handler(MessageHandler(filters.ALL, self.debug_all), group=-1) # Catch-all em grupo separado
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("menu", self.start))
        app.add_handler(CommandHandler("valuebets", self.value_bets))
        app.add_handler(CommandHandler("banca", self.bankroll))
        app.add_handler(CommandHandler("historico", self.history))
        app.add_handler(CommandHandler("reset_conhecimento", self.reset_knowledge))
        
        # Handlers para conversa e áudio
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))
        app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, self.handle_voice))
        
        print("Bot iniciado com suporte a IA e Áudio...")
        app.run_polling()
    async def reset_knowledge(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        self.agent.elite.clear_knowledge(user_id)
        await update.message.reply_text("✅ Memória de conhecimento externo limpa com sucesso!")
