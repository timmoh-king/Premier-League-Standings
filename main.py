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
    else:
        print("No standings data found.")

except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")
