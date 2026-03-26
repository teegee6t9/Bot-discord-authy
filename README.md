# Bot-discord-authy
Service d'auhtentification dans discord via un bot qui va chercher le code de double authentification depuis Authy

Par Thibault Godard

# Twitch 2FA Bot

Bot Discord hébergé sur VPS qui génère et envoie les codes 2FA TOTP du compte Twitch de l'équipe, directement dans Discord via une commande slash.

---

## Fonctionnement

1. Un membre avec le rôle autorisé tape `/twitchcode` dans Discord
2. Le bot génère un code TOTP valide 30 secondes à partir du secret chiffré
3. Le code est envoyé en message éphémère (visible uniquement par l'utilisateur)

---

## Prérequis

- Python 3.12+
- Un VPS Linux avec `pm2` installé
- Un bot Discord créé sur le [Discord Developer Portal](https://discord.com/developers/applications)
- Le secret TOTP du compte Twitch (disponible lors de l'activation du 2FA)

---

## Installation

### 1. Cloner le dépôt et créer l'environnement virtuel

```bash
git clone <url-du-repo>
cd twitch-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurer les variables d'environnement

Créer un fichier `.env` à la racine du dossier `twitch-bot/` :

```env
DISCORD_TOKEN=ton_token_discord
FERNET_KEY=ta_cle_fernet
GUILD_ID=id_de_ton_serveur_discord
ALLOWED_ROLE_NAME=Streamer
```

Pour générer une `FERNET_KEY` :

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 3. Initialiser le secret TOTP

Ouvrir `init_secret.py` et remplacer `***` par le secret TOTP Twitch, puis exécuter :

```bash
python3 init_secret.py
```

Cela crée le fichier `secrets.json` avec le secret chiffré. Le secret en clair ne doit jamais être commité.

### 4. Lancer le bot via pm2

```bash
pm2 start .venv/bin/python --name "twitch-2fa-bot" -- bot_twitch_2fa.py
pm2 save
pm2 startup  # suivre les instructions affichées
```

---

## Utilisation

Dans le serveur Discord, les membres ayant le rôle configuré dans `ALLOWED_ROLE_NAME` peuvent utiliser :

```
/twitchcode
```

Le code 2FA est affiché en message privé éphémère, valable ~30 secondes.

---

## Structure des fichiers

```
twitch-bot/
├── bot_twitch_2fa.py   — bot Discord principal
├── init_secret.py      — initialisation et chiffrement du secret TOTP
├── requirements.txt    — dépendances Python
├── .env                — variables d'environnement (non versionné)
└── secrets.json        — secret TOTP chiffré (non versionné)
```

---

## Sécurité

- Le secret TOTP est chiffré au repos via `cryptography.Fernet`
- Les fichiers `.env` et `secrets.json` sont exclus du dépôt git via `.gitignore`
- L'accès à la commande est restreint par rôle Discord
- Les codes sont envoyés en messages éphémères, invisibles pour les autres membres

---
## Aperçu  
<img width="396" height="126" alt="image" src="https://github.com/user-attachments/assets/46cdf94e-ef95-4a14-90ed-d3a43000e7d4" />
