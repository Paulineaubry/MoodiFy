# =============================================================================
# APPLICATION STREAMLIT - CLUSTERING MUSICAL SPOTIFY
# Script de déploiement pour les recommandations musicales
# =============================================================================

import streamlit as st  # Framework pour applications web interactives
import pandas as pd     # Manipulation de données tabulaires
import numpy as np      # Calculs numériques
import pickle          # Sérialisation/désérialisation d'objets Python
import plotly.express as px  # Visualisations interactives
import plotly.graph_objects as go  # Graphiques Plotly avancés
from sklearn.preprocessing import StandardScaler  # Normalisation des données

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Moodify - Clustering Musical",  # Titre de l'onglet navigateur
    page_icon="🎵",                              # Icône de l'onglet
    layout="wide",                               # Layout large pour plus d'espace
    initial_sidebar_state="expanded"             # Sidebar ouverte par défaut
)

# Cache des modèles pour optimiser les performances
@st.cache_resource  # Décorateur pour mettre en cache les ressources
def charger_modeles():
    """
    Charge les modèles pré-entraînés depuis les fichiers pickle.
    
    Returns:
        tuple: (modele_clustering, scaler, config_metadata)
    """
    try:
        # Chargement du modèle de clustering entraîné
        with open('modeles_deploiement/meilleur_modele.pkl', 'rb') as f:
            modele = pickle.load(f)
        
        # Chargement du scaler pour la normalisation
        with open('modeles_deploiement/scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        
        # Chargement des métadonnées de configuration
        with open('modeles_deploiement/config_metadata.pkl', 'rb') as f:
            config = pickle.load(f)
        
        return modele, scaler, config
    
    except FileNotFoundError as e:
        st.error(f"❌ Fichiers modèle non trouvés: {e}")
        st.stop()  # Arrête l'exécution de l'application
    except Exception as e:
        st.error(f"❌ Erreur chargement modèles: {e}")
        st.stop()

@st.cache_data  # Cache pour les données
def charger_donnees_spotify():
    """
    Charge les données Spotify pour l'application.
    
    Returns:
        pd.DataFrame: DataFrame des données musicales
    """
    try:
        # Tentative de chargement du fichier de données
        df = pd.read_csv('Datasets/df_concat_tagged.csv')
        return df
    except FileNotFoundError:
        st.error("❌ Fichier de données non trouvé")
        return None

def predire_cluster(features_dict, modele, scaler, features_list):
    """
    Prédit le cluster pour une nouvelle chanson.
    
    Args:
        features_dict (dict): Dictionnaire des caractéristiques audio
        modele: Modèle de clustering entraîné
        scaler: Scaler pour la normalisation
        features_list (list): Liste des features utilisées
        
    Returns:
        int: Numéro du cluster prédit
    """
    # Création d'un DataFrame avec les features dans le bon ordre
    df_features = pd.DataFrame([features_dict])[features_list]
    
    # Normalisation des features avec le scaler entraîné
    features_scaled = scaler.transform(df_features)
    
    # Prédiction du cluster
    cluster = modele.predict(features_scaled)[0]
    
    return cluster

def afficher_caracteristiques_cluster(df_spotify, cluster_id, features_list):
    """
    Affiche les caractéristiques moyennes d'un cluster.
    
    Args:
        df_spotify (pd.DataFrame): Données Spotify complètes
        cluster_id (int): ID du cluster à analyser
        features_list (list): Liste des features
    """
    # Filtrage des données du cluster
    cluster_data = df_spotify[df_spotify['cluster'] == cluster_id]
    
    if len(cluster_data) > 0:
        # Calcul des statistiques du cluster
        stats = cluster_data[features_list].describe()
        
        # Affichage des caractéristiques moyennes
        st.subheader(f"📊 Caractéristiques du Cluster {cluster_id}")
        
        # Création de colonnes pour l'affichage
        cols = st.columns(len(features_list))
        
        for i, feature in enumerate(features_list):
            with cols[i]:
                # Valeur moyenne de la feature pour ce cluster
                moyenne = stats.loc['mean', feature]
                st.metric(
                    label=feature.capitalize(),
                    value=f"{moyenne:.3f}"
                )

def main():
    """
    Fonction principale de l'application Streamlit.
    """
    # Titre principal de l'application
    st.title("🎵 Moodify - Clustering Musical Spotify")
    st.markdown("*Découvrez à quel style musical appartient votre chanson*")
    
    # Chargement des modèles et données
    modele, scaler, config = charger_modeles()
    df_spotify = charger_donnees_spotify()
    
    if df_spotify is None:
        return
    
    # Affichage des informations sur le modèle utilisé
    with st.sidebar:
        st.header("ℹ️ Informations du Modèle")
        st.write(f"**Algorithme :** {config['modele_type']}")
        st.write(f"**Features :** {len(config['features_list'])}")
        st.write(f"**Normalisation :** {config['scaler_type']}")
        st.write(f"**Score Composite :** {config['scores']['score_composite']:.4f}")
        
        # Métriques de performance
        st.subheader("📈 Performances")
        st.metric("Silhouette Score", f"{config['scores']['silhouette']:.4f}")
        st.metric("Davies-Bouldin", f"{config['scores']['davies_bouldin']:.4f}")
        st.metric("Calinski-Harabasz", f"{config['scores']['calinski_harabasz']:.0f}")
    
    # Interface principale
    st.header("🎼 Analysez votre chanson")
    
    # Création de colonnes pour l'interface utilisateur
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🎛️ Caractéristiques Audio")
        
        # Création de sliders pour chaque feature
        features_input = {}
        
        # Définition des ranges pour chaque feature
        feature_ranges = {
            'valence': (0.0, 1.0, 0.5),      # (min, max, default)
            'energy': (0.0, 1.0, 0.5),
            'danceability': (0.0, 1.0, 0.5),
            'acousticness': (0.0, 1.0, 0.5),
            'tempo': (50, 200, 120),
            'loudness': (-30, 0, -10),
            'instrumentalness': (0.0, 1.0, 0.1)
        }
        
        # Création des contrôles pour chaque feature utilisée
        for feature in config['features_list']:
            if feature in feature_ranges:
                min_val, max_val, default_val = feature_ranges[feature]
                
                # Slider pour la feature
                features_input[feature] = st.slider(
                    label=f"{feature.capitalize()}",
                    min_value=min_val,
                    max_value=max_val,
                    value=default_val,
                    step=0.01 if feature != 'tempo' else 1,
                    help=f"Valeur {feature} de la chanson"
                )
    
    with col2:
        st.subheader("🔮 Prédiction")
        
        # Bouton de prédiction
        if st.button("🎯 Prédire le Cluster", type="primary"):
            # Prédiction du cluster
            cluster_predit = predire_cluster(
                features_input, modele, scaler, config['features_list']
            )
            
            # Affichage du résultat
            st.success(f"🎵 Cette chanson appartient au **Cluster {cluster_predit}**")
            
            # Affichage des caractéristiques du cluster
            if 'cluster' in df_spotify.columns:
                afficher_caracteristiques_cluster(
                    df_spotify, cluster_predit, config['features_list']
                )
            
            # Suggestions de chansons similaires
            if 'cluster' in df_spotify.columns:
                chansons_similaires = df_spotify[
                    df_spotify['cluster'] == cluster_predit
                ].head(5)
                
                if len(chansons_similaires) > 0:
                    st.subheader("🎵 Chansons Similaires")
                    for _, chanson in chansons_similaires.iterrows():
                        # Colonnes disponibles peuvent varier
                        if 'track_name' in chanson and 'artist_name' in chanson:
                            st.write(f"• **{chanson['track_name']}** - {chanson['artist_name']}")
    
    # Section visualisations
    st.header("📊 Visualisations")
    
    # Graphique radar des features
    if len(features_input) > 0:
        st.subheader("🕸️ Profil Audio")
        
        # Préparation des données pour le graphique radar
        categories = list(features_input.keys())
        values = list(features_input.values())
        
        # Normalisation des valeurs pour le radar (0-1)
        values_norm = []
        for i, (cat, val) in enumerate(zip(categories, values)):
            if cat in feature_ranges:
                min_val, max_val, _ = feature_ranges[cat]
                val_norm = (val - min_val) / (max_val - min_val)
                values_norm.append(val_norm)
        
        # Création du graphique radar avec Plotly
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values_norm,
            theta=categories,
            fill='toself',
            name='Profil Audio'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            title="Profil Audio de la Chanson"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Section statistiques globales
    with st.expander("📈 Statistiques Globales"):
        if df_spotify is not None:
            st.write(f"**Nombre total de chansons :** {len(df_spotify):,}")
            
            # Distribution des features
            if len(config['features_list']) > 0:
                feature_stats = df_spotify[config['features_list']].describe()
                st.dataframe(feature_stats)

# Point d'entrée de l'application
if __name__ == "__main__":
    main()