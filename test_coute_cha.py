import streamlit as st
import pandas as pd
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
# =================== IMPORTS POUR LE MACHINE LEARNING =================== #
import pickle  # Module pour charger le modèle sérialisé depuis le fichier .pkl
from sklearn.metrics import pairwise_distances  # Calcul de distances euclidiennes entre vecteurs





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

# =================== FONCTION AMÉLIORÉE AVEC ML =================== #
def find_similar_track(selected_track, df_genre, audio_features_cols):
    """
    Fonction améliorée pour trouver une chanson similaire en utilisant le modèle ML
    Maintient la même signature pour compatibilité avec le code existant
    
    Args:
        selected_track (pandas.Series): Chanson de référence sélectionnée par l'utilisateur
        df_genre (pandas.DataFrame): DataFrame filtré par genre (pour compatibilité)
        audio_features_cols (list): Liste des colonnes audio (pour compatibilité)
    
    Returns:
        pandas.Series ou None: Chanson similaire trouvée ou None si échec
    """
    # Vérification de la disponibilité du recommandateur ML
    if ml_recommender is not None:
        try:
            # Utilisation du modèle ML pour trouver la chanson la plus similaire
            # method='cluster_cosine' privilégie les chansons du même cluster musical
            similar_track = ml_recommender.find_similar_track_ml(
                selected_track, 
                n_recommendations=1,  # Une seule recommandation pour compatibilité
                method='cluster_cosine'  # Méthode optimale pour Song-to-Song
            )
            
            # Si le ML trouve une recommandation, la retourner
            if similar_track is not None:
                return similar_track
                
        except Exception as e:
            # En cas d'erreur ML, affichage d'un warning et utilisation de la méthode de fallback
            st.warning(f"Erreur ML, utilisation méthode standard : {e}")
    
    # =================== MÉTHODE DE FALLBACK (CODE ORIGINAL) =================== #
    # Si le ML n'est pas disponible ou échoue, utilisation de l'ancienne logique
    
    # Vérification de la disponibilité des features audio
    if not audio_features_cols:
        # Si pas de features audio, sélection aléatoire parmi les autres chansons du genre
        other_tracks = df_genre[df_genre['track_id'] != selected_track['track_id']]
        return other_tracks.sample(n=1).iloc[0] if not other_tracks.empty else None

    # Exclusion de la chanson sélectionnée des candidats
    other_tracks = df_genre[df_genre['track_id'] != selected_track['track_id']]
    if other_tracks.empty:
        return None

    # Calcul de similarité cosine avec les features audio standard
    # fillna(0) remplace les valeurs manquantes par 0
    # reshape(1, -1) crée une matrice 2D pour sklearn
    selected_features = selected_track[audio_features_cols].fillna(0).values.reshape(1, -1)
    other_features = other_tracks[audio_features_cols].fillna(0).values

    # Calcul de la similarité cosine entre la chanson sélectionnée et les autres
    similarities = cosine_similarity(selected_features, other_features)[0]
    
    # Recherche de l'index avec la similarité maximale
    most_similar_idx = np.argmax(similarities)
    
    # Retour de la chanson la plus similaire
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

# =================== FONCTION D'AFFICHAGE ENRICHI AVEC INFO ML =================== #
def display_track_with_ml_info(track, title="Informations de la chanson"):
    """
    Affiche les informations d'une chanson avec les données du modèle ML
    Enrichit l'affichage existant sans modifier l'interface principale
    
    Args:
        track (pandas.Series): Données de la chanson à afficher
        title (str): Titre de la section d'affichage
    """
    # Affichage du titre de la section
    st.subheader(title)
    
    # Colonnes pour organiser l'affichage
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Informations principales de la chanson
        st.write(f"🎵 **Titre:** {track['track_name']}")
        st.write(f"👤 **Artiste:** {track['artist_name']}")
        
        # Affichage du genre si disponible
        if 'genre' in track and pd.notna(track['genre']):
            st.write(f"🎼 **Genre:** {track['genre']}")
            
        # Affichage de l'année si disponible
        if 'release_date' in track and pd.notna(track['release_date']):
            st.write(f"📅 **Année:** {track['release_date']}")
    
    with col2:
        # Informations du modèle ML si disponibles
        if 'cluster_ml' in track and pd.notna(track['cluster_ml']):
            # Métrique Streamlit pour afficher le cluster de façon visuelle
            st.metric("🤖 Groupe Musical IA", f"Cluster {int(track['cluster_ml'])}")
            
        # Affichage de la popularité si disponible
        if 'popularity' in track and pd.notna(track['popularity']):
            st.metric("📊 Popularité", f"{track['popularity']}/100")




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

