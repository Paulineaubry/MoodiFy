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

@st.cache_resource
def get_spotify_client():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=SCOPE,
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        cache_path=".cache"
    ))

sp = get_spotify_client()

def extract_track_id(uri_or_id):
    return uri_or_id.split(':')[-1] if ':' in uri_or_id else uri_or_id

@st.cache_data(show_spinner=False)
def get_album_image_url_cached(track_id):
    try:
        track_info = sp.track(track_id)
        images = track_info['album'].get('images', [])
        if images:
            return images[0]['url'] if len(images) > 0 else None
        return None
    except Exception as e:
        print(f"Erreur récupération image album : {e}")
        return None

def format_duration(total_ms):
    total_seconds = int(total_ms / 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        return f"{hours}h {minutes:02d}min {seconds:02d}s"
    else:
        return f"{minutes}min {seconds:02d}s"

def create_spotify_playlist(track_ids, playlist_name):
    auth_manager = SpotifyOAuth(
        scope=SCOPE,
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        show_dialog=True,
        cache_path=".cache"
    )

    sp_local = spotipy.Spotify(auth_manager=auth_manager)

    user_id = sp_local.current_user()["id"]
    playlist = sp_local.user_playlist_create(user=user_id, name=playlist_name, public=True)

    track_uris = [f"spotify:track:{extract_track_id(tid)}" for tid in track_ids]
    sp_local.playlist_add_items(playlist_id=playlist["id"], items=track_uris)

    return playlist["external_urls"]["spotify"]

@st.cache_data
def load_data():
    return pd.read_csv('../data/df_final.csv')

df = load_data()

required_cols = {'tags_humeur', 'tags_activité', 'track_name', 'artist_name', 'duration_ms', 'track_id', 'genre'}
if not required_cols.issubset(df.columns):
    st.error("Certaines colonnes essentielles sont manquantes dans le fichier CSV.")
    st.stop()

st.set_page_config(page_title="Ecoute Cha !!!", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.mood-display {font-size: 2em; font-weight: bold; margin: 10px 0;}
</style>
""", unsafe_allow_html=True)

st.title("Ecoute me Cha !!")
st.markdown("---")

st.sidebar.markdown("## **Menu Musical**")
choice = st.sidebar.radio("Navigation", ["Song-to-Song", "Mood-to-Playlist", "Activity-to-Playlist"], label_visibility="collapsed")

if choice == "Mood-to-Playlist":
    st.header("Playlist selon l'humeur choisie")
    selected_genre = st.selectbox("Choisissez un genre musical :", df['genre'].dropna().unique())
    humeurs_list = sorted(df[df['genre'] == selected_genre]['tags_humeur'].dropna().unique())

    if humeurs_list:
        mood_index = st.slider("Faites glisser pour choisir votre humeur", 0, len(humeurs_list)-1, len(humeurs_list)//2)
        selected_humeur = humeurs_list[mood_index]
        st.markdown(f"<div class='mood-display'>{selected_humeur}</div>", unsafe_allow_html=True)

        if st.button("🎵 Générer Playlist"):
            with st.spinner("Création en cours..."):
                time.sleep(1.5)
            filtered_df = df[(df['genre'] == selected_genre) & (df['tags_humeur'] == selected_humeur)].sample(frac=1).head(20)
            if filtered_df.empty:
                st.warning("Aucune chanson trouvée pour cette humeur.")
                if 'playlist_df' in st.session_state:
                    del st.session_state['playlist_df']
                    del st.session_state['playlist_title']
            else:
                st.session_state['playlist_df'] = filtered_df
                st.session_state['playlist_title'] = f"Playlist {selected_humeur} - {selected_genre}"

    if 'playlist_df' in st.session_state:
        filtered_df = st.session_state['playlist_df']
        total_duration_ms = filtered_df['duration_ms'].sum()
        st.success(f"Playlist générée pour : **{st.session_state['playlist_title']}**")
        st.metric("Nombre de titres", len(filtered_df))
        st.metric("Durée totale", format_duration(total_duration_ms))

        for i, row in enumerate(filtered_df.itertuples(), 1):
            track_url = f"https://open.spotify.com/track/{row.track_id}"
            image_url = get_album_image_url_cached(row.track_id)
            col1, col2, col3 = st.columns([1, 4, 1])
            with col1:
                if image_url:
                    st.image(image_url, width=60)
            with col2:
                st.markdown(f"{i}. [**{row.track_name}**]({track_url}) – *{row.artist_name}*")
            with col3:
                st.markdown(f"*{format_duration(row.duration_ms)}*")

        if st.button("Créer cette playlist dans mon compte Spotify"):
            try:
                playlist_url = create_spotify_playlist(filtered_df['track_id'].tolist(), st.session_state['playlist_title'])
                st.success("Playlist créée avec succès !")
                st.markdown(f"[Voir la playlist sur Spotify]({playlist_url})")
            except Exception as e:
                st.error(f"Erreur lors de la création de la playlist : {e}")

elif choice == "Activity-to-Playlist":
    st.header("Playlist selon l'activité choisie")
    selected_genre = st.selectbox("Choisissez un genre musical :", df['genre'].dropna().unique())
    selected_activity = st.selectbox("Choisissez une activité :", df[df['genre'] == selected_genre]['tags_activité'].dropna().unique())

    if st.button("Générer Playlist"):
        with st.spinner("Création en cours..."):
            time.sleep(1.5)
        filtered_df = df[(df['genre'] == selected_genre) & (df['tags_activité'] == selected_activity)].sample(frac=1).head(20)
        if filtered_df.empty:
            st.warning("Aucune chanson trouvée pour cette activité.")
            if 'playlist_df' in st.session_state:
                del st.session_state['playlist_df']
                del st.session_state['playlist_title']
        else:
            st.session_state['playlist_df'] = filtered_df
            st.session_state['playlist_title'] = f"Playlist - {selected_activity}"

    if 'playlist_df' in st.session_state:
        filtered_df = st.session_state['playlist_df']
        total_duration_ms = filtered_df['duration_ms'].sum()
        st.success(f"Playlist générée pour : **{st.session_state['playlist_title']}**")
        st.metric("Nombre de titres", len(filtered_df))
        st.metric("Durée totale", format_duration(total_duration_ms))

        for i, row in enumerate(filtered_df.itertuples(), 1):
            track_url = f"https://open.spotify.com/track/{row.track_id}"
            image_url = get_album_image_url_cached(row.track_id)
            col1, col2, col3 = st.columns([1, 4, 1])
            with col1:
                if image_url:
                    st.image(image_url, width=60)
            with col2:
                st.markdown(f"{i}. [**{row.track_name}**]({track_url}) – *{row.artist_name}*")
            with col3:
                st.markdown(f"*{format_duration(row.duration_ms)}*")

        if st.button("Créer cette playlist dans mon compte Spotify"):
            try:
                playlist_url = create_spotify_playlist(filtered_df['track_id'].tolist(), st.session_state['playlist_title'])
                st.success("Playlist créée avec succès !")
                st.markdown(f"[Voir la playlist sur Spotify]({playlist_url})")
            except Exception as e:
                st.error(f"Erreur lors de la création de la playlist : {e}")
