import discord
from discord import ui
from discord.ext import commands

#Fichier Perso
from make.make_db import create_table
from make.make_config import save_to_config

# Dropdown pour le choix du jeu
class JeuDropdown(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Counter-Strike", value="cs", emoji="🔫"),
            discord.SelectOption(label="Valorant", value="valo", emoji="🔫"),
            discord.SelectOption(label="League of Legends", value="lol", emoji="🧙"),
            discord.SelectOption(label="Rocket League", value="rl", emoji="🚗")
        ]
        super().__init__(placeholder="Choisis un jeu", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        modal = RecrutementModal(game=self.values[0])
        await interaction.response.send_modal(modal)


class RecrutementModal(ui.Modal, title="📋 Suivi de Scène E-Sport"):
    def __init__(self, game):
        super().__init__()
        self.game = game

    team = ui.TextInput(label="Équipe à suivre", placeholder="Ex : vitality / kc / gentlemates", max_length=20)
    chan = ui.TextInput(label="Nom du channel cible", placeholder="Ex : vitality-cs / kc-lol", max_length=30)
    url = ui.TextInput(label="Lien Liquipedia", placeholder="Ex : https://liquipedia.net/counterstrike/Team_Vitality/Matches", max_length=200)

    async def on_submit(self, interaction: discord.Interaction):
        team = self.team.value.strip().lower()
        channel_name = self.chan.value.strip().lower().replace(" ", "-")
        url = self.url.value.strip()

        await interaction.user.send("📨 Cette scène va maintenant être suivie dans le channel associé !")

        # ✅ 1. Créer la table dans la DB
        create_table(team, self.game)

        # ✅ 2. Créer le channel
        guild = interaction.guild
        existing = discord.utils.get(guild.text_channels, name=channel_name)

        if existing:
            created_channel_id = existing.id
            await interaction.followup.send(
                f"⚠️ Le channel <#{created_channel_id}> existe déjà !", ephemeral=True)
        else:
            category = interaction.channel.category  # rester dans la même catégorie
            new_channel = await guild.create_text_channel(name=channel_name, category=category)
            created_channel_id = new_channel.id

            await new_channel.send(
                f"📢 Suivi de **{team}** sur **{self.game.upper()}** activé par {interaction.user.mention} !")

        # ✅ 3. Ajout de la data dans config.json
        save_to_config(
            team=self.team.value.lower(),
            url=self.url.value,
            jeu=self.game.lower(),
            channel_id=new_channel.id
        )

        # ✅ 4. Debug
        print("▶️ Nouvelle scène suivie :")
        print("   • Team :", team)
        print("   • Jeu  :", self.game)
        print("   • URL  :", url)
        print("   • Channel ID :", created_channel_id)

class RecrutementView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(JeuDropdown())


async def envoyer_embed_recrutement(bot: commands.Bot, channel_id: int):
    channel = bot.get_channel(channel_id)
    if channel is None:
        print(f"[❌] Channel ID {channel_id} introuvable.")
        return

    embed = discord.Embed(
        title="🎮 Suivre une scène E-Sport",
        description="Clique sur le menu déroulant ci-dessous pour choisir un jeu et créer un suivi d'équipe personnalisé.",
        color=discord.Color.dark_purple()
    )
    embed.set_footer(text="©️ Made by Cloug ©️")

    await channel.send(embed=embed, view=RecrutementView())

# Fonction pour envoyer une notification
async def send_notif(team1, team2, score, date, tournoi, chan_id, bot: commands.Bot):
    channel = bot.get_channel(int(chan_id))
    if not channel:
        print(f"[❌] Channel ID {chan_id} introuvable pour notification.")
        return

    embed = discord.Embed(
        title="🎯 Nouveau Résultat E-Sport",
        color=discord.Color.dark_purple()
    )
    embed.add_field(name="📅 Date", value=date, inline=True)
    embed.add_field(name="🧱 Tournoi", value=tournoi, inline=True)
    embed.add_field(name="⚔️ Match", value=f"{team1} vs {team2}", inline=False)
    embed.add_field(name="📊 Score", value=score, inline=False)
    embed.set_footer(text="©️ Made by Cloug ©️")

    await channel.send(embed=embed)
