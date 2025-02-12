import os
from flask import Flask, request, jsonify

# Initialiser Flask
app = Flask(__name__)

# Route de test pour vérifier que Flask tourne
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API Flask fonctionne", "routes": [rule.rule for rule in app.url_map.iter_rules()]})

# Route /chat pour tester les requêtes POST
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")

    if not message:
        return jsonify({"error": "Message vide"}), 400

    return jsonify({"response": f"Tu as dit : {message}"})

# Lancer Flask avec un port dynamique
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
