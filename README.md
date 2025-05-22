# GenAI Teams QA Bot

A unified **GenAI-powered Q&A bot** for Microsoft Teams, supporting multiple LLMs (OpenAI GPT-4o, Mixtral, Zephyr, and more) with an easy-to-use FastAPI backend.

## 🚀 Features

- **Microsoft Teams Integration:** Chat directly in Teams, get instant AI answers.
- **Supports Multiple LLMs:** Easily switch between OpenAI, HuggingFace Mixtral, and Public Zephyr models.
- **Easy Cloud Deployment:** Fully configured for Azure App Service.
- **Configurable via Environment Variables:** No need to redeploy to change models.
- **REST API:** `/ask` endpoint for Q&A from any client.

## 🌐 Live Demo in Azure and link to Fast-Api (Swagger ui testing ground) 

[![genai-qa.gif](https://i.postimg.cc/Gh2sP0Qg/genai-qa.gif)](https://postimg.cc/jCp5KFBy)

https://genai-teams-qa-frcfbpf4e5gcekax.canadaeast-01.azurewebsites.net/docs

--> In /ask -> Try out
{
  "question": "string", ## change this string to any message
  "provider": "openai"
}

--> Execute
## Screenshot
[![image.png](https://i.postimg.cc/NjHD4w0k/image.png)](https://postimg.cc/cvdfx2wv)

## Screenshot of the bot working on Azure
[![image.png](https://i.postimg.cc/x8GPGjCk/image.png)](https://postimg.cc/dZ1dwYGv)

---

## ⚡️ Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/XessX/genai-teams-qa.git
cd genai-teams-qa
2. Set up your .env file
Add the following to your .env (never commit to git!):


OPENAI_API_KEY=sk-...
HUGGINGFACE_TOKEN=hf_...
MicrosoftAppId=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
MicrosoftAppPassword=your_bot_secret
GENAI_API_URL= # Leave blank unless using remote API
LLM_PROVIDER=openai  # or mixtral or public
3. Local Development

pip install -r requirements.txt
uvicorn main:app --reload
Visit http://localhost:8000/docs to try the API.

Test Teams bot using Azure Bot Framework Emulator or deploy to Azure.

🛠️ Azure Deployment
Deploy using local Git, or via GitHub Actions.

Set these Environment Variables in Azure Portal:

OPENAI_API_KEY

HUGGINGFACE_TOKEN

MicrosoftAppId

MicrosoftAppPassword

LLM_PROVIDER (e.g., openai)

Startup Command:

gunicorn --bind=0.0.0.0 --timeout 600 --worker-class uvicorn.workers.UvicornWorker main:app
Test at:
https://<your-app-name>.azurewebsites.net/docs

📝 How to Switch LLM Providers
Just change the LLM_PROVIDER environment variable (openai, mixtral, public) in Azure—no code changes required!

💬 Microsoft Teams Integration
Register your bot in Azure Bot Service.

Enable Microsoft Teams channel.

Upload the Teams manifest (see /teams-manifest/ folder).

Chat with your bot in Teams!

🖼️ Screenshots
Add screenshots or gifs here to showcase your bot in action!

🛡️ License
MIT License
(c) 2025 Al Jubair Hossain / XessX

🤝 Contributions
PRs, issues, and suggestions are welcome!

Questions? Ping me on LinkedIn or open a GitHub Issue.