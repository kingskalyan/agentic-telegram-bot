import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from src.config import settings
from src.logger import get_logger
from src.agent import get_agent_response

logger = get_logger("bot")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info("start_command_received", user_id=user.id, username=user.username)
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! I am your Agentic AI News Assistant. Ask me about the latest news on any topic!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Just ask me about the latest news on any topic!\nExample: 'What is the latest news about Space exploration?'")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_message = update.message.text
    
    logger.info("message_received", user_id=user_id, text_length=len(user_message))
    
    # Send a typing indicator while the AI thinks and fetches news
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    # Process message through the Agent (which will use News tool internally if needed)
    reply_text = get_agent_response(user_id, user_message)
    
    try:
        await update.message.reply_text(reply_text, parse_mode='Markdown')
    except Exception as parse_error:
        logger.warning("markdown_parse_failed", error=str(parse_error))
        # Fall back to plain text if Telegram's strict Markdown parser crashes
        await update.message.reply_text(reply_text)

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

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
