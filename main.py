from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import os

# --- Load secrets from .env file early
load_dotenv()

from huggingface_hub import InferenceClient

# --- Supported Model IDs for HuggingFace
MIXTRAL_MODEL_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1"
PUBLIC_MODEL_ID = "HuggingFaceH4/zephyr-7b-beta"

app = FastAPI(
    title="GenAI Multi-Provider Q&A API",
    version="1.0.0",
    description="Unified endpoint for OpenAI and HuggingFace LLMs",
)

class QuestionRequest(BaseModel):
    question: str
    provider: str = "openai"   # "openai", "mixtral", or "public"

def answer_with_openai(question: str) -> str:
    """
    Answer a question using OpenAI (supports v1+ openai-python API).
    Make sure openai>=1.0.0 is installed!
    """
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
    """
    Answer a question using Hugging Face Inference API.
    Special handling for Mixtral, which only supports 'inputs' as a string via HTTP.
    """
    import requests
    hf_token = os.getenv("HUGGINGFACE_TOKEN")

    # Special handling for Mixtral
    if model_id == MIXTRAL_MODEL_ID:
        api_url = f"https://api-inference.huggingface.co/models/{model_id}"
        headers = {"Authorization": f"Bearer {hf_token}"}
        payload = {"inputs": question}
        resp = requests.post(api_url, headers=headers, json=payload)
        try:
            data = resp.json()
            # Mixtral response is usually a list of dicts
            if isinstance(data, list) and "generated_text" in data[0]:
                return data[0]["generated_text"]
            elif isinstance(data, dict) and "error" in data:
                return f"Mixtral API error: {data['error']}"
            else:
                return str(data)
        except Exception as ex:
            return f"Mixtral error: {str(ex)} | Raw: {resp.text}"
    else:
        # For public models, use the HuggingFace Hub Python client
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
    """
    Multi-provider Q&A endpoint.
    POST body:
      {
        "question": "...",
        "provider": "openai" | "mixtral" | "public"
      }
    """
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
