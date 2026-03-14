import os
import random
import string
import time
import requests
import re
from flask import Flask, jsonify

app = Flask(__name__)

# Ta clé API ZenRows à configurer dans l'interface de Render
ZENROWS_API_KEY = os.getenv("ZENROWS_API_KEY")

def gen_random(length=10):
    """Génère une chaîne aléatoire (lettres + chiffres)"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def zenrows_request(url, instructions=None):
    """Envoie la commande à ZenRows avec rendu JS et bypass antibot"""
    params = {
        'apikey': ZENROWS_API_KEY,
        'url': url,
        'js_render': 'true',
        'antibot': 'true',
        'premium_proxy': 'true',
    }
    if instructions:
        params['js_instructions'] = str(instructions).replace("'", '"')
    
    return requests.get('https://api.zenrows.com/v1/', params=params)

@app.route('/run')
def run_automation():
    try:
        # --- GÉNÉRATION DES IDENTIFIANTS UNIQUES ---
        user_name = gen_random(8)
        # On construit l'email avec le nom aléatoire
        email_genere = f"{user_name}@outlook.fr" 
        password_genere = gen_random(15) + "A1!" # Ajout de caractères pour les critères de sécurité
        prenom = "Alex"
        nom = "Robot"

        # --- ÉTAPE 1 : CRÉATION DU COMPTE OUTLOOK ---
        url_inscription_outlook = "https://signup.live.com/signup?sru=https%3a%2f%2flogin.live.com%2foauth20_authorize.srf%3flc%3d1036%26client_id%3d9199bf20-a13f-4107-85dc-02114787ef48%26cobrandid%3dab0455a0-8d03-46b9-b18b-df2f57b9e44c%26mkt%3dFR-FR%26opid%3d890FBE2FD9D9C9B0%26opidt%3d1773528109%26uaid%3d3cb1b4ca7be27bdc607547250389f955%26contextid%3dE9A3558BA1E9152C%26opignore%3d1&mkt=FR-FR&uiflavor=web&fl=dob%2cflname%2cwld&cobrandid=ab0455a0-8d03-46b9-b18b-df2f57b9e44c&client_id=9199bf20-a13f-4107-85dc-02114787ef48&uaid=3cb1b4ca7be27bdc607547250389f955&suc=9199bf20-a13f-4107-85dc-02114787ef48&fluent=2&lic=1" # ex: https://signup.live.com/signup
        
        instr_outlook = [
            {"fill": ["input[name='MemberName']", email_genere]}, # Sélecteur à vérifier selon la page
            {"click": "input[type='submit']"},
            {"wait": 1000},
            {"fill": ["input[name='Password']", password_genere]},
            {"click": "input[type='submit']"},
            {"wait": 1000},
            {"fill": ["input[name='FirstName']", prenom]},
            {"fill": ["input[name='LastName']", nom]},
            {"click": "input[type='submit']"},
            # Sélection aléatoire de la date de naissance (JS)
            {"evaluate": "document.querySelector('select[name='BirthDay']').value = '15'"},
            {"evaluate": "document.querySelector('select[name='BirthMonth']').value = '5'"},
            {"evaluate": "document.querySelector('select[name='BirthYear']').value = '1992'"},
            {"click": "input[type='submit']"},
            {"wait": 5000}, # Attente pour la création effective
            {"click": "#btn-skip-verification"}, # Exemple pour passer la vérification
            {"evaluate": "if(document.querySelector('.cancel')){document.querySelector('.cancel').click()}"}
        ]
        
        print(f"Création du compte Outlook : {email_genere}")
        zenrows_request(url_inscription_outlook, instr_outlook)

        # --- ÉTAPE 2 : INSCRIPTION SUR SCRAPINGBEE ---
        # On utilise l'email et le mot de passe créés juste au-dessus
        url_scrapingbee = "https://dashboard.scrapingbee.com/account/register"
        
        instr_bee = [
            {"fill": ["input[name='email']", email_genere]}, 
            {"fill": ["input[name='password']", password_genere]},
            {"click": "#captcha-solve-button"}, # Bouton pour déclencher la résolution
            {"wait": 10000} # On laisse le temps au captcha de se résoudre
        ]
        
        print(f"Inscription ScrapingBee avec {email_genere}...")
        zenrows_request(url_scrapingbee, instr_bee)

        # --- ÉTAPE 3 : RÉCUPÉRATION DU MAIL DE CONFIRMATION ---
        # On retourne sur Outlook pour cliquer sur le lien
        url_outlook_inbox = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=9199bf20-a13f-4107-85dc-02114787ef48&scope=https%3A%2F%2Foutlook.office.com%2F.default%20openid%20profile%20offline_access&redirect_uri=https%3A%2F%2Foutlook.live.com%2Fmail%2F&client-request-id=1042ffd3-f572-ef1c-47bb-d1803a75377f&response_mode=fragment&client_info=1&prompt=select_account&nonce=019cee82-044e-74eb-94df-0136b85b19bc&state=eyJpZCI6IjAxOWNlZTgyLTA0NGQtNzEwMy04ZTg2LTRlYTFkNDkxN2YxNCIsIm1ldGEiOnsiaW50ZXJhY3Rpb25UeXBlIjoicmVkaXJlY3QifX0%3D%7CaHR0cHM6Ly9vdXRsb29rLmxpdmUuY29tL21haWwvMC8_Y3VsdHVyZT1mci1mciZjb3VudHJ5PWZy&claims=%7B%22access_token%22%3A%7B%22xms_cc%22%3A%7B%22values%22%3A%5B%22CP1%22%5D%7D%7D%7D&x-client-SKU=msal.js.browser&x-client-VER=4.22.0&response_type=code&code_challenge=5CMrGLEB0FYP1MK3K3j4s8I9VoM6-gH65mrKGRVQY_M&code_challenge_method=S256&cobrandid=ab0455a0-8d03-46b9-b18b-df2f57b9e44c&fl=dob,flname,wld"
        
        instr_lecture_mail = [
            {"click": "span:contains('ScrapingBee')"}, # Cherche le texte dans la boîte de réception
            {"wait": 2000}
        ]
        
        print("Lecture du mail de confirmation...")
        page_mail = zenrows_request(url_outlook_inbox, instr_lecture_mail)
        
        # Extraction du lien de confirmation par Regex
        links = re.findall(r'https://[\w\d./?=#-]+confirm[\w\d./?=#-]+', page_mail.text)
        if not links:
            return jsonify({"error": "Lien ScrapingBee introuvable dans la boîte mail."})
        
        confirm_link = links[0]

        # --- ÉTAPE 4 : RÉCUPÉRATION DE LA CLÉ API ---
        print("Récupération de la clé API finale...")
        final_page = zenrows_request(confirm_link, [{"wait": 4000}])
        
        # Recherche de la clé API dans le code HTML de la page finale
        api_key_match = re.search(r'spb-[a-zA-Z0-9]+', final_page.text)
        result_key = api_key_match.group(0) if api_key_match else "Clé introuvable"

        return jsonify({
            "succes": True,
            "compte_cree": email_genere,
            "mot_de_passe": password_genere,
            "cle_api_scrapingbee": result_key
        })

    except Exception as e:
        return jsonify({"erreur": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
