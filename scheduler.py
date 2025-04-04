import asyncio
import json
import os
from discord.ext import tasks
from dotenv import load_dotenv

from scraper.scraper_cs import fetch_and_store_matches as cs_scraper
from scraper.scraper_rl import fetch_and_store_matches as rl_scraper
from scraper.scraper_valo import fetch_and_store_matches as valo_scraper
#from scraper.scraper_lol import fetch_and_store_matches as lol_scraper


load_dotenv()

CHAN_ID = int(os.getenv("CHAN_ID"))  # Channel de debug/info

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

bot_ref = None  # Pour stocker le bot à utiliser dans les messages

@tasks.loop(minutes=15)
async def lancer_scraping_periodique():
    print("🔁 [TASK] Début du scraping périodique")
    config = load_config()

    for source in config.get("sources", []):
        url = source["url"]
        equipe = source["equipe"]
        jeu = source["jeu"]
        channel_id = source["channel_id"]

        if jeu == "cs":
            await cs_scraper(url, equipe, channel_id, bot_ref)
        elif jeu == "rl":
            await rl_scraper(url, equipe, channel_id, bot_ref)
        elif jeu == "valo":
            await valo_scraper(url, equipe, channel_id, bot_ref)
        #elif jeu == "lol":
        #    await lol_scraper(url, equipe, channel_id)
        else:
            print(f"[⚠️] Jeu inconnu : {jeu}")

    print("✅ [TASK] Scraping terminé.")

    # ➕ Envoi de message dans le channel debug
    if bot_ref:
        channel = bot_ref.get_channel(CHAN_ID)
        if channel:
            await channel.send(" Le scraping automatique vient de s'exécuter. ✅")

def start_scheduler(bot):
    global bot_ref
    bot_ref = bot
    lancer_scraping_periodique.start()

