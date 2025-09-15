import os
import json
import requests
import pandas as pd
import mysql.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("API_KEY")
API_HOST = os.getenv("API_HOST")
SEASON = 2024
LEAGUE_ID = 39

if not API_KEY or not API_HOST:
    raise ValueError("API_KEY or API_HOST not found in environment variables.")

# API endpoint and request setup
url = "https://api-football-v1.p.rapidapi.com/v3/standings"
headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST,
}
querystring = {
    "league": LEAGUE_ID,
    "season": SEASON,
}

try:
    response = requests.get(url, headers=headers, params=querystring)
    response.raise_for_status()
    data = response.json()
    print("API request successful.")

    # Example: Convert standings data to DataFrame if available
    if "response" in data and data["response"]:
        standings = data["response"][0]["league"]["standings"][0]
        df = pd.DataFrame(standings)
        print(df.head())

        try:
            connection = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", ""),
                database=os.getenv("DB_NAME", "football_db")
            )

            cursor = connection.cursor()

            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS standings (
                    team_id INT,
                    team_name VARCHAR(100),
                    rank INT,
                    points INT,
                    goals_diff INT,
                    form VARCHAR(50),
                    played INT,
                    win INT,
                    draw INT,
                    lose INT,
                    PRIMARY KEY (team_id)
                )
            """)

            # Insert data
            for row in standings:
                team = row["team"]
                stats = row["all"]

                cursor.execute("""
                    REPLACE INTO standings (team_id, team_name, rank, points, goals_diff, form, played, win, draw, lose)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    team["id"],
                    team["name"],
                    row["rank"],
                    row["points"],
                    row["goalsDiff"],
                    row.get("form", ""),
                    stats["played"],
                    stats["win"],
                    stats["draw"],
                    stats["lose"]
                ))

            connection.commit()
            print("✅ Standings saved to MySQL successfully.")

        except mysql.connector.Error as err:
            print(f"MySQL Error: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("🔌 MySQL connection closed.")
    else:
        print("No standings data found.")

except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")
