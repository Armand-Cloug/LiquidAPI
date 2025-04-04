-- 📌 Création de la base de données si elle n'existe pas
CREATE DATABASE IF NOT EXISTS liquid_api;
USE liquid_api;

-- 📌 Template Table CS / RL / LOL
CREATE TABLE IF NOT EXISTS vitality_rl (
    id INT AUTO_INCREMENT PRIMARY KEY,
    match_date VARCHAR(100) UNIQUE,
    match_tier VARCHAR(100),
    match_tournoi VARCHAR(100),
    match_team1 VARCHAR(100),
    match_team2 VARCHAR(100),
    score VARCHAR(100)
);