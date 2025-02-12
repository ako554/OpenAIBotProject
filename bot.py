import openai
import os
import time
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv("key.env")

# Récupérer la clé API OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = "asst_KjtbsY41MGXV5nMzlHGJc6tc"

# Vérifier si la clé API est bien définie
if not OPENAI_API_KEY:
    raise ValueError("❌ ERREUR : La clé API OpenAI n'est pas définie dans key.env")

# Créer un client OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Réutiliser un thread pour l'optimisation
THREAD_ID = None

# Initialiser Flask
app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    """Route API pour interroger l'assistant"""
    global THREAD_ID

    # Vérifier si un message est bien envoyé
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Message vide"}), 400

    try:
        # Créer un thread unique si nécessaire
        if THREAD_ID is None:
            THREAD_ID = client.beta.threads.create().id

        # Ajouter le message utilisateur
        client.beta.threads.messages.create(
            thread_id=THREAD_ID,
            role="user",
            content=user_message
        )

        # Lancer l'exécution de l'assistant
        run = client.beta.threads.runs.create(
            thread_id=THREAD_ID,
            assistant_id=ASSISTANT_ID
        )

        # Attendre la réponse
        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=THREAD_ID, run_id=run.id)
            if run_status.status == "completed":
                break
            time.sleep(0.3)  # Vérification toutes les 300ms

        # Récupérer la réponse
        messages = client.beta.threads.messages.list(thread_id=THREAD_ID)
        if messages.data:
            first_message = messages.data[0]
            if first_message.content and isinstance(first_message.content, list):
                response_text = " ".join(block.text.value for block in first_message.content if hasattr(block, "text"))
                return jsonify({"response": response_text})

        return jsonify({"error": "Aucune réponse reçue"}), 500

    except openai.OpenAIError as e:
        return jsonify({"error": str(e)}), 500

# Lancer le serveur Flask sur Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
