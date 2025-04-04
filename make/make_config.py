#!/bin/python3.11

import json
import os

CONFIG_PATH = "config.json"

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {"sources": []}
    
    with open(CONFIG_PATH, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            print("[⚠️] Erreur de parsing JSON, fichier corrompu ?")
            return {"sources": []}

def save_to_config(team: str, url: str, jeu: str, channel_id: int):
    config = load_config()

    # Vérifie si l'entrée existe déjà (même équipe + jeu)
    for entry in config["sources"]:
        if entry["equipe"] == team.lower() and entry["jeu"] == jeu.lower():
            print(f"[ℹ️] L'entrée pour {team.upper()} ({jeu.upper()}) existe déjà dans le fichier de config.")
            return False

    new_entry = {
        "url": url,
        "equipe": team.lower(),
        "jeu": jeu.lower(),
        "channel_id": channel_id
    }

    config["sources"].append(new_entry)

    with open(CONFIG_PATH, "w") as file:
        json.dump(config, file, indent=2)
    
    print(f"[✅] Nouvelle entrée ajoutée au config.json : {team} ({jeu}) → {channel_id}")
    return True
