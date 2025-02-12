import openai
import os
import time
from dotenv import load_dotenv

# Charger les variables d'environnement depuis key.env
load_dotenv("key.env")

# Récupérer la clé API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = "asst_KjtbsY41MGXV5nMzlHGJc6tc"  # Remplace par ton ID correct

# Vérifier si la clé API est bien chargée
if not OPENAI_API_KEY:
    raise ValueError("❌ ERREUR : La clé API OpenAI n'est pas définie dans key.env")

# Créer un client OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Réutiliser un thread existant pour accélérer les échanges
THREAD_ID = None

def interroger_assistant(message):
    """Envoie un message à l'Assistant API et retourne la réponse."""
    global THREAD_ID
    try:
        # Créer un thread unique si nécessaire
        if THREAD_ID is None:
            THREAD_ID = client.beta.threads.create().id

        # Ajouter le message utilisateur
        client.beta.threads.messages.create(
            thread_id=THREAD_ID,
            role="user",
            content=message
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

        # Récupérer et retourner la réponse
        messages = client.beta.threads.messages.list(thread_id=THREAD_ID)
        if messages.data:
            first_message = messages.data[0]
            if first_message.content and isinstance(first_message.content, list):
                return " ".join(block.text.value for block in first_message.content if hasattr(block, "text"))

        return "❌ Aucune réponse reçue."

    except openai.OpenAIError as e:
        return f"❌ Erreur OpenAI: {e}"

if __name__ == "__main__":
    print("🤖 Chatbot OpenAI Assistant (Tape 'exit' pour quitter)")

    while True:
        user_input = input("Toi: ")
        if user_input.lower() in ["exit", "quit", "stop"]:
            print("Bot: À bientôt ! 👋")
            break

        response = interroger_assistant(user_input)
        print(f"Bot: {response}")
