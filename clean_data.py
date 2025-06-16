import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import requests
from tqdm import tqdm
import numpy as np

# Chargement du CSV de base
df = pd.read_csv("SpotifyFeatures.csv")

# Remplissage de la valeur nulle
df = df.fillna('None')

# Retire la colonne genre
df= df.drop(columns=['genre'])

# Normalise les noms d'artiste pour éviter les doublons
df['artist_name'] = df['artist_name'].str.replace('’', "'",  regex=False)  # apostrophe typographique
df['artist_name'] = df['artist_name'].str.lower().str.strip()  # minuscule + suppression espaces 

# Normalise les noms des chansons 
df['track_name'] = df['track_name'].str.replace('’', "'",  regex=False)  # apostrophe typographique
df['track_name'] = df['track_name'].str.lower().str.strip()  # minuscule + suppression espaces  

# Crée une df des doublons de track_id
df_duplicates = df[df.duplicated(subset=['track_id'])]

audio_features = ['acousticness', 'danceability', 'duration_ms', 'energy', 
                  'instrumentalness', 'key', 'liveness', 'loudness', 'mode', 
                  'speechiness', 'tempo', 'time_signature', 'valence']

# Identifier les track_id avec des valeurs incohérentes
problematic_tracks = []

for track_id, group in df_duplicates.groupby('track_id'):
    for col in audio_features:
        if group[col].nunique() > 1:
            problematic_tracks.append(track_id)
            break  

# Supprimer ces track_id du DataFrame
df_clean = df[~df['track_id'].isin(problematic_tracks)]

# Garder la ligne avec la popularité max pour chaque track_id
df = df_clean.loc[df_clean.groupby('track_id')['popularity'].idxmax()]

# Pour éviter les doublons, nous conservons la version la plus populaire pour chaque couple track_name / artist_name.
df= df.loc[df.groupby(['track_name', 'artist_name'])['popularity'].idxmax()]

# Extraire uniquement le numérateur de la signature [2, 3, 4, 5] pour en faire une colonne numérique propre.
# Étape 1 : Extraire la partie avant le '/' et la convertir en entier
df['time_signature'] = df['time_signature'].str.extract(r'^(\d+)').astype('Int64')
df = df[df['time_signature'].isin([1, 3, 4, 5])]

# Pour chaque titre de chanson unique (track_name) sélectionne la ligne ayant la popularité maximale (popularity) dans le DataFrame df
df = df.loc[df.groupby('track_name')['popularity'].idxmax()]

# On décide de ne garder que les scores au dessus de 20/100 de popularité.
df = df[df['popularity'] >= 20] 

# duration_ms entre 1min et 6min
df = df[(df['duration_ms'] >= 60000) & (df['duration_ms'] <= 360000)]

# Garde les valeurs au dessus de 0.8 sur liveness
df = df[df['liveness'] < 0.8]

# Retire les lignes qui contiennent ces motifs: "- live", "(live)", "[live]"
df = df[~df['track_name'].str.contains(r"(?:-\s*live\b|\(live\)|\[live\])", case=False, na=False, regex=True)]

# Clean en gardant les valeurs entre les bornes
df = df[(df['tempo'] >= 23.82) & (df['tempo'] <= 208.20)]

# Clean des valeurs incohérentes de loudness au dessus de 0
df = df[df['loudness'] <= 0]

# Clean des possibles podcasts/conférences au dela de 0.66 sur speechiness
df_clean = df[df['speechiness']<=0.66]

df_clean.to_csv("clean.csv", index=False)





