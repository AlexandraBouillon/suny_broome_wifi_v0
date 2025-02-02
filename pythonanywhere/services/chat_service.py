import openai
from config import Config, logger

def get_ai_response(user_input, context=""):
    """Get a response from OpenAI for TJ"""
    try:
        if not Config.CHAT_ENABLED:
            return "Chat is currently disabled. Please configure the OpenAI API key."

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"You are TJ, an assistant for a Raspberry Pi Pico W LED Control Panel. {context}"
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        )
        return completion.choices[0].message['content']
    except openai.error.RateLimitError:
        logger.error("OpenAI API rate limit exceeded")
        return "Error: API rate limit exceeded. Please try again later."
    except openai.error.AuthenticationError:
        logger.error("OpenAI API authentication failed")
        return "Error: API authentication failed. Please check your API key."
    except openai.error.InvalidRequestError as e:
        logger.error(f"OpenAI API invalid request: {str(e)}")
        return f"Error: Invalid request - {str(e)}"
    except Exception as e:
        logger.error(f"Error getting AI response: {type(e).__name__}: {str(e)}")
        return f"Error: {str(e)}" 