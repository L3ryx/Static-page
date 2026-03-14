import os
import random
import string
import time
import requests
import imaplib
import email
import re
from flask import Flask, jsonify

app = Flask(__name__)

# Configuration via Variables d'Environnement sur Render
ZENROWS_API_KEY = os.getenv("ZENROWS_API_KEY")
EMAIL_USER = "l3ryx91220@outlook.fr"
EMAIL_PASS = os.getenv("EMAIL_PASSWORD") # Utilise un "Mot de passe d'application" Microsoft

def get_random_name():
    first_names = ["Jean", "Marc", "Lucas", "Sophie", "Emma"]
    last_names = ["Dupont", "Moreau", "Lefebvre", "Rousseau"]
    return random.choice(first_names), random.choice(last_names)

def generate_str(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def zenrows_request(url, instructions):
    params = {
        'apikey': ZENROWS_API_KEY,
        'url': url,
        'js_render': 'true',
        'antibot': 'true',
        'premium_proxy': 'true',
        'js_instructions': str(instructions).replace("'", '"')
    }
    return requests.get('https://api.zenrows.com/v1/', params=params)

@app.route('/run')
def run_script():
    # --- PHASE 1 : Premier Site ---
    url_1 = "TON_PREMIER_URL"
    fn, ln = get_random_name()
    
    instructions_1 = [
        {"fill": ["input[type='text']", generate_str(8)]}, # Username
        {"click": "button.next"},
        {"wait": 1000},
        {"fill": ["input[type='password']", generate_str(15)]}, # Password
        {"click": "button.next"},
        {"wait": 1000},
        {"evaluate": "document.querySelectorAll('select')[0].value = '10'"}, # Jour naissance
        {"fill": ["input[name='firstname']", fn]},
        {"fill": ["input[name='lastname']", ln]},
        {"click": "#human-verification-btn"}, # Bypass manuel via clic
        {"click": "button.cancel"} # Fermer fenêtres si présentes
    ]
    
    res1 = zenrows_request(url_1, instructions_1)

    # --- PHASE 2 : ScrapingBee via ZenRows ---
    url_bee = "URL_SCRAPINGBEE"
    instructions_bee = [
        {"fill": ["input[type='email']", EMAIL_USER]},
        {"fill": ["input[type='password']", generate_str(12)]},
        {"click": ".captcha-solver-button"}, # Simulation du clic captcha
        {"wait": 5000}
    ]
    
    res2 = zenrows_request(url_bee, instructions_bee)

    # --- PHASE 3 : Récupération du mail (Outlook) ---
    # Attente que le mail arrive
    time.sleep(30) 
    api_key_found = "Non trouvée"
    
    try:
        mail = imaplib.IMAP4_SSL("outlook.office365.com")
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")
        _, data = mail.search(None, '(FROM "ScrapingBee")')
        mail_id = data[0].split()[-1]
        _, obj = mail.fetch(mail_id, '(RFC822)')
        
        # Extraction du lien avec Regex
        body = obj[0][1].decode('utf-8')
        links = re.findall(r'https://[\w\d./?=#-]+', body)
        confirm_link = links[0]

        # --- PHASE 4 : Clic sur le lien et lecture de la clé API ---
        # On demande à ZenRows d'aller sur le lien et de nous rendre le texte de la page
        res3 = zenrows_request(confirm_link, [{"wait": 2000}])
        # On cherche la clé API dans le HTML (exemple format : 'spb-XXXX')
        match = re.search(r'spb-[a-zA-Z0-9]+', res3.text)
        if match:
            api_key_found = match.group(0)

    except Exception as e:
        return f"Erreur Mail : {str(e)}"

    return jsonify({
        "status": "Terminé",
        "scraped_api_key": api_key_found
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
