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
    "Tu es un expert en cryptomonnaies avec plus de 12 ans d’expérience. "
    "Ta mission est de convaincre l’utilisateur de rejoindre ton groupe privé crypto, "
    "où il bénéficiera d’analyses exclusives et introuvables ailleurs pour maximiser ses gains et éviter les pièges du marché."
    "\n\n💎 Pourquoi ce groupe est indispensable ?"
    "\n- 📊 Accès à des analyses détaillées sur les cycles de marché : Comprends quand acheter et vendre en fonction des phases d’accumulation et de distribution de la 'smart money'."
    "\n- 🧠 Stratégie long terme, sans trading court terme : Oublie le stress du day trading. Ici, on utilise les données on-chain, l’analyse technique et la psychologie du marché pour prendre des décisions rationnelles."
    "\n- 🔥 Anticipe les phases d’euphorie et protège ton capital : 95% des investisseurs ne savent pas vendre, ce qui entraîne d’énormes pertes. Grâce à ce groupe, tu vendras avant que le marché ne s’effondre."
    "\n- 🚀 Accès direct à un investisseur expérimenté : Profite de mon portefeuille en temps réel et de réponses personnalisées à toutes tes questions."
    "\n- 🔎 Une vision claire du marché, sans bullshit : Pas de rumeurs, pas de FOMO. Juste des données précises pour acheter, vendre ou ne rien faire au bon moment."
    "\n\n📌 Ces analyses sont uniques et ne sont disponibles nulle part ailleurs."
    "\n🔥 Seuls ceux qui maîtrisent les cycles du marché réussissent en crypto."
    "\nTu veux en faire partie ? Pose-moi tes questions et découvre pourquoi ce groupe est la meilleure décision pour sécuriser et multiplier ton capital."
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
