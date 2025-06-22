import streamlit as st
import pandas as pd
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import plotly.graph_objects as go
import plotly.express as px
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Chargement des variables d'environnement
load_dotenv()

# DÉFINITION DES PERMISSIONS SPOTIFY (SCOPE)
# pour créer des playlists publique et privée
SCOPE = "playlist-modify-public playlist-modify-private"

# Sélectionne des tracks avec des caractéristiques audio diverses
def select_diverse_tracks(df_genre, n_tracks=5):
    # Colonnes des caractéristiques audio (à adapter selon votre dataset)
    audio_cols = ['danceability', 'energy', 'valence', 'acousticness', 'instrumentalness']
    
    # Vérifier quelles colonnes existent réellement
    available_cols = [col for col in audio_cols if col in df_genre.columns]
    
    if not available_cols:
        # Si pas de colonnes audio features, sélection aléatoire
        return df_genre.sample(n=min(n_tracks, len(df_genre)))
    
    # Normaliser les valeurs
    df_normalized = df_genre[available_cols].fillna(0)
    
    # Sélectionner des tracks diverses en utilisant un échantillonnage stratifié
    diverse_tracks = []
    
    # Première track aléatoire
    first_track = df_genre.sample(n=1)
    diverse_tracks.append(first_track.index[0])
    
    # Sélectionner les autres en maximisant la diversité
    remaining_df = df_genre.drop(diverse_tracks)
    
    for _ in range(min(n_tracks-1, len(remaining_df))):
        if remaining_df.empty:
            break
            
        # Calculer la similarité avec les tracks déjà sélectionnées
        selected_features = df_normalized.loc[diverse_tracks]
        remaining_features = df_normalized.loc[remaining_df.index]
        
        if len(selected_features) > 0 and len(remaining_features) > 0:
            # Trouver la track la moins similaire aux déjà sélectionnées
            similarities = cosine_similarity(remaining_features, selected_features)
            min_similarity_idx = np.argmin(similarities.mean(axis=1))
            next_track_idx = remaining_features.index[min_similarity_idx]
        else:
            next_track_idx = remaining_df.sample(n=1).index[0]
        
        diverse_tracks.append(next_track_idx)
        remaining_df = remaining_df.drop([next_track_idx])
    
    return df_genre.loc[diverse_tracks]


# Trouve une track similaire basée sur les caractéristiques audio
def find_similar_track(selected_track, df_genre, audio_features_cols):
    if not audio_features_cols:
        # Si pas de features audio, sélection aléatoire
        other_tracks = df_genre[df_genre['track_id'] != selected_track['track_id']]
        return other_tracks.sample(n=1).iloc[0] if not other_tracks.empty else None
    
    # Exclure la track sélectionnée
    other_tracks = df_genre[df_genre['track_id'] != selected_track['track_id']]
    
    if other_tracks.empty:
        return None
    
    # Calculer la similarité
    selected_features = selected_track[audio_features_cols].fillna(0).values.reshape(1, -1)
    other_features = other_tracks[audio_features_cols].fillna(0).values
    
    similarities = cosine_similarity(selected_features, other_features)[0]
    most_similar_idx = np.argmax(similarities)
    
    return other_tracks.iloc[most_similar_idx]


# Crée un graphique radar de comparaison des caractéristiques audio
def create_comparison_chart(track1, track2, audio_features_cols):
    if not audio_features_cols:
        return None
    
    # Préparer les données
    features = audio_features_cols
    track1_values = [track1.get(feat, 0) for feat in features]
    track2_values = [track2.get(feat, 0) for feat in features]
    
    # Créer le graphique radar
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=track1_values,
        theta=features,
        fill='toself',
        name=f"{track1['track_name'][:20]}...",
        line_color='rgb(31, 119, 180)',
        fillcolor='rgba(31, 119, 180, 0.2)'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=track2_values,
        theta=features,
        fill='toself',
        name=f"{track2['track_name'][:20]}...",
        line_color='rgb(255, 127, 14)',
        fillcolor='rgba(255, 127, 14, 0.2)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title="Comparaison des caractéristiques audio",
        height=400
    )
    
    return fig


# Crée et configure le client Spotify avec authentification OAuth une seule fois
# @st.cache_resource évite de recréer la connexion à chaque rechargement de page
@st.cache_resource
def get_spotify_client():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=SCOPE,
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        cache_path=".cache"
    ))

