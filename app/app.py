import streamlit as st
import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval

import pandas as pd
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.preprocessing import StandardScaler

import pickle



def load_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600&display=swap');

    :root {
        --bg-top: #7a5ba2;
        --bg-bottom: #e8b4e0;
        --sidebar-bg-top: #1a1a40;
        --sidebar-bg-bottom: #6a4c93;
        --text-cream: #F5F5DC;
        --selectbox-color: #8FAAC4;
        --selectbox-border-color: #8FAAC4;
        --console-base: #d8c3e0;
        --console-shadow: #b8a3c0;
        --text-primary: #333333;
        --text-secondary: #8a6db8;
        --joy: #78c4d4;
        --sadness: #4A90E2;
        --disgust: #4CAF50;
        --fear: #B084CC;
        --gradient-bg: linear-gradient(to bottom, var(--bg-top), var(--bg-bottom));
        --sidebar-gradient-bg: linear-gradient(to bottom, var(--sidebar-bg-top), var(--sidebar-bg-bottom));
    }

    body, .stApp {
        background: var(--gradient-bg);
        font-family: 'Segoe UI', sans-serif;
        color: var(--text-primary);
    }

    /* Sidebar background */
    [data-testid="stSidebar"] {
        background: var(--sidebar-gradient-bg) !important;
    }

    /* Change the color of the selected item in the sidebar */
    [data-testid="stSidebar"] .css-1lcbmhc {
        color: white !important;
    }

    /* Remove the red background color from the selected item in the sidebar */
    [data-testid="stSidebar"] .css-1lcbmhc:hover, [data-testid="stSidebar"] .css-1lcbmhc:focus, [data-testid="stSidebar"] .css-1lcbmhc:active {
        background-color: transparent !important;
    }

    /* Change the color of the selection indicator in the sidebar */
    [data-testid="stSidebar"] .css-14xtw73::before {
        background-color: white !important;
    }
                    

    /* Style for the selectbox dropdown */
    .stSelectbox > div > div {
        background-color: var(--selectbox-color) !important;
        color: var(--text-primary) !important;
        border: 2px solid var(--selectbox-border-color) !important;
        border-radius: 20px !important;
    }

    /* Style for the selectbox dropdown in the sidebar */
    [data-testid="stSidebar"] .stSelectbox > div > div {
        color: white !important;
    }

    /* Style for the dropdown options */
    .stSelectbox > div > div > div > div {
        background-color: var(--selectbox-color) !important;
        color: white !important;
    }

    /* Style for the radio button indicator */
    [data-testid="stSidebar"] .stRadio > div > label > div[data-testid="stMarkdownContainer"] > div {
        color: white !important;
    }

    h1, h2, h3 {
        font-weight: 600 !important;
        color: var(--text-cream) !important;
        text-align: center;
        text-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
    }

    .song-title {
        color: var(--joy);
        font-size: 1.4rem;
        font-weight: 500;
        text-align: center;
        margin: 0.5rem 0;
    }

    .song-title:hover {
        color: var(--joy);
        transition: color 0.3s ease;
    }

    .stButton > button {
        background: var(--console-base) !important;
        border: 2px solid var(--text-primary) !important;
        border-radius: 20px !important;
        padding: 0.6rem 1.5rem !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        background: var(--joy) !important;
        color: var(--text-primary) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(120, 196, 212, 0.4);
    }

    .track-item, .selection-card {
        background: var(--console-base);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid var(--console-shadow);
        transition: all 0.3s ease;
    }

    .track-item:hover, .selection-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        border-color: var(--joy);
    }

    .footer-style {
        text-align: center !important;
        padding: 1.5rem !important;
        background: var(--console-base) !important;
        border-radius: 15px !important;
        margin-top: 2rem !important;
        border: 1px solid var(--console-shadow) !important;
    }

    .footer-style p {
        color: var(--text-secondary) !important;
        font-style: italic !important;
        font-size: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)