# =================== CLASSE POUR RECOMMANDATIONS ML =================== #
class MoodifyRecommender:
    """
    Classe responsable de charger et utiliser le modèle ML pour générer des recommandations
    Cette classe encapsule toute la logique ML sans impacter l'interface existante
    """
    
    def __init__(self, model_path, data_path):
        """
        Constructeur de la classe - initialise le recommandateur ML
        
        Args:
            model_path (str): Chemin absolu vers le fichier .pkl contenant le modèle entraîné
            data_path (str): Chemin absolu vers le fichier CSV avec les données complètes
        """
        # Stockage des chemins des fichiers (attributs de classe)
        self.model_path = model_path
        self.data_path = data_path
        
        # Initialisation des attributs qui contiendront les données chargées
        self.model_data = None      # Dictionnaire contenant le modèle et ses métadonnées
        self.df = None              # DataFrame pandas avec toutes les chansons
        self.features = None        # Liste des caractéristiques utilisées par le modèle
        self.pipeline = None        # Pipeline sklearn (preprocessing + modèle)
        self.df_processed = None    # DataFrame enrichi avec les prédictions du modèle
        
        # Chargement automatique lors de l'instantiation
        self._load_model()    # Méthode privée pour charger le modèle
        self._load_data()     # Méthode privée pour charger les données
        self._prepare_data()  # Méthode privée pour appliquer le modèle aux données
    
    def _load_model(self):
        """
        Méthode privée pour charger le modèle depuis le fichier pickle
        Le fichier doit contenir un dictionnaire avec les clés 'features' et 'pipeline'
        """
        try:
            # Ouverture du fichier pickle en mode lecture binaire
            with open(self.model_path, 'rb') as f:
                # pickle.load() désérialise l'objet Python stocké dans le fichier
                self.model_data = pickle.load(f)
            
            # Extraction des composants du modèle depuis le dictionnaire
            # get() avec valeur par défaut évite les erreurs si la clé n'existe pas
            self.features = self.model_data.get('features', [])
            self.pipeline = self.model_data.get('pipeline', None)
            
        except FileNotFoundError:
            # Gestion d'erreur si le fichier n'existe pas au chemin spécifié
            raise FileNotFoundError(f"Modèle non trouvé : {self.model_path}")
        except Exception as e:
            # Gestion d'erreur générale pour autres problèmes (corruption, format, etc.)
            raise Exception(f"Erreur chargement modèle : {e}")
    
    def _load_data(self):
        """
        Méthode privée pour charger les données depuis le fichier CSV
        """
        try:
            # pd.read_csv() lit le fichier CSV et crée un DataFrame pandas
            self.df = pd.read_csv(self.data_path)
        except FileNotFoundError:
            # Gestion d'erreur si le fichier CSV n'existe pas
            raise FileNotFoundError(f"Données non trouvées : {self.data_path}")
        except Exception as e:
            # Gestion d'erreurs pour problèmes de lecture (encodage, format, etc.)
            raise Exception(f"Erreur chargement données : {e}")
    
    def _prepare_data(self):
        """
        Méthode privée qui applique le pipeline ML aux données pour générer les clusters
        Ajoute une colonne 'cluster_ml' au DataFrame avec les prédictions
        """
        try:
            # Vérification que le pipeline et les features sont disponibles
            if self.pipeline is not None and self.features:
                
                # Vérification de la présence des features dans les données
                # List comprehension pour identifier les features manquantes
                missing_features = [f for f in self.features if f not in self.df.columns]
                
                # Sélection des features disponibles dans le dataset
                available_features = [f for f in self.features if f in self.df.columns]
                
                if available_features:
                    # Sélection des colonnes et gestion des valeurs manquantes
                    # fillna(0) remplace les NaN par 0 pour éviter les erreurs du modèle
                    X = self.df[available_features].fillna(0)
                    
                    # Application du pipeline : preprocessing + prédiction des clusters
                    # predict() retourne un array numpy avec les labels de clusters
                    clusters = self.pipeline.predict(X)
                    
                    # Création d'une copie du DataFrame original
                    self.df_processed = self.df.copy()
                    # Ajout de la colonne des clusters prédits
                    self.df_processed['cluster_ml'] = clusters
                    
                else:
                    # Si aucune feature disponible, utilisation des données sans ML
                    self.df_processed = self.df.copy()
            else:
                # Si pipeline non disponible, utilisation des données brutes
                self.df_processed = self.df.copy()
                
        except Exception as e:
            # En cas d'erreur, utilisation des données sans traitement ML
            print(f"Erreur préparation données ML : {e}")
            self.df_processed = self.df.copy()
    
    def find_similar_track_ml(self, selected_track, n_recommendations=1, method='cluster_cosine'):
        """
        Méthode publique pour trouver des chansons similaires avec le modèle ML
        Remplace la logique existante de find_similar_track avec de meilleures recommandations
        
        Args:
            selected_track (pandas.Series): Chanson de référence sélectionnée
            n_recommendations (int): Nombre de recommandations (par défaut 1 pour compatibilité)
            method (str): Méthode de calcul de similarité
        
        Returns:
            pandas.Series ou None: Chanson similaire trouvée ou None si aucune
        """
        # Vérification que la chanson de référence a un track_id
        if 'track_id' not in selected_track or pd.isna(selected_track['track_id']):
            return None
        
        # Exclusion de la chanson sélectionnée des candidats
        # Condition != pour éviter de recommander la même chanson
        candidates = self.df_processed[
            self.df_processed['track_id'] != selected_track['track_id']
        ]
        
        # Si aucun candidat disponible, retour None
        if candidates.empty:
            return None
        
        # Définition des caractéristiques audio pour calculer la similarité
        audio_features = [
            'danceability',      # Mesure de la dansabilité (0.0 à 1.0)
            'energy',            # Énergie perçue (0.0 à 1.0)
            'valence',           # Positivité musicale (0.0 à 1.0)
            'acousticness',      # Caractère acoustique (0.0 à 1.0)
            'instrumentalness',  # Absence de voix (0.0 à 1.0)
            'liveness',          # Présence d'audience (0.0 à 1.0)
            'speechiness',       # Présence de paroles (0.0 à 1.0)
            'tempo'              # Tempo en BPM (normalisé entre 0 et 1)
        ]
        
        # Sélection des features disponibles dans les données
        available_features = [f for f in audio_features if f in self.df_processed.columns]
        
        # Si aucune feature audio disponible, sélection aléatoire
        if not available_features:
            return candidates.sample(n=1).iloc[0]
        
        # Stratégie de filtrage selon la méthode choisie
        if method.startswith('cluster_') and 'cluster_ml' in self.df_processed.columns:
            # Recherche dans le même cluster ML pour plus de cohérence
            same_cluster_candidates = candidates[
                candidates['cluster_ml'] == selected_track.get('cluster_ml')
            ]
            # Utilisation du même cluster si disponible, sinon tous les candidats
            final_candidates = same_cluster_candidates if not same_cluster_candidates.empty else candidates
        else:
            # Méthode globale : recherche dans tout le dataset
            final_candidates = candidates
        
        # Préparation des vecteurs de caractéristiques pour le calcul de similarité
        # reshape(1, -1) transforme en matrice 2D requise par sklearn
        ref_features = selected_track[available_features].fillna(0).values.reshape(1, -1)
        # Matrice des features de tous les candidats
        candidates_features = final_candidates[available_features].fillna(0).values
        
        # Calcul de similarité selon la méthode spécifiée
        if 'euclidean' in method:
            # Distance euclidienne : plus la distance est petite, plus c'est similaire
            distances = pairwise_distances(ref_features, candidates_features, metric='euclidean')[0]
            # Conversion en score de similarité (inverse de la distance normalisée)
            similarities = 1 / (1 + distances)
        else:
            # Méthode par défaut : similarité cosine (mesure l'angle entre vecteurs)
            similarities = cosine_similarity(ref_features, candidates_features)[0]
        
        # Recherche de l'index avec la plus haute similarité
        # argmax() retourne l'index de la valeur maximale
        most_similar_idx = np.argmax(similarities)
        
        # Retour de la chanson la plus similaire
        return final_candidates.iloc[most_similar_idx]



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











