import os
from dotenv import load_dotenv
import requests

load_dotenv()

HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

payload = {
    "inputs": "Say hello to the world!"
}

resp = requests.post(HF_API_URL, headers=headers, json=payload)
try:
    data = resp.json()
    # The response can be a list of dicts with "generated_text"
    if isinstance(data, list) and "generated_text" in data[0]:
        print(data[0]["generated_text"])
    else:
        print("Raw response:", data)
except Exception as ex:
    print("Raw response:", resp.text)
