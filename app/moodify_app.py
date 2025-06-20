import streamlit as st
import pandas as pd
import random

# Chargement du dataset
df = pd.read_csv("df_test.csv")

# Pondérations par tranche d'âge
AGE_GENRE_WEIGHTS = {
    "15-24": {"Rap": 0.54, "Pop": 0.20, "Electro": 0.15, "Autre": 0.11},
    "25-34": {"Rap": 0.43, "Pop": 0.30, "Variete française": 0.10, "Rock": 0.10, "Autre": 0.07},
    "35-44": {"Variete française": 0.67, "Rock": 0.20, "Jazz": 0.05, "Classique": 0.05, "Autre": 0.03},
    "45-59": {"Variete française": 0.72, "Blues": 0.10, "Rock": 0.08, "Jazz": 0.10},
    "60-69": {"Variete française": 0.81, "Jazz": 0.10, "Classique": 0.09},
    "70+": {"Variete française": 0.89, "Classique": 0.11}
}

# Interface utilisateur
st.title("🎧 Application de recommandation musicale")

age_group = st.selectbox("📅 Choisissez votre tranche d'âge", list(AGE_GENRE_WEIGHTS.keys()))

# Étape 1 : Sélectionner 15 titres selon la pondération
def sample_weighted_songs(df, age_group, n=15):
    weights = AGE_GENRE_WEIGHTS[age_group]
    sampled = []

    for genre, proportion in weights.items():
        genre_df = df[df["genre"] == genre]
        if not genre_df.empty:
            count = max(1, int(proportion * n))
            sampled.extend(genre_df.sample(min(count, len(genre_df))).to_dict(orient="records"))
    
    # Compléter s’il manque
    while len(sampled) < n:
        sampled.append(df.sample(1).iloc[0].to_dict())

    random.shuffle(sampled)
    return sampled[:n]

sampled_tracks = sample_weighted_songs(df, age_group)

# Étape 2 : Choix des titres préférés
st.subheader("🎵 Choisissez vos 5 titres préférés")
selected_titles = st.multiselect(
    "Sélectionnez 5 titres",
    options=[f"{track['track_name']} - {track['artist_name']}" for track in sampled_tracks],
    max_selections=5
)

# Fonction pour retrouver un track_id à partir du nom affiché
def get_track_by_label(label):
    for track in sampled_tracks:
        if f"{track['track_name']} - {track['artist_name']}" == label:
            return track
    return None

if len(selected_titles) == 5:
    st.success("✅ Merci pour votre sélection !")

    # Récupération des track_ids sélectionnés
    selected_tracks = [get_track_by_label(label) for label in selected_titles]

    tab1, tab2, tab3 = st.tabs(["🔁 Song to Song", "😊 Playlist par humeur", "🏃 Playlist par activité"])

    # --- Song to Song ---
    with tab1:
        st.subheader("🔁 Recommandations similaires à un titre")
        track_to_match = st.selectbox("Choisissez un titre", selected_titles)
        track_row = get_track_by_label(track_to_match)
        
        if track_row:
            st.write(f"🎧 Recommandations similaires à : **{track_row['track_name']}**")
            features = ['valence', 'energy', 'danceability', 'acousticness', 'tempo']
            base_vector = df[df["track_id"] == track_row['track_id']][features].iloc[0]
            df["distance"] = df[features].apply(lambda row: ((row - base_vector)**2).sum(), axis=1)
            recommendations = df[df["track_id"] != track_row["track_id"]].sort_values("distance").head(10)
            for _, row in recommendations.iterrows():
                st.write(f"🎶 {row['track_name']} - {row['artist_name']} ({row['genre']})")

    # --- Playlist par humeur ---
    with tab2:
        st.subheader("😊 Sélectionnez une humeur")
        mood = st.selectbox("Choisissez une humeur", df["mood_tag"].unique())
        mood_playlist = df[df["mood_tag"] == mood].sample(10)
        for _, row in mood_playlist.iterrows():
            st.write(f"🎶 {row['track_name']} - {row['artist_name']} ({row['mood_tag']})")

    # --- Playlist par activité ---
    with tab3:
        st.subheader("🏃 Sélectionnez une activité")
        activity = st.selectbox("Choisissez une activité", df["activity_tag"].unique())
        activity_playlist = df[df["activity_tag"] == activity].sample(10)
        for _, row in activity_playlist.iterrows():
            st.write(f"🎶 {row['track_name']} - {row['artist_name']} ({row['activity_tag']})")

else:
    st.info("👉 Sélectionnez exactement 5 titres pour accéder aux recommandations.")

