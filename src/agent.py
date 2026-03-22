import google.generativeai as genai
from src.config import settings
from src.tools.news_search import search_latest_news
from src.memory import add_message, get_history
from src.logger import get_logger

logger = get_logger("agent")

genai.configure(api_key=settings.gemini_api_key)

MODEL_NAME = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = """
You are a helpful, professional AI assistant on Telegram built specifically to provide the latest news updates.
You have access to a tool called `search_latest_news` to query recent news articles from the web.
When a user asks about any topic, current events, or news, you MUST use the `search_latest_news` tool to fetch accurate and up-to-date information before responding. Do not guess the news.
Always synthesize the news articles returned by the tool into a concise, readable, and well-structured summary. Focus on the most important facts.
Include links mapping to the sources so the user can read more.
Format your responses beautifully using Markdown for Telegram (e.g., *bold*, _italic_, [text](url)).
If a user simply greets you, introduce yourself as the News Assistant and ask what topics they would like to know about today.
"""

def get_agent_response(user_id: str, user_message: str) -> str:
    logger.info("processing_user_message", user_id=user_id)
    str_user_id = str(user_id)
    
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        tools=[search_latest_news],
        system_instruction=SYSTEM_INSTRUCTION
    )
    
    history = get_history(str_user_id)
    
    formatted_history = []
    for h in history:
        formatted_history.append({'role': h['role'], 'parts': h['parts']})
        
    chat = model.start_chat(
        history=formatted_history,
        enable_automatic_function_calling=True
    )
    
    add_message(str_user_id, "user", user_message)
    
    try:
        # The AI automatically detects when to use the tool, calls it, gets results, and responds.
        response = chat.send_message(user_message)
        
        model_text = "I couldn't generate a specific response."
        if hasattr(response, 'text') and response.text:
            model_text = response.text
            
        add_message(str_user_id, "model", model_text)
        logger.info("agent_response_success", user_id=user_id)
        return model_text
    
    except Exception as e:
        logger.error("agent_execution_error", error=str(e), exc_info=True)
        return "I'm sorry, I encountered an error while trying to fetch the news for you."
