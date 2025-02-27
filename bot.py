from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import time

# Configuration
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key
assistant_id = "asst_KjtbsY41MGXV5nMzlHGJc6tc"

app = Flask(__name__)
CORS(app)  # Autorise toutes les origines (modifier pour plus de sécurité en production)


def get_openai_response(message):
    start_time = time.time()
    print(f"Début de la requête à {time.strftime('%H:%M:%S', time.localtime(start_time))}")

    # Créer le thread
    thread_start = time.time()
    try:
        thread = openai.beta.threads.create(
            messages=[{"role": "user", "content": message}]
        )
    except Exception as e:
        print(f"Erreur lors de la création du thread : {str(e)}")
        raise
    print(f"Création thread : {time.time() - thread_start:.2f} secondes")

    thread_id = thread.id

    # Lancer le run
    run_start = time.time()
    try:
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
    except Exception as e:
        print(f"Erreur lors du lancement du run : {str(e)}")
        raise
    print(f"Lancement run : {time.time() - run_start:.2f} secondes")

    run_id = run.id

    # Attente optimisée du statut avec délai et timeout strict
    max_attempts = 6  # 6 tentatives (3 secondes max avec sleep(0.5))
    attempt = 0
    while attempt < max_attempts:
        check_start = time.time()
        try:
            run_status = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        except Exception as e:
            print(f"Erreur lors de la vérification du statut : {str(e)}")
            raise
        print(f"Vérification statut (tentative {attempt + 1}) : {time.time() - check_start:.2f} secondes")
        if run_status.status == "completed":
            break
        time.sleep(0.5)  # Délai maintenu à 0.5 seconde
        attempt += 1

    if attempt >= max_attempts:
        raise TimeoutError("Délai maximum atteint (3 secondes)")

    print(f"Temps total d'attente du statut : {time.time() - start_time:.2f} secondes")

    # Récupérer les messages (avec timeout explicite)
    messages_start = time.time()
    try:
        messages = openai.beta.threads.messages.list(thread_id=thread_id, timeout=5)  # Timeout de 5 secondes
    except Exception as e:
        print(f"Erreur lors de la récupération des messages : {str(e)}")
        raise
    print(f"Récupération messages : {time.time() - messages_start:.2f} secondes")

    # Extraction réponse
    assistant_response = next(
        (msg.content[0].text.value for msg in messages if msg.role == "assistant"),
        "L'assistant n'a pas fourni de réponse."
    )

    total_time = time.time() - start_time
    print(f"Temps total de la requête : {total_time:.2f} secondes")

    return assistant_response.replace("\\n", "\n").replace('\\"', '"')


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
        response = get_openai_response(message)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=PORT)