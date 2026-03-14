import os
import random
import string
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Ta clé API ZenRows
ZENROWS_KEY = os.getenv("ZENROWS_API_KEY")

def gen_random(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def zenrows_request(url, instructions=None):
    params = {
        'apikey': ZENROWS_KEY, 'url': url, 'js_render': 'true',
        'antibot': 'true', 'premium_proxy': 'true'
    }
    if instructions:
        params['js_instructions'] = str(instructions).replace("'", '"')
    return requests.post('https://api.zenrows.com/v1/', data=params)

@app.route('/run')
def run_automation():
    email = f"{gen_random()}@outlook.fr"
    password = f"Auto{gen_random(6)}!"
    
    # Instructions détaillées pour Outlook
    instr_outlook = [
        {"fill": ["input[name='MemberName']", email]},
        {"click": "button[data-testid='primaryButton']"},
        {"wait": 3000}, # Temps pour charger le mot de passe
        {"fill": ["input[name='Password']", password]},
        {"click": "button[data-testid='primaryButton']"},
        {"wait": 2000},
        {"fill": ["input[name='FirstName']", "Jean"]},
        {"fill": ["input[name='LastName']", "Dupont"]},
        {"click": "button[data-testid='primaryButton']"},
        {"wait": 2000},
        # Sélection date naissance
        {"evaluate": 'document.querySelector("select[name=\'BirthDay\']").value = "15"'},
        {"evaluate": 'document.querySelector("select[name=\'BirthMonth\']").value = "5"'},
        {"evaluate": 'document.querySelector("select[name=\'BirthYear\']").value = "1990"'},
        {"click": "button[data-testid='primaryButton']"},
        {"wait": 10000} # Attente longue pour résolution Captcha manuel si nécessaire
    ]
    
    zenrows_request("https://signup.live.com/signup?lic=1", instr_outlook)
    
    return jsonify({"email_cree": email, "password": password, "message": "Si le script a réussi, le compte est créé."})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
