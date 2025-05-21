import os
from dotenv import load_dotenv

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# HuggingFace/GenAI Imports
from huggingface_hub import InferenceClient

# Bot Framework Imports
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    ConversationState,
    MemoryStorage,
    ActivityHandler,
    TurnContext,
)
from botbuilder.schema import Activity

import aiohttp

# --- HuggingFace Model IDs
MIXTRAL_MODEL_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1"
PUBLIC_MODEL_ID = "HuggingFaceH4/zephyr-7b-beta"

# --- FastAPI App
app = FastAPI(
    title="GenAI Multi-Provider Q&A API with Teams Integration",
    version="1.0.0",
    description="Unified endpoint for OpenAI and HuggingFace LLMs, plus Teams bot integration.",
)

# --- GenAI API Logic
class QuestionRequest(BaseModel):
    question: str
    provider: str = "openai"   # "openai", "mixtral", or "public"

def answer_with_openai(question: str) -> str:
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": question}],
        )
        answer = response.choices[0].message.content
        return answer.strip()
    except Exception as e:
        import traceback
        return f"OpenAI Error: {type(e).__name__}: {str(e)}\n{traceback.format_exc()}"

def answer_with_hf_api(question: str, model_id: str) -> str:
    import requests
    hf_token = os.getenv("HUGGINGFACE_TOKEN")
    if model_id == MIXTRAL_MODEL_ID:
        api_url = f"https://api-inference.huggingface.co/models/{model_id}"
        headers = {"Authorization": f"Bearer {hf_token}"}
        payload = {"inputs": question}
        resp = requests.post(api_url, headers=headers, json=payload)
        try:
            data = resp.json()
            if isinstance(data, list) and "generated_text" in data[0]:
                return data[0]["generated_text"]
            elif isinstance(data, dict) and "error" in data:
                return f"Mixtral API error: {data['error']}"
            else:
                return str(data)
        except Exception as ex:
            return f"Mixtral error: {str(ex)} | Raw: {resp.text}"
    else:
        client = InferenceClient(model=model_id, token=hf_token)
        try:
            answer = client.text_generation(
                prompt=question,
                max_new_tokens=256,
                temperature=0.2,
                stream=False,
            )
            return answer.strip()
        except Exception as e:
            import traceback
            msg = str(e)
            return f"HuggingFace Error for {model_id}: {type(e).__name__}: {msg}\n{traceback.format_exc()}"

@app.post("/ask")
async def ask(request: QuestionRequest):
    try:
        provider = request.provider.lower()
        if provider == "openai":
            answer = answer_with_openai(request.question)
        elif provider == "mixtral":
            answer = answer_with_hf_api(request.question, MIXTRAL_MODEL_ID)
        elif provider == "public":
            answer = answer_with_hf_api(request.question, PUBLIC_MODEL_ID)
        else:
            answer = "Unknown provider (choose: openai, mixtral, or public)"
        return {"answer": answer}
    except Exception as ex:
        import traceback
        return JSONResponse(
            status_code=500,
            content={"answer": f"Unhandled Error: {type(ex).__name__}: {str(ex)}\n{traceback.format_exc()}"}
        )

# --- Teams Bot Integration
APP_ID = os.getenv("MicrosoftAppId", "")
APP_PASSWORD = os.getenv("MicrosoftAppPassword", "")
GENAI_API_URL = os.getenv("GENAI_API_URL", "")

# Set the default LLM provider for Teams (from env, or fallback)
DEFAULT_LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)
memory = MemoryStorage()
conversation_state = ConversationState(memory)

class GenAIBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        user_message = (turn_context.activity.text or "").strip()
        if not user_message:
            await turn_context.send_activity("[No input received. Please enter your question.]")
            return
        ai_answer = await self.call_genai_api(user_message)
        await turn_context.send_activity(ai_answer)

    async def call_genai_api(self, user_message: str) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    GENAI_API_URL or "http://localhost:8000/ask",
                    json={
                        "question": user_message,
                        "provider": DEFAULT_LLM_PROVIDER  # <--- use env/configurable provider
                    },
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

@app.post("/api/messages")
async def teams_messages(request: Request):
    body = await request.json()
    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")
    response = await adapter.process_activity(activity, auth_header, bot.on_turn)
    if response:
        return Response(content=response.body, status_code=response.status, media_type="application/json")
    return Response(status_code=201)

@app.get("/")
def root():
    return {"status": "App is running and ready for requests."}

# Local dev only (not used in Azure)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
