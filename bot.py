from flask import Flask, request, jsonify
import openai
import os
import time

# Configuration de l'API OpenAI
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

# ID de ton assistant OpenAI
assistant_id = "asst_KjtbsY41MGXV5nMzlHGJc6tc"

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "API Flask fonctionne",
        "routes": [rule.rule for rule in app.url_map.iter_rules()]
    })

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")

    if not message:
        return jsonify({"error": "Message vide"}), 400

    try:
        # Étape 1 : Créer un thread avec ton message utilisateur
        thread = openai.beta.threads.create(
            messages=[{"role": "user", "content": message}]
        )
        thread_id = thread.id

        # Étape 2 : Lancer un run avec ton assistant sur ce thread
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        run_id = run.id

        # Étape 3 : Attendre que le run se termine (OpenAI traite en asynchrone)
        while True:
            run_status = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run_status.status == "completed":
                break
            time.sleep(1)

        # Étape 4 : Récupérer les messages générés par l'assistant
        messages = openai.beta.threads.messages.list(thread_id=thread_id)

        # Extraction de la réponse de l'assistant
        assistant_response = next(
            (msg.content[0].text.value for msg in messages if msg.role == "assistant"),
            "L'assistant n'a pas fourni de réponse."
        )

        # Nettoyage des caractères d'échappement
        assistant_response = assistant_response.replace("\\n", "\n").replace('\\"', '"')

        return jsonify({"response": assistant_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Configuration pour Render
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))