class MoodifyRecommender:
    def __init__(self, model_path, data_path):
        self.model_info = self.charger_modele(model_path)

        if self.model_info is None:
            raise ValueError("Impossible de charger le modèle ML")

        # Si c'est un dict, on extrait le modèle et les infos
        if isinstance(self.model_info, dict):
            self.model = self.model_info.get('model', None)
            self.cluster_profiles = self.model_info.get('cluster_profiles', {})
        else:
            self.model = self.model_info
            self.cluster_profiles = {}

        self.features = ['danceability', 'energy', 'valence', 'tempo']

        self.df_songs = pd.read_csv(data_path)
        self.songs_processed = None
        self.songs_scaled = None
        self.clusters_assigned = None

        if self.model:
            self.preparer_donnees()
        else:
            raise ValueError("Modèle sklearn introuvable")

    def charger_modele(self, model_path):
        try:
            print(f"[DEBUG] Tentative de chargement du modèle depuis : {model_path}")
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            print(f"[DEBUG] Modèle chargé : {type(model)}")
            return model
        except Exception as e:
            print(f"[ERREUR] Erreur lors du chargement du modèle: {e}")
            return None

    def preparer_donnees(self):
        self.songs_processed = self.df_songs[self.features].dropna()
        # Scaling des données pour les distances et similarités
        scaler = StandardScaler()
        self.songs_scaled = scaler.fit_transform(self.songs_processed)

        # Affectation des clusters (fit_predict de DBSCAN)
        self.clusters_assigned = self.model.fit_predict(self.songs_processed)

        self.df_songs_with_clusters = self.df_songs.loc[self.songs_processed.index].copy()
        self.df_songs_with_clusters['cluster'] = self.clusters_assigned

    def get_song_profile(self, song_index):
        if song_index not in self.df_songs_with_clusters.index:
            return {}
        song_data = self.df_songs_with_clusters.loc[song_index]
        song_cluster = song_data['cluster']
        cluster_profile = self.cluster_profiles.get(song_cluster, {})
        song_features = {feature: song_data.get(feature, 0) for feature in self.features}
        return {
            'song_info': song_data.to_dict(),
            'cluster': song_cluster,
            'cluster_profile': cluster_profile,
            'features': song_features
        }
    def recommander_songs_similaires(self, song_index, n_recommendations=5, method='cluster_cosine'):
        """
        Recommande des chansons similaires à une chanson donnée.
        
        Args:
            song_index: index de la chanson dans df_songs (index du DataFrame original)
            n_recommendations: nombre de recommandations
            method: 'cluster_cosine', 'cluster_euclidean' ou 'global_cosine'
            
        Returns:
            DataFrame avec les chansons similaires et leur score
        """
        if self.songs_scaled is None or self.clusters_assigned is None:
            raise ValueError("Les données n'ont pas été préparées avec preparer_donnees()")
            
        if song_index not in self.df_songs_with_clusters.index:
            print(f"La chanson {song_index} n'existe pas dans le jeu de données traité.")
            return pd.DataFrame()
        
        # Position dans le tableau numpy
        pos = list(self.songs_processed.index).index(song_index)
        target_vector = self.songs_scaled[pos].reshape(1, -1)
        
        if method.startswith('cluster'):
            cluster_id = self.df_songs_with_clusters.loc[song_index, 'cluster']
            cluster_indices = self.df_songs_with_clusters[self.df_songs_with_clusters['cluster'] == cluster_id].index
            cluster_pos = [list(self.songs_processed.index).index(i) for i in cluster_indices if i != song_index]
            
            if not cluster_pos:
                print("Pas d'autres chansons dans le cluster.")
                return pd.DataFrame()
            
            cluster_vectors = self.songs_scaled[cluster_pos]
            
            if method == 'cluster_cosine':
                similarities = cosine_similarity(target_vector, cluster_vectors)[0]
                indices_sorted = np.argsort(-similarities)
                scores = similarities[indices_sorted]
            elif method == 'cluster_euclidean':
                distances = euclidean_distances(target_vector, cluster_vectors)[0]
                indices_sorted = np.argsort(distances)
                scores = 1 / (1 + distances[indices_sorted])  # conversion en score simple
            else:
                print(f"Méthode inconnue: {method}")
                return pd.DataFrame()
            
            selected_pos = np.array(cluster_pos)[indices_sorted[:n_recommendations]]
            
        elif method == 'global_cosine':
            similarities = cosine_similarity(target_vector, self.songs_scaled)[0]
            similarities[pos] = -1  # exclure la chanson elle-même
            indices_sorted = np.argsort(-similarities)
            scores = similarities[indices_sorted]
            selected_pos = indices_sorted[:n_recommendations]
            
        else:
            print(f"Méthode inconnue: {method}")
            return pd.DataFrame()
        
        indices_selected = [self.songs_processed.index[i] for i in selected_pos]
        df_result = self.df_songs_with_clusters.loc[indices_selected].copy()
        df_result['similarity_score'] = scores[:len(df_result)]
        
        return df_result.reset_index()


# -------- FONCTION ADAPTÉE POUR SÉLECTIONNER DES TRACKS DIVERSES AVEC ML -------- #

def select_diverse_tracks_ml(recommender, genre, n_tracks=5):
    """
    Sélectionne des tracks diverses en utilisant le clustering ML
    """
    # Filtrer par genre dans le dataset du recommender
    df_genre = recommender.df_songs_with_clusters[
        recommender.df_songs_with_clusters['genre'] == genre
    ].copy()
    
    if df_genre.empty:
        return pd.DataFrame()
    
    # Sélectionner des tracks de différents clusters
    clusters = df_genre['cluster'].unique()
    diverse_tracks = []
    
    # Prendre au moins une track de chaque cluster
    for cluster in clusters[:n_tracks]:
        cluster_tracks = df_genre[df_genre['cluster'] == cluster]
        if not cluster_tracks.empty:
            # Prendre une track aléatoire du cluster
            selected_track = cluster_tracks.sample(n=1)
            diverse_tracks.append(selected_track)
    
    # Si on n'a pas assez de tracks, compléter avec des sélections aléatoires
    while len(diverse_tracks) < n_tracks and len(diverse_tracks) < len(df_genre):
        remaining_tracks = df_genre.drop([t.index[0] for t in diverse_tracks])
        if not remaining_tracks.empty:
            diverse_tracks.append(remaining_tracks.sample(n=1))
        else:
            break
    
    if diverse_tracks:
        return pd.concat(diverse_tracks)
    else:
        return pd.DataFrame()


