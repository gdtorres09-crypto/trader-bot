from agents.betting_analyst import BettingAnalyst
from integrations.telegram_bot import TelegramBot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import asyncio
import logging

# Configurar fuso horário para Brasília (UTC-3)
# Em sistemas Windows, o nome do fuso pode variar, usaremos offset manual ou pytz se necessário.
# Por simplicidade, usaremos a hora local do sistema se estiver correta.

# Configurar log para arquivo e console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_errors.log"),
        logging.StreamHandler()
    ]
)

def main():
    print("Iniciando SPORTS_BETTING_ANALYST_AI com Agendador...")
    
    agent = BettingAnalyst()
    bot = TelegramBot(agent)
    
    # Configurar Agendador
    scheduler = AsyncIOScheduler()
    
    # Agendar para as 08:00 todos os dias
    # Nota: O bot.run() do python-telegram-bot v20+ usa asyncio por baixo.
    # Mas o run_polling() é bloqueante. Precisamos integrar o scheduler.
    
    async def run_bot():
        # Inicializar a aplicação do bot sem rodar o polling ainda
        from telegram.ext import ApplicationBuilder
        app = ApplicationBuilder().token(bot.token).build()
        
        # Adicionar handlers (repetindo a lógica do bot.run() de forma injetada)
        from telegram.ext import CommandHandler, MessageHandler, filters
        app.add_handler(MessageHandler(filters.ALL, bot.debug_all), group=-1) 
        app.add_handler(CommandHandler("start", bot.start))
        app.add_handler(CommandHandler("menu", bot.start))
        app.add_handler(CommandHandler("valuebets", bot.value_bets))
        app.add_handler(CommandHandler("banca", bot.bankroll))
        app.add_handler(CommandHandler("odds", bot.odds))
        app.add_handler(CommandHandler("ev", bot.ev))
        app.add_handler(CommandHandler("ligas", bot.ligas))
        app.add_handler(CommandHandler("sharp", bot.sharp))
        app.add_handler(CommandHandler("previsao", bot.prevision))
        app.add_handler(CommandHandler("live", bot.live))
        app.add_handler(CommandHandler("controle", bot.control))
        app.add_handler(CommandHandler("agenda", bot.agenda))
        app.add_handler(CommandHandler("jogadores", bot.players))
        app.add_handler(CommandHandler("estrategias", bot.strategies))
        app.add_handler(CommandHandler("trade", bot.trade))
        app.add_handler(CommandHandler("aprendizado", bot.learning))
        app.add_handler(CommandHandler("alavancagem", bot.leverage))
        app.add_handler(CommandHandler("insider", bot.insider))
        app.add_handler(CommandHandler("historico", bot.history))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), bot.handle_message))
        app.add_handler(MessageHandler(filters.VOICE, bot.handle_voice))
        
        # Configurar Job agendado (Antigo: 08:00 diário -> Novo: A cada 10 minutos)
        from core.auto_trader import AutoTrader
        from integrations.youtube_monitor import YouTubeMonitor
        trader = AutoTrader(agent)
        yt_monitor = YouTubeMonitor(agent.elite.kp)
        
        async def automatic_task():
            # 1. Ciclo de Trading (Odds API)
            signals = await trader.run_analysis_cycle()
            for msg in signals:
                await bot.send_broadcast(app.bot, msg)
            
            # 2. Ciclo YouTube
            new_vids = yt_monitor.check_for_new_videos()
            for vid in new_vids:
                print(f"Processando vídeo automático: {vid['title']}")
                # Injeta como se o usuário tivesse enviado o link
                agent.elite.inject_knowledge(bot.user_id, vid['url'])
                # A próxima análise do ciclo de trading já terá esse conhecimento contextuado.

        scheduler.add_job(automatic_task, 'interval', minutes=10)
        scheduler.start()
        
        print("Bot e AutoTrader (Ciclo: 10 min) iniciados!")
        
        async with app:
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            
            # Manter rodando
            while True:
                await asyncio.sleep(3600)

    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\nDesligando agente...")

if __name__ == "__main__":
    main()
