# bot_twitch_2fa.py
import os
import json
import logging
from cryptography.fernet import Fernet
import pyotp
import discord
from discord import app_commands
from dotenv import load_dotenv

# --- Configuration ---
# Charge les variables depuis le fichier .env
load_dotenv()

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
FERNET_KEY = os.environ.get("FERNET_KEY")
GUILD_ID = os.environ.get("GUILD_ID") # L'ID de votre serveur Discord
ALLOWED_ROLE_NAME = os.environ.get("ALLOWED_ROLE_NAME", "Streamer")
SECRETS_FILE = "secrets.json"

# --- Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("twitch2fa_bot")

# --- Vérifications au démarrage ---
if not all([DISCORD_TOKEN, FERNET_KEY, GUILD_ID]):
    logger.error("Les variables d'environnement DISCORD_TOKEN, FERNET_KEY, et GUILD_ID sont requises.")
    exit()

try:
    fernet = Fernet(FERNET_KEY.encode())
    guild_object = discord.Object(id=int(GUILD_ID))
except (ValueError, TypeError) as e:
    logger.error(f"Erreur de configuration (GUILD_ID ou FERNET_KEY invalide): {e}")
    exit()

# --- Fonctions pour la clé secrète ---
def load_secret(name: str) -> str | None:
    """Charge et déchiffre la clé secrète depuis le fichier."""
    if not os.path.exists(SECRETS_FILE):
        logger.warning(f"Le fichier de secrets '{SECRETS_FILE}' n'existe pas. As-tu exécuté init_secret.py ?")
        return None
    with open(SECRETS_FILE, "r") as f:
        data = json.load(f)
    
    encrypted_secret = data.get(name)
    if not encrypted_secret:
        logger.warning(f"Aucun secret trouvé pour '{name}' dans '{SECRETS_FILE}'.")
        return None
        
    try:
        return fernet.decrypt(encrypted_secret.encode()).decode()
    except Exception as e:
        logger.exception("Échec du déchiffrement de la clé. La FERNET_KEY a-t-elle changé ?")
        return None

# --- Client Discord ---
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(
    name="twitchcode",
    description="Obtenir le code 2FA pour le compte Twitch de l'équipe.",
    guild=guild_object
)
async def get_twitch_code(interaction: discord.Interaction):
    """Génère et envoie le code 2FA Twitch."""
    # Vérifie si l'utilisateur a le rôle requis
    if not isinstance(interaction.user, discord.Member):
        await interaction.response.send_message("Cette commande doit être utilisée sur le serveur.", ephemeral=True)
        return

    has_role = any(role.name == ALLOWED_ROLE_NAME for role in interaction.user.roles)
    
    if not has_role:
        logger.warning(f"Accès refusé pour {interaction.user} (n'a pas le rôle '{ALLOWED_ROLE_NAME}').")
        await interaction.response.send_message(
            f"❌ Vous n'avez pas la permission. Seuls les membres avec le rôle `{ALLOWED_ROLE_NAME}` peuvent utiliser cette commande.",
            ephemeral=True
        )
        return

    # Charge la clé secrète et génère le code
    totp_secret = load_secret("twitch_team")
    if not totp_secret:
        await interaction.response.send_message("Erreur critique : La clé secrète n'est pas configurée. Contactez un admin.", ephemeral=True)
        return
        
    totp = pyotp.TOTP(totp_secret)
    code = totp.now()

    # Envoie le code en message éphémère (visible uniquement par l'utilisateur)
    await interaction.response.send_message(f"🔑 Votre code 2FA pour Twitch est : `{code}`\n*(Ce code est valide environ 30 secondes)*", ephemeral=True)
    logger.info(f"Code 2FA généré et envoyé à {interaction.user}.")

@client.event
async def on_ready():
    """Événement déclenché quand le bot est prêt."""
    await tree.sync(guild=guild_object)
    logger.info(f"Bot connecté en tant que {client.user}.")
    logger.info(f"Commande '/twitchcode' synchronisée pour le serveur {GUILD_ID}.")

# --- Lancement du bot ---
client.run(DISCORD_TOKEN)
