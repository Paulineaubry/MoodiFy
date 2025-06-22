import pandas as pd
import spotipy
import time
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os
from tqdm import tqdm

# Authentification Spotify 
load_dotenv()
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Charger les données et trier par popularité 
df = pd.read_csv("clean.csv")  # ou "top_100.csv" si on veut faire le test sur l'échantillon

# Extraire la liste d'artistes
artists = df['artist_name']

artist_genres = {}

# Pour chaque artiste, chercher son artist_id via recherche et récupérer les genres
for artist_name in tqdm(artists, desc="Récupération genres artistes"):
    try:
        results = sp.search(q=f'artist:{artist_name}', type='artist', limit=1)
        items = results['artists']['items']
        if items:
            artist_id = items[0]['id']
            genres = items[0]['genres']
            artist_genres[artist_name] = genres
        else:
            artist_genres[artist_name] = []
        time.sleep(0.1)
    except Exception as e:
        print(f"Erreur artiste {artist_name}: {e}")
        artist_genres[artist_name] = []

# Ajouter une colonne genres dans le DataFrame à partir du mapping
df['genre'] = df['artist_name'].map(artist_genres)

df.to_csv("artists_with_genres.csv", index=False) # ou top100_with_genres.csv si on veut l'échantillon
print("Export terminé.")
