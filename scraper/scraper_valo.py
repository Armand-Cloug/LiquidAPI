#!/bin/python3.11

import os
import requests
import mysql.connector
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Fichier perso
from discord_embed import send_notif

# Charger les variables d'environnement
load_dotenv()

# Connexion à la base de données
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

USER_AGENT = 'LiquipediaBot/1.0'
HEADERS = {"User-Agent": USER_AGENT}


async def fetch_and_store_matches(url, team_followed, chan_id, bot):
    """
    Scrape les matchs Liquipedia et insère les nouveaux dans la base de données.
    Envoie une notif Discord si un nouveau match est détecté.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
    except mysql.connector.Error as err:
        print(f"[❌] Erreur de connexion à la base : {err}")
        return []

    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    match_rows = soup.select('table.wikitable tbody tr')

    new_matches = []

    print(f"[🔍] {len(match_rows)} ligne(s) détectées.")

    for idx, row in enumerate(match_rows):
        cells = row.find_all(['td', 'th'])
        if len(cells) < 8:
            continue

        date = cells[0].get_text(strip=True)
        tier = cells[1].get_text(strip=True)
        tournoi = cells[4].get_text(strip=True)
        team1 = team_followed
        team2 = cells[6].get_text(strip=True)
        score = cells[5].get_text(strip=True)

        table_name = team_followed + "_valo"

        # Vérifier si le match existe déjà
        query = f"SELECT 1 FROM {table_name} WHERE match_date = %s"
        cursor.execute(query, (date,))
        if cursor.fetchone():
            continue

        # Insertion du match
        insert_query = f"""
            INSERT INTO {table_name} (match_date, match_tier, match_tournoi, match_team1, match_team2, score)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (date, tier, tournoi, team1, team2, score))
        conn.commit()

        print(f"[{idx+1:03d}] ✅ Nouveau match ajouté : {team1} {score} {team2}")
        new_matches.append({
            "date": date,
            "tier": tier,
            "tournoi": tournoi,
            "team1": team1,
            "team2": team2,
            "score": score
        })

        # 🔔 Envoi de notification Discord
        await send_notif(team1, team2, score, date, tournoi, chan_id, bot)

    cursor.close()
    conn.close()
    return new_matches