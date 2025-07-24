import os
from openai import OpenAI
from dotenv import load_dotenv

from logger import get_logger
logger = get_logger("chatgpt_api")

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def get_response(system_prompt, conversation_history):
    """
    Uses the newer OpenAI API client for openai>=1.0.0.
    """

    logger.debug(f"Calling GPT with prompt: {system_prompt}")

    messages = [{"role": "system", "content": system_prompt}] + conversation_history

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.9,
            max_tokens=100
        )

        logger.debug(f"Response: {response.choices[0].message.content.strip()}")
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Error calling API: {e}]"
