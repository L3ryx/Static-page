import os
import random
import string
import time
import requests
import re
from flask import Flask, jsonify

app = Flask(__name__)
ZENROWS_API_KEY = os.getenv("ZENROWS_API_KEY")

def gen_user(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def zenrows_request(url, instructions=None):
    params = {
        'apikey': ZENROWS_API_KEY, 'url': url, 'js_render': 'true', 
        'antibot': 'true', 'premium_proxy': 'true'
    }
    if instructions:
        params['js_instructions'] = str(instructions).replace("'", '"')
    return requests.get('https://api.zenrows.com/v1/', params=params)

@app.route('/run')
def run():
    # Identifiants générés
    email_gen = f"user{gen_user()}@outlook.fr"
    password = f"Pass{random.randint(1000, 9999)}"
    first_name = f"Alex{random.randint(100000, 999999)}"
    last_name = f"Doe{random.randint(1000, 9999)}"

    # 1. INSCRIPTION OUTLOOK
    instr_outlook = [
        {"fill": ["input[name='MemberName']", email_gen]},
        {"click": "button[data-testid='primaryButton']"},
        {"wait": 2000},
        {"fill": ["input[type='password']", password]},
        {"click": "button[data-testid='primaryButton']"},
        {"wait": 2000},
        {"evaluate": 'document.querySelector("select[name=\'BirthDay\']").value = "15"'},
        {"evaluate": 'document.querySelector("select[name=\'BirthMonth\']").value = "5"'},
        {"evaluate": 'document.querySelector("select[name=\'BirthYear\']").value = "1990"'},
        {"click": "button[data-testid='primaryButton']"},
        {"wait": 2000},
        {"fill": ["input[name='firstNameInput']", first_name]},
        {"fill": ["input[name='lastNameInput']", last_name]},
        {"click": "button[data-testid='primaryButton']"}
    ]
    zenrows_request("https://signup.live.com/signup...", instr_outlook)

    # 2. INSCRIPTION SCRAPINGBEE
    instr_bee = [
        {"fill": ["input[name='email']", email_gen]},
        {"fill": ["input[name='password']", password]},
        {"click": "#accept_terms"},
        {"click": "button[type='submit']"} # Clic captcha
    ]
    zenrows_request("https://dashboard.scrapingbee.com/account/register", instr_bee)

    # 3. RÉCUPÉRATION CLÉ (Logique simplifiée pour l'exemple)
    # Ici, le script accède à l'URL Microsoft fournie, se connecte, et cherche le lien.
    # ... (Logique de navigation via ZenRows pour cliquer sur le mail)

    return jsonify({"status": "Terminé", "email": email_gen, "password": password})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

