import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from src.config import settings
from src.logger import get_logger
from src.agent import get_agent_response

logger = get_logger("bot")

async def hourly_news_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    logger.info("running_hourly_job", chat_id=chat_id)
    
    # send_chat_action is invalid in Channels, removed for broadcast completely.
    prompt = "Give me a quick bulleted summary of the 3 biggest news stories right now specifically related to Agentic AI, Autonomous AI Agents, and Artificial Intelligence progress."
    reply_text = get_agent_response(str(chat_id), prompt)
    
    try:
        await context.bot.send_message(chat_id=chat_id, text=reply_text, parse_mode='Markdown')
    except Exception as parse_error:
        logger.warning("markdown_parse_failed", error=str(parse_error))
        await context.bot.send_message(chat_id=chat_id, text=reply_text)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    logger.info("start_command_received", user_id=user.id, username=user.username)
    
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()
        
    context.job_queue.run_repeating(hourly_news_job, interval=3600, first=10, chat_id=chat_id, name=str(chat_id))
    
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! I am your Agentic AI News Assistant.\n\n<b>Hourly Broadcast Enabled:</b> I am now programmed to automatically fetch and send you the top 3 biggest news headlines every 1 hour!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Just ask me about the latest news on any topic!\nExample: 'What is the latest news about Space exploration?'")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # User requested to completely disable chat so the bot operates purely as a notification channel
    await update.message.reply_text(
        "🔕 Chat input is disabled. I operate purely as a news broadcast channel!\n\n"
        "Please wait for the automated hourly news updates."
    )

def main():
    if not settings.telegram_bot_token or settings.telegram_bot_token == "your_telegram_bot_token_here":
        logger.error("telegram_bot_token_missing - Please set it in .env")
        sys.exit(1)
        
    if not settings.gemini_api_key or settings.gemini_api_key == "your_gemini_api_key_here":
        logger.error("gemini_api_key_missing - Please set it in .env")
        sys.exit(1)

    logger.info("starting_telegram_bot")
    
    application = Application.builder().token(settings.telegram_bot_token).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the automated Channel Broadcast exactly 10 seconds after boot, then every hour
    application.job_queue.run_repeating(
        hourly_news_job, 
        interval=3600, 
        first=10, 
        chat_id="@flashnews1810",
        name="channel_broadcast"
    )

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
