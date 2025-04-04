import mysql.connector
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def create_table(team, game):
    table_name = f"{team.lower()}_{game.lower()}".replace(" ", "_")

    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{table_name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        match_date VARCHAR(100) UNIQUE,
        match_tier VARCHAR(100),
        match_tournoi VARCHAR(100),
        match_team1 VARCHAR(100),
        match_team2 VARCHAR(100),
        score VARCHAR(100)
    );
    """

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Table `{table_name}` créée ou déjà existante.")
    except mysql.connector.Error as err:
        print(f"❌ Erreur lors de la création de la table : {err}")

