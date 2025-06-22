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
        cache_path=".cache"
    ))

sp = get_spotify_client()

# Fonction cachée pour récupérer l'URL de l'image de l'album via l'API Spotify
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

# Fonction pour convertir les millisecondes en format lisible
def format_duration(total_ms):
    """Convertit les millisecondes en format HH:MM:SS ou MM:SS"""
    total_seconds = int(total_ms / 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes:02d}min {seconds:02d}s"
    else:
        return f"{minutes}min {seconds:02d}s"

# Fonction pour créer une playlist Spotify dans le compte utilisateur
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

# CSS pour le style de la jauge avec classes dynamiques par humeur
st.markdown("""
<style>
.mood-gauge {
    text-align: center;
    padding: 20px;
    border-radius: 15px;
    margin: 20px 0;
    color: white;
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Background dynamique selon humeur */
.mood-gauge.calme {
    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.mood-gauge.joyeux {
    background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
}

.mood-gauge.triste {
    background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%);
}

.mood-gauge.energique {
    background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
}

.mood-display {
    font-size: 2em;
    font-weight: bold;
    margin: 10px 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.gauge-description {
    font-size: 1em;
    margin-bottom: 15px;
}

.slider-container {
    margin: 20px 0;
}
</style>
""", unsafe_allow_html=True)

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

# MOOD-TO-PLAYLIST avec JAUGE dynamique
elif choice == "Mood-to-Playlist":
    st.markdown('<h2 class="section-header">Playlist selon l\'humeur choisie</h2>', unsafe_allow_html=True)

    # Sélection du genre
    genres_disponibles = df['genre'].dropna().unique()
    selected_genre = st.selectbox("Choisissez un genre musical :", genres_disponibles)

    # Récupération des humeurs disponibles pour ce genre
    humeurs_disponibles = df[df['genre'] == selected_genre]['tags_humeur'].dropna().unique()
    humeurs_list = sorted(list(humeurs_disponibles))
    
    if len(humeurs_list) > 0:
        st.markdown("### Sélectionnez votre humeur avec la jauge :")
        
        # Création de la jauge (slider)
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            # Slider pour sélectionner l'index de l'humeur
            mood_index = st.slider(
                "Faites glisser pour choisir votre humeur",
                min_value=0,
                max_value=len(humeurs_list) - 1,
                step=1,
                value=len(humeurs_list) // 2,  # Valeur par défaut au milieu
                label_visibility="collapsed",
                key="mood_slider"
            )
            
            # Humeur sélectionnée
            selected_humeur = humeurs_list[mood_index]
            
            
            # Affichage de la jauge avec classe dynamique
            st.markdown(f"""
                <div class="gauge-description">Humeur sélectionnée</div>
                <div class="mood-display">{selected_humeur}</div>
                <div style="font-size: 0.9em; opacity: 0.8;">
                    {mood_index + 1} sur {len(humeurs_list)} humeurs disponibles
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Affichage des autres humeurs disponibles
            st.markdown("**Autres humeurs disponibles :**")
            mood_pills = " | ".join([f"**{mood}**" if mood == selected_humeur else mood for mood in humeurs_list])
            st.markdown(f"<div style='text-align: center; font-size: 0.9em; color: #666;'>{mood_pills}</div>", unsafe_allow_html=True)

        if st.button("🎵 Générer Playlist", use_container_width=True):
            with st.spinner("Création en cours..."):
                time.sleep(1.5)

            filtered_df = df[(df['genre'] == selected_genre) & (df['tags_humeur'] == selected_humeur)]
            filtered_df = filtered_df.sample(frac=1).head(20).reset_index(drop=True)

            if filtered_df.empty:
                st.warning("Aucune chanson trouvée pour cette humeur.")
            else:
                # Calcul de la durée totale
                total_duration_ms = filtered_df['duration_ms'].sum()
                duration_formatted = format_duration(total_duration_ms)
                
                st.success(f"Playlist générée pour l'humeur : **{selected_humeur}** 🎵")
                
                # Affichage des statistiques de la playlist
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    st.metric("Nombre de titres", len(filtered_df))
                with col_stat2:
                    st.metric("Durée totale", duration_formatted)
                with col_stat3:
                    avg_duration = total_duration_ms / len(filtered_df)
                    st.metric("Durée moyenne", format_duration(avg_duration))
                
                st.markdown("### Ta Playlist :")

                for i, row in enumerate(filtered_df.itertuples(), 1):
                    track_id_clean = row.track_id.split(':')[-1]
                    track_url = f"https://open.spotify.com/track/{track_id_clean}"
                    image_url = get_album_image_url_cached(track_id_clean)
                    
                    # Durée de la chanson individuelle
                    song_duration = format_duration(row.duration_ms)

                    col1, col2, col3 = st.columns([1, 4, 1])
                    with col1:
                        if image_url:
                            st.image(image_url, width=60)
                    with col2:
                        st.markdown(f"{i}. [**{row.track_name}**]({track_url}) - {row.artist_name} ({song_duration})", unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"<a href='{track_url}' target='_blank'>🎧</a>", unsafe_allow_html=True)

                # Création playlist Spotify si utilisateur connecté
                if st.session_state.get("spotify_auth"):
                    track_ids = filtered_df['track_id'].tolist()
                    playlist_name = f"Playlist {selected_humeur} - {selected_genre}"
                    try:
                        playlist_url = create_spotify_playlist(track_ids, playlist_name)
                        st.markdown(f"Votre playlist est disponible sur [Spotify]({playlist_url}) 🎉", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Erreur lors de la création de la playlist Spotify : {e}")
                else:
                    st.info("Connectez-vous avec Spotify pour créer la playlist directement.")
    else:
        st.warning("Aucune humeur disponible pour ce genre musical.")


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
            # Calcul de la durée totale pour les activités aussi
            total_duration_ms = filtered_df['duration_ms'].sum()
            duration_formatted = format_duration(total_duration_ms)
            
            st.success(f"Playlist générée pour l'activité : {selected_activity} ({len(filtered_df)} titres)")
            
            # Affichage des statistiques de la playlist
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("Nombre de titres", len(filtered_df))
            with col_stat2:
                st.metric("Durée totale", duration_formatted)
            with col_stat3:
                avg_duration = total_duration_ms / len(filtered_df)
                st.metric("Durée moyenne", format_duration(avg_duration))
            
            st.markdown("### Ta Playlist :")

            track_ids_spotify = []

            for i, row in enumerate(filtered_df.itertuples(), 1):
                track_id_clean = row.track_id.split(':')[-1]
                track_ids_spotify.append(f"spotify:track:{track_id_clean}")
                track_url = f"https://open.spotify.com/track/{track_id_clean}"
                image_url = get_album_image_url_cached(track_id_clean)
                
                # Durée de la chanson individuelle
                song_duration = format_duration(row.duration_ms)

                col1, col2, col3 = st.columns([1, 4, 1])
                with col1:
                    if image_url:
                        st.image(image_url, width=60)
                with col2:
                    st.markdown(f"{i}. [**{row.track_name}**]({track_url}) – *{row.artist_name}*")
                with col3:
                    st.markdown(f"*{song_duration}*")

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