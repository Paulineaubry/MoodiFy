import pandas as pd
df = pd.read_csv('artists_with_genres_completed.csv')

def classer_genre(row):
    # Priorité : genre_group > genres > artist_name
    text = ''
    if pd.notna(row['genre_group']):
        text = row['genre_group'].lower()
    elif pd.notna(row['genres']):
        text = row['genres'].lower()
    elif pd.notna(row['artist_name']):
        text = row['artist_name'].lower()

    if "rap" in text or "hip hop" in text or "trap" in text:
        return "rap"
    elif "pop" in text:
        return "pop"
    elif "jazz" in text or "blues" in text:
        return "jazz/blues"
    elif "rock" in text or "indie" in text:
        return "rock/indie"
    elif "electro" in text or "dance" in text or "house" in text or "techno" in text:
        return "électro/dance"
    elif "classique" in text or "opera" in text:
        return "classique/opéra"
    else:
        return "autre"
    

def genre_audio(row):
    if row['speechiness'] > 0.33 and row['danceability'] > 0.6 and row['valence'] < 0.5:
        return 'rap'
    elif row['danceability'] > 0.7 and row['energy'] > 0.6 and row['acousticness'] < 0.3:
        return 'électro/dance'
    elif row['acousticness'] > 0.6 and row['valence'] > 0.5:
        return 'variété française'
    elif row['instrumentalness'] > 0.8:
        return 'classique/opéra'
    elif row['energy'] < 0.4 and row['valence'] < 0.4:
        return 'jazz/blues'
    elif row['energy'] > 0.7 and row['valence'] > 0.5 and row['speechiness'] < 0.1:
        return 'rock/indie'
    else:
        return 'pop'
    
df["genre_simplifié"] = df.apply(classer_genre, axis=1)
df['genre_audio'] = df.apply(genre_audio, axis=1)


# Sauvegarder le DataFrame avec les genres simplifiés
df.to_csv("df_enr_genres.csv", index=False)