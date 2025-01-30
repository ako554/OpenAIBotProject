import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis key.env
load_dotenv("key.env")

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print(f"Clé API chargée avec succès : {api_key[:10]}********")
else:
    print("Erreur : la clé API OpenAI n'a pas été trouvée.")

