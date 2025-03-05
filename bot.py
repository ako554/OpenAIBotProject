from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import time
import concurrent.futures  # Pour exécuter les requêtes OpenAI en parallèle

# Configuration
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key
assistant_id = "asst_oFDIqZw8UyPvvmPZfCzZMWc1"

app = Flask(__name__)
CORS(app)  # Autorise toutes les origines (modifier pour plus de sécurité en production)

# Utilisation d'un ThreadPool pour exécuter OpenAI sans bloquer Flask
executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

def get_openai_response(message, max_wait_time=15):
    """
    Exécute la requête OpenAI en parallèle sans bloquer Flask.
    """
    start_time = time.time()

    try:
        # Étape 1 : Créer un thread OpenAI
        thread = openai.beta.threads.create(
            messages=[{"role": "user", "content": message}]
        )
        thread_id = thread.id

        # Étape 2 : Lancer un run
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        run_id = run.id

        # Étape 3 : Attente non bloquante avec timeout progressif
        sleep_time = 0.3  # Commence par 0.3s pour accélérer l’attente
        elapsed_time = 0

        while elapsed_time < max_wait_time:
            run_status = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)

            if run_status.status == "completed":
                break  # Sortie immédiate dès que c'est prêt

            time.sleep(sleep_time)
            elapsed_time = time.time() - start_time

            # Augmente progressivement le délai d’attente (max 2s)
            sleep_time = min(sleep_time * 1.5, 2)

        if elapsed_time >= max_wait_time:
            return "⏳ Temps d’attente dépassé, réessayez plus tard."

        # Étape 4 : Récupérer les messages OpenAI
        messages = openai.beta.threads.messages.list(thread_id=thread_id)

        # Extraction de la réponse
        assistant_response = next(
            (msg.content[0].text.value for msg in messages if msg.role == "assistant"),
            "⚠️ L'assistant n'a pas fourni de réponse."
        )

        return assistant_response.replace("\\n", "\n").replace('\\"', '"')

    except openai.OpenAIError as e:
        return f"❌ Erreur OpenAI : {str(e)}"
    except Exception as e:
        return f"❌ Erreur inconnue : {str(e)}"


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "API Flask fonctionne",
        "routes": [rule.rule for rule in app.url_map.iter_rules()]
    })


@app.route("/chat", methods=["POST"])
def chat():
    """Gère les requêtes POST pour interagir avec l'assistant OpenAI en parallèle."""
    data = request.get_json()
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "⚠️ Message vide"}), 400

    # Lancement de la requête OpenAI en parallèle (Flask ne sera pas bloqué)
    future = executor.submit(get_openai_response, message)
    response = future.result()  # Attente non bloquante

    return jsonify({"response": response})


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=PORT, threaded=True)  # Mode multithread activé
