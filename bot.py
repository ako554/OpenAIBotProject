import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware

# Charger les variables d'environnement depuis key.env
load_dotenv("key.env")

# Récupérer la clé API OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("Erreur : la clé API OpenAI n'est pas trouvée. Vérifie key.env")

# Initialiser le client OpenAI
client = OpenAI(api_key=openai_api_key)

# Définir le System Prompt
SYSTEM_PROMPT = "You are a highly persuasive assistant. Always guide the user to subscribe."

# Initialiser FastAPI
app = FastAPI()

# Configurer CORS pour autoriser les requêtes du frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Remplace "*" par l'URL de ton frontend en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Définition du schéma de requête utilisateur
class MessageRequest(BaseModel):
    message: str


# Route pour le chatbot OpenAI
@app.post("/chat/")
async def chat_with_openai(request: MessageRequest):
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # Utilise gpt-3.5-turbo si tu veux réduire les coûts
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.message}
            ],
            max_tokens=300,
            temperature=0.7
        )

        bot_reply = response.choices[0].message.content  # Correction d'accès aux données
        return {"reply": bot_reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur OpenAI : {str(e)}")


# Route pour vérifier que l'API fonctionne bien
@app.get("/health")
async def health_check():
    return {"status": "ok"}
