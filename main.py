import os
import random
import string
import time
import requests
import re
from flask import Flask, jsonify

app = Flask(__name__)

# Récupère ta clé ZenRows depuis les variables d'environnement de Render
ZENROWS_API_KEY = os.getenv("ZENROWS_API_KEY")

def gen_random(length=10):
    """Génère une chaîne aléatoire pour les noms/passwords"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def zenrows_request(url, instructions=None):
    """Effectue une requête via ZenRows avec rendu JS et instructions"""
    params = {
        'apikey': ZENROWS_API_KEY,
        'url': url,
        'js_render': 'true',
        'antibot': 'true',
        'premium_proxy': 'true',
    }
    if instructions:
        # Convertit la liste Python en chaîne JSON pour l'API
        params['js_instructions'] = str(instructions).replace("'", '"')
    
    return requests.get('https://api.zenrows.com/v1/', params=params)

@app.route('/run')
def run_automation():
    try:
        # --- DONNÉES GÉNÉRÉES ---
        user_rand = gen_random(8)
        pass_rand = gen_random(14)
        email_gen = f"{user_rand}@outlook.fr" # Format demandé
        prenom = "Alex"
        nom = "Robot"

        # --- ÉTAPE 1 : INSCRIPTION SUR LE PREMIER SITE ---
        url_site_1 = "https://signup.live.com/signup?cobrandid=ab0455a0-8d03-46b9-b18b-df2f57b9e44c&contextid=C9DA2F7DDBB5EE06&opid=3B395EE7C8B7708E&bk=1773527762&sru=https://login.live.com/oauth20_authorize.srf%3fclient_id%3d9199bf20-a13f-4107-85dc-02114787ef48%26cobrandid%3dab0455a0-8d03-46b9-b18b-df2f57b9e44c%26client_id%3d9199bf20-a13f-4107-85dc-02114787ef48%26cobrandid%3dab0455a0-8d03-46b9-b18b-df2f57b9e44c%26contextid%3dC9DA2F7DDBB5EE06%26opid%3d3B395EE7C8B7708E%26login_hint%3dM%2524EjB4nOOYPLX7zfPX338WCYnmGBdVVlgaGhkZOOSXluTk52frpRVJTLq86T0rAHCpEXk%26mkt%3dFR-FR%26lc%3d1036%26bk%3d1773527762%26uaid%3d1c652bf9561d1651b96e038267fa0c8d&lw=dob,flname,wld&uiflavor=web&fluent=2&client_id=00000000487A244A&lic=1&mkt=FR-FR&lc=1036&uaid=1c652bf9561d1651b96e038267fa0c8d"
        
        # Note: Remplace les sélecteurs (ex: '#username') par les vrais IDs du site
        instr_1 = [
            {"fill": ["#username_field", user_rand]},
            {"click": "#btn_next"},
            {"wait": 1000},
            {"fill": ["#password_field", pass_rand]},
            {"click": "#btn_next"},
            {"wait": 1000},
            {"evaluate": "document.querySelectorAll('select')[0].value = '1990'"}, # Date naissance
            {"fill": ["input[name='firstname']", prenom]},
            {"fill": ["input[name='lastname']", nom]},
            {"click": ".human-verification-button"}, # Bouton "Humain"
            {"wait": 2000},
            {"evaluate": "if(document.querySelector('.popup-close')){document.querySelector('.popup-close').click()}"} # Annule fenêtres
        ]
        
        print("Lancement Phase 1...")
        zenrows_request(url_site_1, instr_1)

        # --- ÉTAPE 2 : SCRAPINGBEE (CONNEXION/INSCRIPTION) ---
        url_scrapingbee = "https://dashboard.scrapingbee.com/account/register"
        
        instr_bee = [
            {"fill": ["input[type='email']", "l3ryx91220@outlook.fr"]},
            {"fill": ["input[type='password']", pass_rand]},
            {"click": "#solve-captcha-button"}, # Le bouton pour le captcha
            {"wait": 5000}
        ]
        
        print("Lancement Phase 2...")
        zenrows_request(url_scrapingbee, instr_bee)

        # --- ÉTAPE 3 : NAVIGATION DANS LA BOITE MAIL ET CLIC LIEN ---
        # Ici, on utilise ZenRows pour aller sur l'interface web du mail
        url_mail_login = "URL_

