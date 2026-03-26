# init_secret.py
import os, json
from cryptography.fernet import Fernet
from dotenv import load_dotenv
load_dotenv()
FERNET_KEY = os.environ.get("FERNET_KEY")
if not FERNET_KEY:
    exit("Erreur: FERNET_KEY non définie dans .env")

# --- METS TA NOUVELLE CLÉ SECRÈTE TWITCH ICI ---
TWITCH_TOTP_SECRET = ""

if "TA_NOUVELLE_CLÉ_SECRÈTE_TWITCH" in TWITCH_TOTP_SECRET:
    exit("Attention: Remplace par ta vraie clé secrète TOTP.")
fernet = Fernet(FERNET_KEY.encode())
encrypted_secret = fernet.encrypt(TWITCH_TOTP_SECRET.encode()).decode()
data = {"twitch_team": encrypted_secret}
with open("secrets.json", "w") as f:
    json.dump(data, f)
print("✅ Fichier secrets.json créé avec la nouvelle clé chiffrée.")
