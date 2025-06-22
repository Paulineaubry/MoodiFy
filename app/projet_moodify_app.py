import streamlit as st
import pandas as pd
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

# Chargement des variables d'environnement
load_dotenv()

SCOPE = "playlist-modify-public playlist-modify-private"

# Instanciation unique du client Spotify, cachée avec st.cache_resource pour éviter erreur de sérialisation
@st.cache_resource
def get_spotify_client():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=SCOPE,
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        cache_path=".env"
    ))

sp = get_spotify_client()

# Fonction cachée pour récupérer l'URL de l'image de l'album via l'API Spotify
@st.cache_data(show_spinner=False)
def get_album_image_url_cached(track_id):
    try:
        track_info = sp.track(track_id)
        images = track_info['album'].get('images', [])
        if images:
            return images[2]['url']  # plus grande image
        return None
    except Exception as e:
        print(f"Erreur récupération image album : {e}")
        return None

# Fonction pour créer une playlist Spotify dans le compte utilisateur
def create_spotify_playlist(track_ids, playlist_name):
    auth_manager = SpotifyOAuth(
        scope=SCOPE,
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        show_dialog=True,
        cache_path=".env"
                )

    sp_local = spotipy.Spotify(auth_manager=auth_manager)

    user_id = sp_local.current_user()["id"]
    playlist = sp_local.user_playlist_create(user=user_id, name=playlist_name, public=True)
    sp_local.playlist_add_items(playlist_id=playlist["id"], items=track_ids)

    return playlist["external_urls"]["spotify"]

# Chargement des données CSV
@st.cache_data
def load_data():
    return pd.read_csv('../data/df_final.csv')

df = load_data()

required_cols = {'tags_humeur', 'tags_activité', 'track_name', 'artist_name', 'duration_ms', 'track_id', 'genre'}
if not required_cols.issubset(df.columns):
    st.error("Certaines colonnes essentielles sont manquantes dans le fichier CSV.")
    st.stop()

# Configuration de la page
st.set_page_config(
    page_title="Ecoute Cha !!!",
    layout="wide",
    initial_sidebar_state="expanded"
)

# En-tête
st.markdown('<h1 class="main-header">Ecoute me Cha !!</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle"> Ton humeur, mon choix ;-) </p>', unsafe_allow_html=True)
st.markdown("---")

# Menu latéral
st.sidebar.markdown("## **Menu Musical**")
choice = st.sidebar.radio(
    "Navigation",
    options=["Song-to-Song", "Mood-to-Playlist", "Activity-to-Playlist"],
    label_visibility="collapsed"
)
st.sidebar.markdown("---")
st.sidebar.markdown("### **À Propos**")
st.sidebar.info("MoodiFy votre humeur, notre choix")

# SONG-TO-SONG (à compléter selon besoins)
if choice == "Song-to-Song":
    st.markdown('<h2 class="section-header">Découvrez des Sons Similaires</h2>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        song_name = st.text_input("Nom de la chanson", placeholder="Ex: Imagine - John Lennon")

# MOOD-TO-PLAYLIST
elif choice == "Mood-to-Playlist":
    st.markdown('<h2 class="section-header">Playlist selon l\'humeur choisie</h2>', unsafe_allow_html=True)

    genres_disponibles = df['genre'].dropna().unique()
    selected_genre = st.selectbox("Choisissez un genre musical :", genres_disponibles)

    humeur_filtrées = df[df['genre'] == selected_genre]['tags_humeur'].dropna().unique()
    selected_humeur = st.selectbox("Choisissez une humeur musicale :", humeur_filtrées)

    if st.button("Générer Playlist"):
        with st.spinner("Création en cours..."):
            time.sleep(1.5)

        filtered_df = df[(df['genre'] == selected_genre) & (df['tags_humeur'] == selected_humeur)]
        filtered_df = filtered_df.sample(frac=1).head(20).reset_index(drop=True)

        if filtered_df.empty:
            st.warning("Aucune chanson trouvée pour cette humeur.")
        else:
            st.success(f"Playlist générée pour l'humeur : {selected_humeur}")
            st.markdown("### Ta Playlist :")

            for i, row in enumerate(filtered_df.itertuples(), 1):
                track_id_clean = row.track_id.split(':')[-1]
                track_url = f"https://open.spotify.com/track/{track_id_clean}"
                image_url = get_album_image_url_cached(track_id_clean)

                col1, col2 = st.columns([1, 5])
                with col1:
                    if image_url:
                        st.image(image_url, width=60)
                with col2:
                    st.markdown(f"{i}. [**{row.track_name}**]({track_url}) – *{row.artist_name}*")

# ACTIVITY-TO-PLAYLIST
elif choice == "Activity-to-Playlist":
    st.markdown('<h2 class="section-header">Playlist selon l\'activité choisie</h2>', unsafe_allow_html=True)

    genres_disponibles = df['genre'].dropna().unique()
    selected_genre = st.selectbox("Choisissez un genre musical :", genres_disponibles)

    activités_filtrées = df[df['genre'] == selected_genre]['tags_activité'].dropna().unique()
    selected_activity = st.selectbox("Choisissez une activité :", activités_filtrées)

    if st.button("Générer Playlist"):
        with st.spinner("Création en cours..."):
            time.sleep(1.5)

        filtered_df = df[(df['genre'] == selected_genre) & (df['tags_activité'] == selected_activity)]
        filtered_df = filtered_df.sample(frac=1).head(20).reset_index(drop=True)

        if filtered_df.empty:
            st.warning("Aucune chanson trouvée pour cette activité.")
        else:
            st.success(f"Playlist générée pour l'activité : {selected_activity} ({len(filtered_df)} titres)")
            st.markdown("### Ta Playlist :")

            track_ids_spotify = []

            for i, row in enumerate(filtered_df.itertuples(), 1):
                track_id_clean = row.track_id.split(':')[-1]
                track_ids_spotify.append(f"spotify:track:{track_id_clean}")
                track_url = f"https://open.spotify.com/track/{track_id_clean}"
                image_url = get_album_image_url_cached(track_id_clean)

                col1, col2 = st.columns([1, 5])
                with col1:
                    if image_url:
                        st.image(image_url, width=60)
                with col2:
                    st.markdown(f"{i}. [**{row.track_name}**]({track_url}) – *{row.artist_name}*")

            if st.button("Créer cette playlist dans mon compte Spotify"):
                try:
                    playlist_url = create_spotify_playlist(track_ids_spotify, f"Playlist - {selected_activity}")
                    st.success("Playlist créée avec succès !")
                    st.markdown(f"[Voir la playlist sur Spotify]({playlist_url})")
                except Exception as e:
                    st.error(f"Erreur lors de la création de la playlist : {e}")

# Footer
st.markdown("---")
st.markdown('<div class="footer-style"><p>Créé par Pauline, Gaelle, Bertrand et Hassan</p></div>', unsafe_allow_html=True)