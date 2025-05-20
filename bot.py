from dotenv import load_dotenv
load_dotenv()

import os
import aiohttp
from aiohttp import web
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    ConversationState,
    MemoryStorage,
    ActivityHandler,
    TurnContext,
)
from botbuilder.schema import Activity

# --- Load Credentials and Endpoint URLs from .env ---
APP_ID = os.getenv("MicrosoftAppId", "")
APP_PASSWORD = os.getenv("MicrosoftAppPassword", "")
GENAI_API_URL = os.getenv("GENAI_API_URL")  # e.g., "https://my-ngrok-or-azure-url/ask"

# --- Bot Framework Adapter and State ---
adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)
memory = MemoryStorage()
conversation_state = ConversationState(memory)

# --- Main Bot Logic ---
class GenAIBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        user_message = (turn_context.activity.text or "").strip()
        if not user_message:
            await turn_context.send_activity("[No input received. Please enter your question.]")
            return
        # Call the GenAI backend (FastAPI) for a real AI answer
        ai_answer = await self.call_genai_api(user_message)
        await turn_context.send_activity(ai_answer)

    async def call_genai_api(self, user_message: str) -> str:
        """Calls the GenAI FastAPI backend and returns the answer string."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    GENAI_API_URL,
                    json={"question": user_message, "provider": "mixtral"},  # change provider as needed
                    timeout=20,
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("answer", "[No answer from AI backend]")
                    elif resp.status == 404:
                        return "[GenAI API error: Endpoint not found]"
                    else:
                        return f"[GenAI API error: HTTP {resp.status}]"
        except Exception as e:
            return f"[GenAI API Exception: {e}]"

bot = GenAIBot()

# --- aiohttp route for the Teams Messaging Endpoint ---
async def messages(req):
    """Handles incoming activities from Microsoft Teams (messages, etc)."""
    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")
    response = await adapter.process_activity(activity, auth_header, bot.on_turn)
    if response:
        return web.json_response(data=response.body, status=response.status)
    return web.Response(status=201)

# --- aiohttp Application Setup ---
app = web.Application()
app.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    try:
        web.run_app(app, host="0.0.0.0", port=3978)
    except Exception as error:
        raise error