# Chargement des variables d'environnement
load_dotenv()

# DÉFINITION DES PERMISSIONS SPOTIFY (SCOPE)
# pour créer des playlists publique et privée
SCOPE = "playlist-modify-public playlist-modify-private"

# START APPLICATION
df = load_data()

# Instance globale du client Spotify réutilisée dans toute l'application
sp = get_spotify_client()

# =================== INITIALISATION DU MODÈLE ML =================== #
# Configuration des chemins vers vos fichiers (à adapter selon votre environnement)
MODEL_PATH = '/Users/beber/Documents/Cours/Wild_Code_School/Semaine_8_Visualisation_interactive_&_Pandas_approfondi/Projet_2/Projet_2_local/Datasets/modeles_deploiement/best_model.pkl'
DATA_PATH = '/Users/beber/Documents/Cours/Wild_Code_School/Semaine_8_Visualisation_interactive_&_Pandas_approfondi/Projet_2/Projet_2_local/Notebooks/df_concat_tagged.csv'

# Initialisation du recommandateur ML avec mise en cache pour optimiser les performances
# @st.cache_resource évite de recharger le modèle à chaque interaction utilisateur
@st.cache_resource
def get_ml_recommender():
    """
    Fonction cachée pour initialiser le recommandateur ML une seule fois par session
    Le décorateur @st.cache_resource maintient l'objet en mémoire entre les interactions
    """
    try:
        # Création de l'instance du recommandateur avec chargement automatique
        return MoodifyRecommender(MODEL_PATH, DATA_PATH)
    except Exception as e:
        # En cas d'erreur, affichage dans Streamlit et retour None
        st.error(f"Erreur initialisation ML : {e}")
        return None

