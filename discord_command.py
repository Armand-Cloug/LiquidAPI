import discord
from discord.ext import commands
import mysql.connector
import os
import sys
from dotenv import load_dotenv
import json

# Importe les scrapers
from scraper.scraper_cs import fetch_and_store_matches as cs_scraper
from scraper.scraper_rl import fetch_and_store_matches as rl_scraper
from scraper.scraper_valo import fetch_and_store_matches as valo_scraper
#from scraper.scraper_lol import fetch_and_store_matches as lol_scraper

# Pour passer le bot_client dans les scrapers
from main import bot_client

role_admin="La Team"

# Charger la config
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

# Charger les variables d'environnement
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

class DBCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="tables",
        description="📊 Affiche les tables de la base de données"
    )
    @commands.has_role(role_admin)  # 👈 Autoriser uniquement les membres avec ce rôle
    async def list_tables(self, ctx):
        """Commande hybride pour lister les tables de la base MySQL."""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            if not tables:
                await ctx.send("❌ Aucune table trouvée dans la base de données.")
                return

            table_names = "\n".join([f"• `{table[0]}`" for table in tables])
            embed = discord.Embed(
                title="📋 Tables dans la base de données",
                description=table_names,
                color=discord.Color.teal()
            )
            await ctx.send(embed=embed)

        except mysql.connector.Error as err:
            await ctx.send(f"❌ Erreur DB : {err}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()    

class RebootCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="reboot",
        description="🔁 Redémarre le bot via PM2."
    )
    @commands.is_owner()
    async def reboot(self, ctx: commands.Context):
        await ctx.reply("♻️ Redémarrage du bot via **PM2** en cours...", ephemeral=True)

        print(f"[🔁] Reboot demandé par {ctx.author} via /reboot")

        # ✅ Restart via PM2
        os.system("pm2 restart bot-liquidapi")  # ← "discord-bot" est le nom que tu donnes avec pm2 start

        # 🛑 Fermer proprement l'instance actuelle du bot
        await self.bot.close()

class ScrapeCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="scrape",
        description="🕵️ Forcer un scraping immédiat pour toutes les scènes suivies"
    )
    @commands.has_role(role_admin)  # 👈 Autoriser uniquement les membres avec ce rôle
    async def scrape_now(self, ctx):
        await ctx.reply("🔄 Scraping manuel en cours...", ephemeral=True)

        config = load_config()
        total = 0

        for source in config.get("sources", []):
            url = source["url"]
            equipe = source["equipe"]
            jeu = source["jeu"]
            channel_id = source["channel_id"]
            bot_ref=self.bot

            try:
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

                total += 1
            except Exception as e:
                await ctx.send(f"❌ Erreur sur {equipe} ({jeu}) : {e}", ephemeral=True)

        await ctx.send(f"✅ Scraping manuel terminé pour {total} scène(s) !", ephemeral=True)
    
    # 🔐 Gestion des erreurs d'autorisation
    @scrape_now.error
    async def scrape_now_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.send("🚫 Tu n'as pas le rôle requis pour utiliser cette commande.", ephemeral=True)
        else:
            raise error

# Fonction pour enregistrer le cog
async def setup(bot):
    await bot.add_cog(DBCommands(bot))
    await bot.add_cog(RebootCommand(bot))
    await bot.add_cog(ScrapeCommand(bot))