# -------- FONCTION ADAPTÉE POUR CRÉER LE GRAPHIQUE DE COMPARAISON AVEC ML -------- #

def create_ml_comparison_chart(selected_track, similar_track, recommender):
    """
    Crée un graphique de comparaison basé sur les features ML
    """
    if not recommender.features:
        return None
    
    # Préparer les données
    features = recommender.features
    track1_values = [selected_track.get(feat, 0) for feat in features]
    track2_values = [similar_track.get(feat, 0) for feat in features]
    
    # Créer le graphique radar
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=track1_values,
        theta=features,
        fill='toself',
        name=f"{selected_track['track_name'][:20]}...",
        line_color='rgb(31, 119, 180)',
        fillcolor='rgba(31, 119, 180, 0.2)'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=track2_values,
        theta=features,
        fill='toself',
        name=f"{similar_track['track_name'][:20]}...",
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
        title="Comparaison des caractéristiques audio (ML)",
        height=400
    )
    
    return fig


# -------- SECTION SONG-TO-SONG ADAPTÉE AVEC ML -------- #

def song_to_song_ml_section():
    """
    Section Song-to-Song utilisant le système de recommandation ML
    """
    st.header("Découverte musicale intelligente : d'une chanson à l'autre")
    st.markdown("*Basée sur votre modèle de clustering ML entraîné*")
    
    # Initialisation du recommandeur
    if 'recommender' not in st.session_state:
        try:
            # MODIFIEZ CES CHEMINS SELON VOS FICHIERS
            model_path = os.path.join(os.path.dirname(__file__), 'meilleur_modele.pkl')
            data_path = os.path.join(os.path.dirname(__file__), '../data/df_final.csv')

            
            with st.spinner("Chargement du modèle ML..."):
                st.session_state.recommender = MoodifyRecommender(model_path, data_path)
            
            if st.session_state.recommender.model_info is None:
                st.error("Impossible de charger le modèle ML")
                return
            else:
                st.success("Modèle ML chargé avec succès!")
                
        except Exception as e:
            st.error(f"Erreur d'initialisation: {e}")
            st.info("Vérifiez que les chemins vers votre modèle et vos données sont corrects.")
            return
    

    recommender = st.session_state.recommender
    recommender.preparer_donnees()

    # Sélection du genre
    available_genres = recommender.df_songs_with_clusters['genre'].dropna().unique()
    selected_genre = st.selectbox("Choisissez votre genre de prédilection :", available_genres)
    
    # Filtrer le dataset par genre
    genre_count = len(recommender.df_songs_with_clusters[
        recommender.df_songs_with_clusters['genre'] == selected_genre
    ])
    
    if genre_count == 0:
        st.warning("Aucune chanson trouvée pour ce genre.")
        return
    
    st.write(f"**{genre_count} chansons disponibles dans le genre {selected_genre}**")
    st.info(f"Modèle utilise {len(recommender.features)} caractéristiques audio : {', '.join(recommender.features)}")
    
    # Méthode de recommandation
    recommendation_method = st.selectbox(
        "Méthode de recommandation :",
        options=['cluster_cosine', 'cluster_euclidean', 'global_cosine'],
        format_func=lambda x: {
            'cluster_cosine': 'Cluster + Similarité Cosinus (Recommandé)',
            'cluster_euclidean': 'Cluster + Distance Euclidienne',
            'global_cosine': 'Global Cosinus'
        }[x]
    )
    
    # Sélectionner 5 tracks diverses
    if st.button("Découvrir 5 chansons variées (ML)"):
        with st.spinner("Sélection intelligente en cours..."):
            diverse_tracks = select_diverse_tracks_ml(recommender, selected_genre, 5)
            if not diverse_tracks.empty:
                st.session_state['diverse_tracks_ml'] = diverse_tracks
                st.session_state['recommendation_method'] = recommendation_method
                st.success(f" {len(diverse_tracks)} chansons sélectionnées de différents clusters!")
            else:
                st.error("Aucune chanson trouvée pour ce genre.")
    
    # Afficher les 5 tracks si elles existent
    if 'diverse_tracks_ml' in st.session_state:
        st.subheader("Choisissez une chanson parmi ces options variées :")
        
        diverse_tracks = st.session_state['diverse_tracks_ml']
        
        # Afficher les informations sur les clusters
        clusters_info = diverse_tracks['cluster'].value_counts()
        st.write(f"**Répartition par cluster :** {dict(clusters_info)}")
        
        # Créer les colonnes pour l'affichage
        cols = st.columns(min(5, len(diverse_tracks)))
        
        for idx, (track_idx, track) in enumerate(diverse_tracks.iterrows()):
            if idx < len(cols):
                with cols[idx]:
                    # Image de l'album
                    image_url = get_album_image_url_cached(track['track_id'])
                    if image_url:
                        st.image(image_url, width=120)
                    
                    # Informations de la track
                    st.write(f"**{track['track_name'][:20]}{'...' if len(track['track_name']) > 20 else ''}**")
                    st.write(f"*{track['artist_name'][:15]}{'...' if len(track['artist_name']) > 15 else ''}*")
                    st.write(f"Cluster: {track['cluster']}")
                    
                    # Bouton de sélection
                    if st.button(f"Choisir", key=f"select_ml_{track_idx}"):
                        st.session_state['selected_track_ml'] = track
                        st.session_state['selected_track_index'] = track_idx
        
        # Si une track est sélectionnée
        if 'selected_track_ml' in st.session_state:
            selected_track = st.session_state['selected_track_ml']
            selected_index = st.session_state['selected_track_index']
            
            st.markdown("---")
            st.subheader("Chanson sélectionnée :")
            
            # Afficher le profil de la chanson
            song_profile = recommender.get_song_profile(selected_index)
            if song_profile:
                col1, col2 = st.columns([2, 1])
                with col1:
                    # Lecteur Spotify intégré
                    embed_url = f"https://open.spotify.com/embed/track/{selected_track['track_id']}"
                    st.markdown(
                        f"""
                        <iframe style="border-radius:12px" src="{embed_url}" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
                        """,
                        unsafe_allow_html=True 
                    )
                
                with col2:
                    st.metric("Cluster", song_profile['cluster'])
                    if 'cluster_profile' in song_profile and song_profile['cluster_profile']:
                        st.write("**Profil du cluster :**")
                        for key, value in song_profile['cluster_profile'].items():
                            if isinstance(value, (int, float)):
                                st.write(f"• {key}: {value:.3f}")
            
            # Trouver des chansons similaires avec ML
            if st.button("Trouver des chansons similaires (ML)"):
                with st.spinner("Analyse ML en cours..."):
                    method = st.session_state.get('recommendation_method', 'cluster_cosine')
                    similar_tracks = recommender.recommander_songs_similaires(
                        selected_index, 
                        n_recommendations=5, 
                        method=method
                    )
                    
                    if not similar_tracks.empty:
                        st.session_state['similar_tracks_ml'] = similar_tracks
                        st.rerun()
                    else:
                        st.error("Aucune chanson similaire trouvée.")
            
            # Afficher les recommandations
            if 'similar_tracks_ml' in st.session_state:
                similar_tracks = st.session_state['similar_tracks_ml']
                
                st.markdown("---")
                st.subheader("Chansons recommendées par l'IA :")
                
                # Statistiques des recommandations
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Recommandations", len(similar_tracks))
                with col2:
                    avg_similarity = similar_tracks['similarity_score'].mean()
                    st.metric("Similarité moyenne", f"{avg_similarity:.3f}")
                with col3:
                    clusters_in_reco = similar_tracks['cluster'].nunique()
                    st.metric("Clusters représentés", clusters_in_reco)
                
                # Affichage des recommandations avec scores
                for idx, (reco_idx, track) in enumerate(similar_tracks.iterrows()):
                    with st.expander(
                        f"{track['track_name']} - {track['artist_name']} "
                        f"(Similarité: {track['similarity_score']:.3f}, Cluster: {track['cluster']})"
                    ):
                        embed_url = f"https://open.spotify.com/embed/track/{track['track_id']}"
                        st.markdown(
                            f"""
                            <iframe style="border-radius:12px" src="{embed_url}" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
                            """,
                            unsafe_allow_html=True 
                        )
                
                # Graphique de comparaison avec la première recommandation
                if len(similar_tracks) > 0:
                    first_recommendation = similar_tracks.iloc[0]
                    
                    st.markdown("---")
                    st.subheader("Comparaison des caractéristiques (ML)")
                    
                    comparison_chart = create_ml_comparison_chart(
                        selected_track, first_recommendation, recommender
                    )
                    
                    if comparison_chart:
                        st.plotly_chart(comparison_chart, use_container_width=True)
                        
                        # Tableau de comparaison détaillé
                        comparison_data = {
                            'Caractéristique': recommender.features,
                            'Chanson sélectionnée': [round(selected_track.get(col, 0), 3) for col in recommender.features],
                            'Meilleure recommandation': [round(first_recommendation.get(col, 0), 3) for col in recommender.features]
                        }
                        
                        comparison_df = pd.DataFrame(comparison_data)
                        st.dataframe(comparison_df, use_container_width=True)
        
        # Bouton pour réinitialiser
        if st.button("Recommencer la découverte"):
            keys_to_remove = [
                'diverse_tracks_ml', 'selected_track_ml', 'selected_track_index', 
                'similar_tracks_ml', 'recommendation_method'
            ]
            for key in keys_to_remove:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()




