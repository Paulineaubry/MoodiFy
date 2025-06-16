import pandas as pd
import requests
import os
from dotenv import load_dotenv
from tqdm import tqdm

# === 1. Chargement clé API Last.fm ===
load_dotenv()
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")

def get_lastfm_genres(artist_name):
    """
    Récupère les tags (genres) associés à un artiste via l'API Last.fm.
    """
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "artist.gettoptags",
        "artist": artist_name,
        "api_key": LASTFM_API_KEY,
        "format": "json"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "toptags" in data and "tag" in data["toptags"]:
            tags = data["toptags"]["tag"]
            top_tags = [tag["name"] for tag in tags if int(tag.get("count", 0)) > 0]
            return top_tags[:3]  # max 3 genres
        else:
            return []
    except Exception as e:
        print(f"Erreur pour l'artiste '{artist_name}' : {e}")
        return []

# === 2. Charger les données ===
df = pd.read_csv("artists_with_genres.csv")

# === 3. Identifier les lignes où la colonne 'genres' contient exactement '[]'
# Attention : ici c’est une string, pas une vraie liste
mask_missing = df['genres'] == '[]'

# === 4. Compléter les genres vides avec Last.fm ===
for i, row in tqdm(df[mask_missing].iterrows(), total=mask_missing.sum(), desc="Complétion via Last.fm"):
    artist_name = row['artist_name']
    new_genres = get_lastfm_genres(artist_name)
    df.at[i, 'genres'] = str(new_genres)  # On stocke la liste comme string (comme le reste du fichier)

# === 5. Export du nouveau DataFrame ===
df.to_csv("artists_with_genres_completed.csv", index=False)
print("Fichier mis à jour : artists_with_genres_completed.csv")


