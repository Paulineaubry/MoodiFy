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
        response = requests.get(url, params=params)
        data = response.json()

        if "toptags" in data and "tag" in data["toptags"]:
            tags = data["toptags"]["tag"]
            top_tags = [tag["name"] for tag in tags if int(tag.get("count", 0)) > 0]
            return top_tags[:3]
        else:
            return []
    except Exception as e:
        print(f"Erreur pour l'artiste '{artist_name}' : {e}")
        return []

# === 2. Charger les données ===
df = pd.read_csv("artists_with_genres.csv")

# === 3. S'assurer que la colonne 'genres' est bien des listes (pas des chaînes de type "['pop']") ===
import ast
df['genres'] = df['genres'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

# === 4. Identifier les lignes où la liste de genres est vide ===
df['genres_missing'] = df['genres'].apply(lambda g: isinstance(g, list) and len(g) == 0)

# === 5. Compléter les genres vides avec l'API Last.fm ===
for i, row in tqdm(df[df['genres_missing']].iterrows(), total=df['genres_missing'].sum(), desc="Complétion via Last.fm"):
    artist_name = row['artist_name']
    new_genres = get_lastfm_genres(artist_name)
    df.at[i, 'genres'] = new_genres

# === 6. Nettoyage : supprimer la colonne temporaire ===
df.drop(columns=['genres_missing'], inplace=True)

# === 7. Export du nouveau DataFrame ===
df.to_csv("artists_with_genres_completed.csv", index=False)
print("Fichier mis à jour : artists_with_genres_completed.csv")