# Instance globale du client Spotify réutilisée dans toute l'application
sp = get_spotify_client()

# Récupère l'URL de la couverture d'album via l'API Spotify et la met en cache
# show_spinner=False évite d'afficher le loader pendant le chargement des images
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


# Convertit une durée en millisecondes au format lisible 
def format_duration(total_ms):
    total_seconds = int(total_ms / 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        return f"{hours}h {minutes:02d}min {seconds:02d}s"
    else:
        return f"{minutes}min {seconds:02d}s"

# Crée une nouvelle playlist publique sur Spotify avec les chansons données
# Utilise show_dialog=True pour forcer la reconnexion si nécessaire
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

    track_uris = [f"spotify:track:" for tid in track_ids]
    sp_local.playlist_add_items(playlist_id=playlist["id"], items=track_uris)

    return playlist["external_urls"]["spotify"]


@st.cache_data
# Charge le dataset des chansons depuis le fichier CSV et le met en cache
def load_data():
    return pd.read_csv('../data/df_final.csv')

df = load_data()


# Vérification que toutes les colonnes essentielles sont présentes dans le CSV
# Arrête l'application si des colonnes critiques manquent
required_cols = {'tags_humeur', 'tags_activité', 'track_name', 'artist_name', 'duration_ms', 'track_id', 'genre'}
if not required_cols.issubset(df.columns):
    st.error("Certaines colonnes essentielles sont manquantes dans le fichier CSV.")
    st.stop()

# CSS personnalisé pour le design de l'application


# Configuration de la page Streamlit (titre, layout large, sidebar ouverte par défaut)
st.set_page_config(page_title="Ecoute Cha !!!", layout="wide", initial_sidebar_state="expanded")

# CSS personnalisé pour styliser l'affichage des humeurs en gros caractères
st.markdown("""
<style>
.mood-display {font-size: 2em; font-weight: bold; margin: 10px 0;}
</style>
""", unsafe_allow_html=True)

# Interface principale de l'application
st.title("Ecoute me Cha !!")
st.markdown("---")

# Menu de navigation dans la sidebar pour choisir entre les 3 fonctionnalités
st.sidebar.markdown("## **Menu Musical**")
choice = st.sidebar.radio("Navigation", ["Song-to-Song", "Mood-to-Playlist", "Activity-to-Playlist"], label_visibility="collapsed")


# Fonctionnalité playlist selon l'humeur
if choice == "Mood-to-Playlist":
    st.header("Playlist selon l'humeur choisie")
    selected_genre = st.selectbox("Choisissez un genre musical :", df['genre'].dropna().unique())
    humeurs_list = sorted(df[df['genre'] == selected_genre]['tags_humeur'].dropna().unique())

    if humeurs_list:
        mood_index = st.slider("Faites glisser pour choisir votre humeur", 0, len(humeurs_list)-1, len(humeurs_list)//2)
        selected_humeur = humeurs_list[mood_index]
        st.markdown(f"<div class='mood-display'>{selected_humeur}</div>", unsafe_allow_html=True)

        if st.button("Générer Playlist"):
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

# Fonctionnalité playlist selon l'activité
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

# Fonctionnalité chanson pour chanson
elif choice == "Song-to-Song":
    st.header("Découverte musicale : d'une chanson à l'autre")
    
    # Sidebar pour sélection du genre
    selected_genre = st.selectbox("Choisissez votre genre de prédilection :", 
                                  df['genre'].dropna().unique())
    
    # Filtrer le dataset par genre
    df_genre = df[df['genre'] == selected_genre].copy()
    
    if df_genre.empty:
        st.warning("Aucune chanson trouvée pour ce genre.")
    else:
        st.write(f"**{len(df_genre)} chansons disponibles dans le genre {selected_genre}**")
        
        # Identifier les colonnes de caractéristiques audio disponibles
        audio_features_cols = ['danceability', 'energy', 'valence', 'acousticness', 
                              'instrumentalness', 'speechiness', 'liveness']
        available_audio_cols = [col for col in audio_features_cols if col in df_genre.columns]
        
        if not available_audio_cols:
            st.info("ℹLes caractéristiques audio ne sont pas disponibles dans le dataset. La sélection sera basée sur d'autres critères.")
        
        # Sélectionner 5 tracks diverses
        if st.button("Découvrir 5 chansons variées"):
            with st.spinner("Sélection de chansons variées..."):
                diverse_tracks = select_diverse_tracks(df_genre, 5)
                st.session_state['diverse_tracks'] = diverse_tracks
        
        # Afficher les 5 tracks si elles existent
        if 'diverse_tracks' in st.session_state:
            st.subheader("Choisissez une chanson parmi ces 5 options variées :")
            
            # Créer les colonnes pour l'affichage
            cols = st.columns(5)
            
            selected_track_id = None
            
            for idx, (_, track) in enumerate(st.session_state['diverse_tracks'].iterrows()):
                with cols[idx]:
                    # Image de l'album
                    image_url = get_album_image_url_cached(track['track_id'])
                    if image_url:
                        st.image(image_url, width=120)
                    
                    # Informations de la track
                    st.write(f"**{track['track_name'][:20]}{'...' if len(track['track_name']) > 20 else ''}**")
                    st.write(f"*{track['artist_name'][:15]}{'...' if len(track['artist_name']) > 15 else ''}*")
                    
                    # Bouton de sélection
                    if st.button(f"Choisir", key=f"select_{track['track_id']}"):
                        selected_track_id = track['track_id']
                        st.session_state['selected_track'] = track
            
            # Si une track est sélectionnée ou déjà en session
            if 'selected_track' in st.session_state:
                selected_track = st.session_state['selected_track']
                
                st.markdown("---")
                st.subheader("Chanson sélectionnée :")
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    image_url = get_album_image_url_cached(selected_track['track_id'])
                    if image_url:
                        st.image(image_url, width=150)
                
                with col2:
                    track_url = f"https://open.spotify.com/track/{selected_track['track_id']}"
                    st.markdown(f"### [{selected_track['track_name']}]({track_url})")
                    st.markdown(f"**Artiste :** {selected_track['artist_name']}")
                    st.markdown(f"**Durée :** {format_duration(selected_track['duration_ms'])}")
                    st.markdown(f"**Genre :** {selected_track['genre']}")
                
                # Trouver une chanson similaire
                if st.button("Trouver une chanson similaire"):
                    with st.spinner("Recherche d'une chanson similaire..."):
                        similar_track = find_similar_track(selected_track, df_genre, available_audio_cols)
                        if similar_track is not None:
                            st.session_state['similar_track'] = similar_track
                        else:
                            st.error("Aucune chanson similaire trouvée.")
                
                # Afficher la chanson similaire si elle existe
                if 'similar_track' in st.session_state:
                    similar_track = st.session_state['similar_track']
                    
                    st.markdown("---")
                    st.subheader("Chanson recommandée :")
                    
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        similar_image_url = get_album_image_url_cached(similar_track['track_id'])
                        if similar_image_url:
                            st.image(similar_image_url, width=150)
                    
                    with col2:
                        similar_track_url = f"https://open.spotify.com/track/{similar_track['track_id']}"
                        st.markdown(f"### [{similar_track['track_name']}]({similar_track_url})")
                        st.markdown(f"**Artiste :** {similar_track['artist_name']}")
                        st.markdown(f"**Durée :** {format_duration(similar_track['duration_ms'])}")
                        st.markdown(f"**Genre :** {similar_track['genre']}")
                    
                    # Graphique de comparaison
                    if available_audio_cols:
                        st.markdown("---")
                        st.subheader("Comparaison des caractéristiques audio")
                        
                        comparison_chart = create_comparison_chart(
                            selected_track, similar_track, available_audio_cols
                        )
                        
                        if comparison_chart:
                            st.plotly_chart(comparison_chart, use_container_width=True)
                            
                            # Tableau de comparaison
                            comparison_data = {
                                'Caractéristique': available_audio_cols,
                                'Chanson sélectionnée': [round(selected_track.get(col, 0), 3) for col in available_audio_cols],
                                'Chanson recommandée': [round(similar_track.get(col, 0), 3) for col in available_audio_cols]
                            }
                            
                            comparison_df = pd.DataFrame(comparison_data)
                            st.dataframe(comparison_df, use_container_width=True)
        
        # Bouton pour réinitialiser
        if st.button("Recommencer la découverte"):
            for key in ['diverse_tracks', 'selected_track', 'similar_track']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

st.markdown("---")
st.markdown('<div class="footer-style"><p>Créé par Pauline, Gaelle, Bertrand et Hassan</p></div>', unsafe_allow_html=True)