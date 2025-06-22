import streamlit as st
import pandas as pd

# Charger les données
df = pd.read_csv('../data/df_final.csv')

# Vérifiez les colonnes et ajustez si nécessaire
if 'mood_tag' not in df.columns:
    df['mood_tag'] = df['tags_humeur'].str.strip('#')
if 'activity_tag' not in df.columns:
    df['activity_tag'] = df['tags_activité'].str.split('/').str[0].str.strip('#')

# Interface utilisateur
st.title("Application de recommandation musicale")

# Sélection aléatoire de quelques pistes pour la démonstration
sampled_tracks = df.sample(10)
selected_titles = st.multiselect("Sélectionnez 5 titres", [f"{track['track_name']} - {track['artist_name']}" for _, track in sampled_tracks.iterrows()])

# Fonction pour retrouver un track_id à partir du nom affiché
def get_track_by_label(label):
    for _, track in sampled_tracks.iterrows():
        if f"{track['track_name']} - {track['artist_name']}" == label:
            return track
    return None

if len(selected_titles) == 5:
    st.success(" Merci pour votre sélection !")

    # Récupération des pistes sélectionnées
    selected_tracks = [get_track_by_label(label) for label in selected_titles]

    tab1, tab2, tab3 = st.tabs([" Song to Song", " Playlist par humeur", " Playlist par activité"])

    # --- Song to Song ---
    with tab1:
        st.subheader("Recommandations similaires à un titre")
        track_to_match = st.selectbox("Choisissez un titre", selected_titles)
        track_row = get_track_by_label(track_to_match)

        if track_row:
            st.write(f"Recommandations similaires à : **{track_row['track_name']}**")
            features = ['valence', 'energy', 'danceability', 'acousticness', 'tempo']
            base_vector = df[df["track_id"] == track_row['track_id']][features].iloc[0]
            df["distance"] = df[features].apply(lambda row: ((row - base_vector)**2).sum(), axis=1)
            recommendations = df[df["track_id"] != track_row["track_id"]].sort_values("distance").head(10)
            for _, row in recommendations.iterrows():
                st.write(f"🎶 {row['track_name']} - {row['artist_name']} ({row['genre']})")

    # --- Playlist par humeur ---
    with tab2:
        st.subheader(" Sélectionnez une humeur")
        mood = st.selectbox("Choisissez une humeur", df["mood_tag"].unique())
        mood_playlist = df[df["mood_tag"] == mood].sample(10)
        for _, row in mood_playlist.iterrows():
            st.write(f"🎶 {row['track_name']} - {row['artist_name']} ({row['mood_tag']})")

    # --- Playlist par activité ---
    with tab3:
        st.subheader("Sélectionnez une activité")
        activity = st.selectbox("Choisissez une activité", df["activity_tag"].unique())
        activity_playlist = df[df["activity_tag"] == activity].sample(10)
        for _, row in activity_playlist.iterrows():
            st.write(f"{row['track_name']} - {row['artist_name']} ({row['activity_tag']})")

else:
    st.info("Sélectionnez exactement 5 titres pour accéder aux recommandations.")

# Générateur de Playlist
st.title('Générateur de Playlist')

# Sélection du genre
genres = df['genre'].unique()
selected_genre = st.selectbox('Sélectionnez un genre', genres)

# Sélection de l'activité
activities = df['activity_tag'].unique()
selected_activity = st.selectbox('Sélectionnez une activité', activities)

# Générer la playlist
if st.button('Générer Playlist'):
    playlist = df[(df['genre'] == selected_genre) & (df['activity_tag'] == selected_activity)]
    if not playlist.empty:
        st.write(f"Playlist pour le genre '{selected_genre}' et l'activité '{selected_activity}':")
        st.dataframe(playlist[['artist_name', 'track_name', 'popularity', 'danceability']])
    else:
        st.write("Aucune piste trouvée pour les critères sélectionnés.")



