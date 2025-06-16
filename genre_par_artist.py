import pandas as pd
import spotipy
import time
import json
import os
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from tqdm import tqdm

# === 1. Authentification Spotify ===
load_dotenv()
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# === 2. Charger les artistes ===
df = pd.read_csv("artists_unique.csv")  # ou top_100.csv pour test
artists = df['artist_name'].dropna().unique()

# === 3. Charger cache si existant ===
CACHE_FILE = "artist_genres_cache.json"
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        artist_genres = json.load(f)
else:
    artist_genres = {}

# === 4. Traitement des artistes ===
for artist_name in tqdm(artists, desc="Récupération genres artistes"):
    if artist_name in artist_genres:
        continue  # Déjà traité

    try:
        results = sp.search(q=f'artist:{artist_name}', type='artist', limit=1)
        items = results['artists']['items']
        if items:
            genres = items[0]['genres']
            artist_genres[artist_name] = genres
        else:
            artist_genres[artist_name] = []

    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 429:
            retry_after = int(e.headers.get("Retry-After", 10))
            print(f"[Rate Limit] Attente de {retry_after} sec pour {artist_name}")
            time.sleep(retry_after)
            continue
        else:
            print(f"[Erreur Spotify] {artist_name}: {e}")
            artist_genres[artist_name] = []

    except Exception as e:
        print(f"[Erreur générale] {artist_name}: {e}")
        artist_genres[artist_name] = []

    # Sauvegarde du cache à chaque itération
    with open(CACHE_FILE, "w") as f:
        json.dump(artist_genres, f)

    time.sleep(0.1)  # Petite pause pour éviter surcharge

# === 5. Ajout des genres au DataFrame final ===
df['genres'] = df['artist_name'].map(artist_genres)

# === 6. Export CSV final ===
df.to_csv("artists_with_genres.csv", index=False)
print("Export terminé dans 'artists_with_genres.csv'")

