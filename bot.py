import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ✅ Charger key.env
load_dotenv("key.env")

# ✅ Vérifier si la clé API OpenAI est bien chargée
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("❌ ERREUR : La clé API OpenAI n'est pas trouvée. Vérifie key.env !")
    exit(1)

# ✅ Initialiser le client OpenAI
client = openai.OpenAI(api_key=openai_api_key)

# ✅ System Prompt optimisé pour vendre un abonnement crypto
SYSTEM_PROMPT = (
    "Tu es un assistant expert en cryptomonnaies et en analyse de marché. "
    "Ton objectif est de convaincre l'utilisateur de s'abonner à un service premium "
    "offrant des analyses on-chain exclusives, des signaux de trading, des stratégies avancées "
    "et un accès à un groupe privé où des experts partagent leurs insights et transactions en temps réel. "
    "Utilise des arguments solides sur la rentabilité, la gestion des risques, la psychologie du marché "
    "et les opportunités à long terme pour persuader l'utilisateur de rejoindre l'abonnement. "
    "Ne sois pas trop insistant, mais guide toujours la conversation vers l'intérêt de souscrire."
)

# ✅ Initialiser FastAPI
app = FastAPI()

# ✅ Configurer CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔥 Modifier "*" par l'URL frontend en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Définition du modèle de requête utilisateur
class MessageRequest(BaseModel):
    message: str

# ✅ Route principale du chatbot OpenAI
@app.post("/chat/")
async def chat_with_openai(request: MessageRequest):
    try:
        print(f"➡️ Requête reçue : {request.message}")  # Debug

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.message}
            ],
            max_tokens=300,
            temperature=0.7
        )

        print(f"✅ Réponse OpenAI brute : {response}")  # Debug

        bot_reply = response.choices[0].message.content
        return {"reply": bot_reply}

    except openai.OpenAIError as oe:
        print(f"❌ Erreur OpenAI : {oe}")  # Debug
        raise HTTPException(status_code=502, detail=f"Erreur OpenAI : {str(oe)}")

    except Exception as e:
        print(f"❌ Erreur interne : {e}")  # Debug
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")

# ✅ Route pour vérifier que l'API fonctionne bien
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# ✅ Lancer le serveur Uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