# Initialisation du recommandateur ML global pour l'application
ml_recommender = get_ml_recommender()


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
            "Joie":      {"color": "#FFE28A", "tag_humeur": "#triste"},
            "Tristesse": {"color": "#A9C8E2", "tag_humeur": "#calme"},
            "Colère":    {"color": "#F59B9B", "tag_humeur": "#energique"},
            "Dégoût":    {"color": "#B5E3A1", "tag_humeur": "#joyeux"},
            "Angoisse":  {"color": "#CBA9E5", "tag_humeur": "#calme"}
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
            st.markdown(f"""
            <div style='background-color:{color}; padding: 1em; text-align: center; border-radius: 12px; font-size: 1.3em; font-weight: bold;'>
                {selected_humeur}
            </div>
            """, unsafe_allow_html=True)


        st.markdown(f"<div class='mood-display'>{selected_humeur}</div>", unsafe_allow_html=True)

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


elif choice == "Activity-to-Playlist":
    st.header("Playlist selon l'activité choisie")

    selected_genre = st.selectbox("Choisissez un genre musical :", df['genre'].dropna().unique())

    # Mapping des activités fixes
    activities_dict = {
        "Sport ":      {"color": "#F9C74F", "tag_activité": "#sport/#cardio"},
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

    # Choix de la durée souhaitée
    duree_min = st.slider("Durée de la playlist (en minutes)", min_value=10, max_value=120, step=5)
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

        # Grille 2 colonnes comme pour humeur
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

                # Lecteur Spotify intégré
                embed_url = f"https://open.spotify.com/embed/track/{selected_track['track_id']}"
                st.markdown(
                    f"""
                    <iframe style="border-radius:12px" src="{embed_url}" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
                    """,
                    unsafe_allow_html=True 
                    )

                # Trouver une chanson similaire
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

   
                    # Lecteur intégré Spotify pour la chanson recommandée
                    embed_url = f"https://open.spotify.com/embed/track/{similar_track['track_id']}"
                    st.markdown(
                        f"""
                        <iframe style="border-radius:12px" src="{embed_url}" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
                        """,
                        unsafe_allow_html=True 
                    )
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

# ----- Fonctionalité BONUS ------ #

elif choice == "Track-by-Audio-Preferences":
    st.header("Trouve une chanson selon tes préférences audio")

    st.markdown("**Ajuste les curseurs selon ce que tu recherches dans une chanson** ")

    features = ['danceability', 'energy', 'valence', 'acousticness', 
                'instrumentalness', 'speechiness', 'liveness']

    user_preferences = {}
    for feature in features:
        user_preferences[feature] = st.slider(
            label=feature.capitalize(),
            min_value=0.0,
            max_value=1.0,
            step=0.05,
            value=0.5,
        )

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

        st.subheader("Comparaison des caractéristiques audio ")

        # Préparer les données pour le radar
        fig = go.Figure()

        # Tracé des préférences utilisateur
        fig.add_trace(go.Scatterpolar(
            r=[user_preferences[feat] for feat in features],
            theta=[feat.capitalize() for feat in features],
            fill='toself',
            name='Préférences utilisateur',
            line_color='deepskyblue'
        ))

        # Tracé du morceau sélectionné
        fig.add_trace(go.Scatterpolar(
            r=[closest_track[feat] for feat in features],
            theta=[feat.capitalize() for feat in features],
            fill='toself',
            name='Chanson proposée',
            line_color='gold'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1])
            ),
            showlegend=True,
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        # Affichage des valeurs détaillées (facultatif)
        with st.expander("Détails numériques "):
            for feature in features  :
                st.metric(
                    label=feature.capitalize(),
                    value=f"{closest_track[feature]:.2f}",
                    delta=f"{closest_track[feature] - user_preferences[feature]:+.2f}"
                )


st.markdown("---")
st.markdown('<div class="footer-style"><p>Créé par Pauline, Gaelle, Bertrand et Hassan</p></div>', unsafe_allow_html=True)