# -------- Sélectionne des tracks avec des caractéristiques audio diverses -------- #

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


# -------- Trouve une track similaire basée sur les caractéristiques audio -------- #

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


# -------- Crée un graphique radar de comparaison des caractéristiques audio -------- #

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


# -------- Crée et configure le client Spotify avec authentification OAuth une seule fois -------- #

@st.cache_resource          # évite de recréer la connexion à chaque rechargement de page

def get_spotify_client():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=SCOPE,
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        cache_path=".cache"
    ))


# -------- Récupère l'URL de la couverture d'album via l'API Spotify et la met en cache -------- #

@st.cache_data(show_spinner=False)        # évite d'afficher le loader pendant le chargement des images

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


# -------- Convertit une durée en millisecondes au format lisible -------- #

def format_duration(total_ms):
    total_seconds = int(total_ms / 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        return f"{hours}h {minutes:02d}min {seconds:02d}s"
    else:
        return f"{minutes}min {seconds:02d}s"


# -------- Crée une nouvelle playlist publique sur Spotify avec les chansons données --------- #

def create_spotify_playlist(track_ids, playlist_name):




    auth_manager = SpotifyOAuth(
        scope=SCOPE,
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        show_dialog=True, # forcer la reconnexion si nécessaire
        cache_path=".cache"
    )

    # Crée un objet Spotify connecté avec l’authentification donnée
    # Récupère l’identifiant de l’utilisateur connecté
    # Crée une nouvelle playlist publique avec le nom donné pour cet utilisateur
    # Prépare la liste des URI des chansons à ajouter dans la playlist
    # Ajoute les chansons à la playlist créée
    # Retourne le lien web pour accéder à la playlist sur Spotify

    sp_local = spotipy.Spotify(auth_manager=auth_manager)
    user_id = sp_local.current_user()["id"]
    playlist = sp_local.user_playlist_create(user=user_id, name=playlist_name, public=True)
    track_uris = [f"spotify:track:{tid}" for tid in track_ids]
    sp_local.playlist_add_items(playlist_id=playlist["id"], items=track_uris)
    return playlist["external_urls"]["spotify"]



# -------- Charge le dataset des chansons depuis le fichier CSV et le met en cache -------- #

@st.cache_data
def load_data():
    return pd.read_csv('../data/df_final.csv')

# Instancie ton recommender une seule fois au début (ou dans une condition pour éviter de le recharger plusieurs fois)
@st.cache_resource  # pour ne pas le recréer à chaque interaction
def load_recommender():
    model_path = 'meilleur_modele.pkl'  
    data_path = '../data/df_final.csv' 
    return MoodifyRecommender(model_path, data_path)








# charge la variable de classe recommender
recommender = load_recommender()

# Chargement des variables d'environnement
load_dotenv()

# DÉFINITION DES PERMISSIONS SPOTIFY (SCOPE)
# pour créer des playlists publique et privée
SCOPE = "playlist-modify-public playlist-modify-private"

# START APPLICATION
df = load_data()

# Instance globale du client Spotify réutilisée dans toute l'application
sp = get_spotify_client()

# Vérification que toutes les colonnes essentielles sont présentes dans le CSV
# Arrête l'application si des colonnes critiques manquent
required_cols = {'tags_humeur', 'tags_activité', 'track_name', 'artist_name', 'duration_ms', 'track_id', 'genre'}
if not required_cols.issubset(df.columns):
    st.error("Certaines colonnes essentielles sont manquantes dans le fichier CSV.")
    st.stop()

# Charge le fichier css pour le design de l'application
load_custom_css()

# Configuration de la page Streamlit (titre, layout large, sidebar ouverte par défaut)
st.set_page_config(page_title="Spectral", layout="wide", initial_sidebar_state="expanded")

# Interface principale de l'application
st.title("Spectral")
st.markdown("---")

# Suivi du choix précédent
previous_choice = st.session_state.get("previous_choice", None)

# Menu de navigation dans la sidebar pour choisir entre les 3 fonctionnalités
st.sidebar.markdown("## **Menu Musical**")
choice = st.sidebar.radio("Navigation", ["Song-to-Song", "Mood-to-Playlist", "Activity-to-Playlist","Track-by-Audio-Preferences"], label_visibility="collapsed")

# Si changement de vue, mettre à jour
if previous_choice != choice:
    st.session_state['previous_choice'] = choice



# ----- Fonctionnalité playlist selon l'humeur ----- #

if choice == "Mood-to-Playlist":

    # Affiche un titre pour la section humeur
    # Permet à l'utilisateur de choisir un genre musical parmi ceux disponibles dans le dataframe
    # Crée une liste triée des humeurs associées au genre sélectionné, sans doublons ni valeurs manquantes

    st.header("Playlist selon l'humeur choisie")
    selected_genre = st.selectbox("Choisissez un genre musical :", df['genre'].dropna().unique())
    humeurs_list = sorted(df[df['genre'] == selected_genre]['tags_humeur'].dropna().unique())

    if humeurs_list:

        # Humeurs fixes avec couleurs et mapping
        humeurs_dict = {
            "Joyeux":      {"color": "#F9C74F", "tag_humeur": "#joyeux"},
            "Triste":      {"color": "#A9C8E2", "tag_humeur": "#triste"},
            "En colère":   {"color": "#F9844A", "tag_humeur": "#energique"},
            "Dégoûté":     {"color": "#B5E3A1", "tag_humeur": "#calme"},
            "Angoissé":    {"color": "#BDB2FF", "tag_humeur": "#calme"}
        }

        # Boutons bulles
        selected_humeur = st.radio(
            "Comment vous sentez-vous aujourd’hui ?",
            list(humeurs_dict.keys()),
            horizontal=True,
        )

        # Jauge colorée stylisée
        if selected_humeur:
            color = humeurs_dict[selected_humeur]["color"]

            # Messages conditionnels liés aux humeurs
            humeur_messages = {
                "Joyeux": "Gardez cette humeur !",
                "Triste": "Allez-y, lâchez tout !",
                "En colère": "Défoulez-vous !",
                "Dégoûté": "Laissez couler.",
                "Angoissé": "Respirez."
            }

            message = humeur_messages.get(selected_humeur, "")

            st.markdown(f"""
            <div style='background-color:{color}; padding: 1em; text-align: center; border-radius: 12px; font-size: 1.3em; font-weight: bold;'>
                {selected_humeur.upper()} : <i>{message}</i>
            </div>
            """, unsafe_allow_html=True)


            st.markdown("")
 



        if st.button("Générer Playlist"):

            # Affiche une animation de chargement pendant 1.5 secondes
            with st.spinner("Création en cours..."):
                time.sleep(1.5)

            # Filtre les chansons du genre et de l'humeur choisis, mélange aléatoirement et prend les 20 premières
            tag_humeur = humeurs_dict[selected_humeur]["tag_humeur"]
            filtered_df = df[(df['genre'] == selected_genre) & (df['tags_humeur'] == tag_humeur)].sample(frac=1).head(10)

            if filtered_df.empty:
                # Message si aucune chanson ne correspond
                st.warning("Aucune chanson trouvée pour cette humeur.")
                st.session_state.pop('mood_playlist_df', None)
                st.session_state.pop('mood_playlist_title', None)

            # Stocke la playlist filtrée et son titre dans la session
            else:
                st.session_state['mood_playlist_df'] = filtered_df
                st.session_state['mood_playlist_title'] = f"Playlist {selected_humeur} - {selected_genre}"
                st.session_state['playlist_title'] = st.session_state['mood_playlist_title']


    if 'mood_playlist_df' in st.session_state:

        # Calcule la durée totale de la playlist en millisecondes
        filtered_df = st.session_state['mood_playlist_df']
        total_duration_ms = filtered_df['duration_ms'].sum()

        # Affiche un message de succès avec le titre de la playlist
        st.success(f"Playlist générée pour : **{st.session_state['mood_playlist_title']}**")

        # Affiche des indicateurs : nombre de chansons et durée totale formatée
        st.metric("Nombre de titres", len(filtered_df))
        st.metric("Durée totale", format_duration(total_duration_ms))

        # CORRECTION : Affichage en grille des lecteurs Spotify
        num_columns = 2  # Réduit à 2 colonnes pour un meilleur affichage
        tracks_list = list(filtered_df.itertuples())
        
        for i in range(0, len(tracks_list), num_columns):
            cols = st.columns(num_columns)
            for j in range(num_columns):
                if i + j < len(tracks_list):
                    track = tracks_list[i + j]
                    with cols[j]:
                        embed_url = f"https://open.spotify.com/embed/track/{track.track_id}"
                        st.markdown(
                            f"""
                            <iframe style="border-radius:12px" src="{embed_url}" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
                            """,
                            unsafe_allow_html=True 
                        )
    

        if st.button("Créer cette playlist dans mon compte Spotify"):
            try:
                playlist_url = create_spotify_playlist(filtered_df['track_id'].tolist(), st.session_state['playlist_title'])
                st.success("Playlist créée avec succès !")
                st.markdown(f"[Voir la playlist sur Spotify]({playlist_url})")
            except Exception as e:
                st.error(f"Erreur lors de la création de la playlist : {e}")


# ----- Fonctionalité playlist selon activité ----- #
elif choice == "Activity-to-Playlist":
    st.header("Playlist selon l'activité choisie")

    selected_genre = st.selectbox("Choisissez un genre musical :", df['genre'].dropna().unique())

    # Mapping des activités fixes
    activities_dict = {
        "Sport ":       {"color": "#F9C74F", "tag_activité": "#sport/#cardio"},
        "Travail ":     {"color": "#90BE6D", "tag_activité": "#concentration/#travail"},
        "Fête ":        {"color": "#F9844A", "tag_activité": "#dance/#fête"},
        "Détente ":     {"color": "#BDB2FF", "tag_activité": "#meditation/#yoga"},
    }

    selected_activity = st.radio(
        "Quelle est votre activité actuelle ?",
        list(activities_dict.keys()),
        horizontal=True,
    )

    if selected_activity:
        color = activities_dict[selected_activity]["color"]
        st.markdown(f"""
        <div style='background-color:{color}; padding: 1em; text-align: center; border-radius: 12px; font-size: 1.3em; font-weight: bold;'>
            {selected_activity}
        </div>
        """, unsafe_allow_html=True)

    # Slider noir personnalisé uniquement
    html_slider_duree = """
    <div style="margin: 20px 0;">
        <label for="slider_duree" style="font-size: 14px; font-weight: bold; color: #262730;">
            Durée de la playlist (en minutes): <span id="value_duree">60</span>
        </label>
        <input
            id="slider_duree"
            type="range"
            min="20"
            max="180"
            value="60"
            step="5"
            style="width: 100%; height: 8px; accent-color: black; margin-top: 10px;"
            oninput="
                document.getElementById('value_duree').innerText = this.value;
                window.parent.postMessage({feature: 'duree_min', value: parseInt(this.value)}, '*');
            "
        >
    </div>
    <script>
        // Initialiser la valeur dans le session state de Streamlit
        window.parent.postMessage({feature: 'duree_min', value: 60}, '*');
        
        window.addEventListener('message', (event) => {
            if (event.data.feature === 'duree_min') {
                document.getElementById('slider_duree').value = event.data.value;
                document.getElementById('value_duree').innerText = event.data.value;
            }
        });
    </script>
    """

    components.html(html_slider_duree, height=100)

    # Récupération de la valeur du slider personnalisé
    # Utilisation de session_state pour stocker la valeur
    if 'duree_min' not in st.session_state:
        st.session_state.duree_min = 60
    
    duree_min = st.session_state.duree_min
    duree_ms = duree_min * 60 * 1000  # en millisecondes

    if st.button("Générer Playlist"):
        with st.spinner("Création en cours..."):
            time.sleep(1.5)

        tag_activite = activities_dict[selected_activity]["tag_activité"]

        candidats = df[
            (df['genre'] == selected_genre) & 
            (df['tags_activité'] == tag_activite)
        ].sample(frac=1)

        playlist = []
        total = 0

        for _, row in candidats.iterrows():
            if total + row['duration_ms'] > duree_ms:
                break
            playlist.append(row)
            total += row['duration_ms']

        if not playlist:
            st.warning("Aucune chanson trouvée pour cette durée et activité.")
            st.session_state.pop('activity_playlist_df', None)
            st.session_state.pop('activity_playlist_title', None)
        else:
            filtered_df = pd.DataFrame(playlist)
            st.session_state['activity_playlist_df'] = filtered_df
            st.session_state['activity_playlist_title'] = f"Playlist {selected_activity} - {selected_genre}"
            st.session_state['playlist_title'] = st.session_state['activity_playlist_title']

    # Affichage des résultats
    if 'activity_playlist_df' in st.session_state:
        filtered_df = st.session_state['activity_playlist_df']
        total_duration_ms = filtered_df['duration_ms'].sum()

        st.success(f"Playlist générée pour : **{st.session_state['activity_playlist_title']}**")
        st.metric("Nombre de titres", len(filtered_df))
        st.metric("Durée totale", format_duration(total_duration_ms))

        # Grille 2 
        num_columns = 2
        tracks_list = list(filtered_df.itertuples())

        for i in range(0, len(tracks_list), num_columns):
            cols = st.columns(num_columns)
            for j in range(num_columns):
                if i + j < len(tracks_list):
                    track = tracks_list[i + j]
                    with cols[j]:
                        embed_url = f"https://open.spotify.com/embed/track/{track.track_id}"
                        st.markdown(
                            f"""
                            <iframe style="border-radius:12px" src="{embed_url}" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
                            """,
                            unsafe_allow_html=True
                        )

        if st.button("Créer cette playlist dans mon compte Spotify"):
            try:
                playlist_url = create_spotify_playlist(filtered_df['track_id'].tolist(), st.session_state['playlist_title'])
                st.success("Playlist créée avec succès !")
                st.markdown(f"[Voir la playlist sur Spotify]({playlist_url})")
            except Exception as e:
                st.error(f"Erreur lors de la création de la playlist : {e}")

#----- Fonctionnalité chanson pour chanson-----#
elif choice == "Song-to-Song":
    st.header("Découverte musicale : d'une chanson à l'autre")
    
    selected_genre = st.selectbox("Choisissez votre genre de prédilection :", 
                                  df['genre'].dropna().unique())
    
    df_genre = df[df['genre'] == selected_genre].copy()
    
    if df_genre.empty:
        st.warning("Aucune chanson trouvée pour ce genre.")
    else:
        st.write(f"**{len(df_genre)} chansons disponibles dans le genre {selected_genre}**")
        
        audio_features_cols = ['danceability', 'energy', 'valence', 'acousticness', 
                              'instrumentalness', 'speechiness', 'liveness']
        available_audio_cols = [col for col in audio_features_cols if col in df_genre.columns]
        
        if not available_audio_cols:
            st.info("Les caractéristiques audio ne sont pas disponibles dans le dataset. La sélection sera basée sur d'autres critères.")
        
        if st.button("Découvrir 5 chansons variées"):
            with st.spinner("Sélection de chansons variées..."):
                diverse_tracks = select_diverse_tracks(df_genre, 5)
                st.session_state['diverse_tracks'] = diverse_tracks
        
        if 'diverse_tracks' in st.session_state:
            st.subheader("Choisissez une chanson parmi ces 5 options variées :")
            
            cols = st.columns(5)
            
            for idx, (_, track) in enumerate(st.session_state['diverse_tracks'].iterrows()):
                with cols[idx]:
                    image_url = get_album_image_url_cached(track['track_id'])
                    if image_url:
                        st.image(image_url, width=120)
                    
                    st.write(f"**{track['track_name'][:20]}{'...' if len(track['track_name']) > 20 else ''}**")
                    st.write(f"*{track['artist_name'][:15]}{'...' if len(track['artist_name']) > 15 else ''}*")
                    
                    if st.button(f"Choisir", key=f"select_{track['track_id']}"):
                        st.session_state['selected_track'] = track
                        st.rerun()

            if 'selected_track' in st.session_state:
                selected_track = st.session_state['selected_track']
                
                st.markdown("---")
                st.subheader("Chanson sélectionnée :")
                

                # CORRECTION : Lecteur Spotify intégré
                embed_url = f"https://open.spotify.com/embed/track/{selected_track['track_id']}"
                st.markdown(
                    f"""
                    <iframe style="border-radius:12px" src="{embed_url}" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
                    """,
                    unsafe_allow_html=True 
                    )

                if st.button("Trouver une chanson similaire"):
                    with st.spinner("Recherche d'une chanson similaire..."):
                        similar_track = find_similar_track(selected_track, df_genre, available_audio_cols)
                        if similar_track is not None:
                            st.session_state['similar_track'] = similar_track
                            st.rerun()
                        else:
                            st.error("Aucune chanson similaire trouvée.")
                
                if 'similar_track' in st.session_state:
                    similar_track = st.session_state['similar_track']
                    
                    st.markdown("---")
                    st.subheader("Chanson recommandée :")
                    
               
                    
                    # CORRECTION : Lecteur Spotify pour la chanson recommandée
                    embed_url = f"https://open.spotify.com/embed/track/{similar_track['track_id']}"
                    st.markdown(
                        f"""
                        <iframe style="border-radius:12px" src="{embed_url}" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
                        """,
                        unsafe_allow_html=True 
                    )

                    if available_audio_cols:
                        st.markdown("---")
                        st.subheader("Comparaison des caractéristiques audio")
                        
                        comparison_chart = create_comparison_chart(
                            selected_track, similar_track, available_audio_cols
                        )
                        
                        if comparison_chart:
                            st.plotly_chart(comparison_chart, use_container_width=True)
                            
                            comparison_data = {
                                'Caractéristique': available_audio_cols,
                                'Chanson sélectionnée': [round(selected_track.get(col, 0), 3) for col in available_audio_cols],
                                'Chanson recommandée': [round(similar_track.get(col, 0), 3) for col in available_audio_cols]
                            }
                            
                            comparison_df = pd.DataFrame(comparison_data)
                            st.dataframe(comparison_df, use_container_width=True)
        
        if st.button("Recommencer la découverte"):
            for key in ['diverse_tracks', 'selected_track', 'similar_track']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# ----- Fonctionalité BONUS ------ #

elif choice == "Track-by-Audio-Preferences":
    st.header("Trouve une chanson selon tes préférences audio")

    st.markdown("**Ajuste les curseurs selon ce que tu recherches dans une chanson** ")

    features = ['danceability', 'energy', 'valence', 'acousticness', 
            'instrumentalness', 'speechiness', 'liveness']

    user_preferences = {}

    for feature in features:
        # Génère un slider HTML avec accent-color
        html_slider = f"""
        <label for="slider_{feature}">{feature.capitalize()}: <span id="value_{feature}">0.50</span></label>
        <input
            id="slider_{feature}"
            type="range"
            min="0"
            max="100"
            value="50"
            step="5"
            style="width: 100%; accent-color: black;"
            oninput="
                document.getElementById('value_{feature}').innerText = (this.value / 100).toFixed(2);
                window.parent.postMessage({{feature: '{feature}', value: this.value / 100}}, '*');
            "
        >
        <script>
            window.addEventListener('message', (event) => {{
                if (event.data.feature === '{feature}') {{
                    document.getElementById('slider_{feature}').value = event.data.value * 100;
                    document.getElementById('value_{feature}').innerText = event.data.value.toFixed(2);
                }}
            }});
        </script>
        <hr/>
        """
        # Insert HTML
        components.html(html_slider, height=80)

    if st.button("Trouver une chanson qui correspond"):
        with st.spinner("Analyse en cours..."):
            time.sleep(1.5)

        # Calcul de la distance euclidienne
        df_filtered = df.dropna(subset=features)
        distances = ((df_filtered[features] - pd.Series(user_preferences)) ** 2).sum(axis=1)
        closest_index = distances.idxmin()
        closest_track = df_filtered.loc[closest_index]

        st.success("Voici la chanson qui correspond le plus à tes préférences :")

        st.write(f"**{closest_track['track_name']}** — *{closest_track['artist_name']}*")

        embed_url = f"https://open.spotify.com/embed/track/{closest_track['track_id']}"
        st.markdown(
            f"""
            <iframe style="border-radius:12px" src="{embed_url}" width="100%" height="152" frameBorder="0" allowfullscreen=""
            allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
            """,
            unsafe_allow_html=True,
        )




st.markdown("---")
st.markdown('<div class="footer-style"><p>Créé par Pauline, Gaelle, Bertrand et Hassan</p></div>', unsafe_allow_html=True)