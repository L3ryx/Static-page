import os
import random
import string
import time
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Configuration (Utilise des variables d'environnement sur Render)
ZENROWS_API_KEY = os.getenv("ZENROWS_API_KEY")
SCRAPINGBEE_API_KEY = os.getenv("SCRAPINGBEE_API_KEY")

def get_random_str(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

@app.route('/')
def health_check():
    return "Bot en ligne. Utilisez /run pour lancer l'automatisation."

@app.route('/run')
def run_automation():
    target_url = "L_URL_QUE_TU_METTRAS"
    
    # 1. Préparation des instructions JS pour ZenRows
    # On simule les clics et le remplissage de formulaire directement dans le navigateur distant
    js_instructions = [
        {"fill": ["input[name='username']", get_random_str()]},
        {"click": "#next-button"},
        {"wait": 2000},
        {"fill": ["input[name='password']", get_random_str(12)]},
        {"click": "#submit-button"},
        {"wait": 2000},
        # Ajoute ici les sélecteurs spécifiques pour la date, nom, prénom
        {"click": ".human-verification-button"}, 
    ]

    params = {
        'apikey': ZENROWS_API_KEY,
        'url': target_url,
        'js_render': 'true',
        'antibot': 'true',
        'premium_proxy': 'true',
        'js_instructions': str(js_instructions).replace("'", '"')
    }

    try:
        # Exécution ZenRows
        response = requests.get('https://api.zenrows.com/v1/', params=params)
        
        # Logique simplifiée pour ScrapingBee après (E-mail)
        # Note : Pour l'e-mail, il faudrait une intégration IMAP pour lire le lien
        
        return jsonify({
            "status": "success",
            "message": "Script exécuté. Vérifiez vos logs pour la clé API finale.",
            "debug_code": response.status_code
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

