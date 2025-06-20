import streamlit as st
import pandas as pd
import numpy as np
import time

# Configuration de la page
st.set_page_config(
    page_title="Ecoute Cha 🐈!!!",
    layout="wide",
    initial_sidebar_state="collapsed" # Masque la barre latérale par défaut
)

# CSS amélioré mais compatible Streamlit
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    .stApp {
        background: linear-gradient(45deg, #667eea, #764ba2, #f093fb, #f5576c, #4facfe, #00f2fe);
        background-size: 400% 400%;
        animation: gradientShift 8s ease infinite;
        color: white;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .main-header {
        text-align: center;
        font-family: 'Poppins', sans-serif;
        font-size: 4rem;
        font-weight: 700;
        color: #ffffff;
        text-shadow: 0 0 20px rgba(255,255,255,0.5);
        margin-bottom: 0.5rem;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .subtitle {
        text-align: center;
        font-family: 'Poppins', sans-serif;
        font-size: 1.2rem;
        color: #e8f4fd;
        margin-bottom: 2rem;
        text-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }

    .stSelectbox label, .stTextInput label {
        font-family: 'Poppins', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff !important;
    }

    .stButton > button {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.75rem 2rem !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        font-family: 'Poppins', sans-serif !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3) !important;
    }

    .recommendation-box {
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #4ecdc4;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    .song-list {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #ff6b6b;
        font-family: 'Poppins', sans-serif;
        font-size: 1rem;
    }

    /* Styles pour cacher la barre latérale */
    div[data-testid="stSidebarContent"] {
        display: none !important;
    }
    div[data-testid="stSidebar"] {
        display: none !important;
    }
    /* Ceci est parfois nécessaire pour les versions plus récentes de Streamlit */
    .st-emotion-cache-1mpu1lq {
        display: none !important;
    }

    .stRadio label {
        font-family: 'Poppins', sans-serif;
        font-size: 1.1rem;
        color: white !important;
        font-weight: 500;
    }

    .section-header {
        font-family: 'Poppins', sans-serif;
        font-size: 2rem;
        font-weight: 600;
        color: #ffffff;
        text-align: center;
        margin: 1rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }

    .footer-style {
        text-align: center;
        color: rgba(255,255,255,0.8);
        font-family: 'Poppins', sans-serif;
        margin-top: 3rem;
        padding: 1rem;
        background: rgba(0,0,0,0.2);
        border-radius: 10px;
    }

    /* Styles pour l'égaliseur */
    .equalizer-container {
        display: flex;
        justify-content: center;
        align-items: flex-end; /* Align bars to the bottom */
        height: 100px; /* Height of the equalizer */
        gap: 4px; /* Space between bars */
        margin-top: 2rem;
        margin-bottom: 2rem;
    }

    .equalizer-bar {
        width: 8px; /* Width of each bar */
        background: linear-gradient(to top, #4ecdc4, #ff6b6b); /* Gradient color for bars */
        border-radius: 2px;
        transform-origin: bottom; /* Animation starts from the bottom */
        animation: bar-animation 1.2s ease-in-out infinite alternate; /* Animation properties */
    }

    /* Define animation for bars */
    @keyframes bar-animation {
        0% { height: 20%; }
        25% { height: 80%; }
        50% { height: 40%; }
        75% { height: 90%; }
        100% { height: 20%; }
    }

    /* Individual animation delays for varied movement */
    .equalizer-bar:nth-child(1) { animation-delay: 0s; }
    .equalizer-bar:nth-child(2) { animation-delay: 0.2s; }
    .equalizer-bar:nth-child(3) { animation-delay: 0.4s; }
    .equalizer-bar:nth-child(4) { animation-delay: 0.6s; }
    .equalizer-bar:nth-child(5) { animation-delay: 0.8s; }
    .equalizer-bar:nth-child(6) { animation-delay: 1s; }
    .equalizer-bar:nth-child(7) { animation-delay: 0.3s; }
    .equalizer-bar:nth-child(8) { animation-delay: 0.7s; }
    .equalizer-bar:nth-child(9) { animation-delay: 0.1s; }
    .equalizer-bar:nth-child(10) { animation-delay: 0.5s; }


    /* --- Styles pour les onglets --- */

    /* Conteneur des onglets */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem; /* Espace entre les onglets */
        justify-content: center; /* Centrer les onglets */
        margin-bottom: 2rem; /* Espace sous les onglets */
    }

    /* Style des onglets individuels (non sélectionnés) */
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.1); /* Fond semi-transparent */
        border-radius: 10px; /* Bords arrondis */
        padding: 0.75rem 1.5rem; /* Espacement interne */
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.7); /* Couleur du texte */
        transition: all 0.3s ease; /* Transition douce */
        border: none; /* Pas de bordure par défaut */
        box-shadow: 0 2px 8px rgba(0,0,0,0.2); /* Ombre légère */
    }

    /* Style des onglets individuels au survol */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255, 255, 255, 0.2);
        color: #ffffff; /* Texte plus blanc */
        transform: translateY(-2px); /* Léger mouvement vers le haut */
        box-shadow: 0 4px 12px rgba(0,0,0,0.3); /* Ombre plus prononcée */
    }

    /* Style de l'onglet sélectionné */
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4); /* Dégradé de vos couleurs principales */
        color: #ffffff; /* Texte blanc */
        border-bottom: 3px solid transparent; /* Pas de bordure inférieure Streamlit par défaut */
        transform: none; /* Annule le transform: translateY(-2px) si nécessaire */
        box-shadow: 0 4px 15px rgba(0,0,0,0.3); /* Ombre plus intense */
    }

    /* Cache l'indicateur bleu par défaut de l'onglet sélectionné */
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"]::after {
        content: none !important;
    }

    /* Texte des onglets (pour assurer le Poppins et la bonne taille) */
    .stTabs [data-testid="stTabContent"] {
        font-family: 'Poppins', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# En-tête principal
st.markdown('<h1 class="main-header">Ecoute moi Cha 🐈!!!</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle"> Ton humeur, mon choix ;-) </p>', unsafe_allow_html=True)

# Ligne de séparation décorative
st.markdown("---")

# Fonction pour afficher l'égaliseur (maintenant une fonction)
def display_equalizer():
    st.markdown("""
        <div class="equalizer-container">
            <div class="equalizer-bar"></div>
            <div class="equalizer-bar"></div>
            <div class="equalizer-bar"></div>
            <div class="equalizer-bar"></div>
            <div class="equalizer-bar"></div>
            <div class="equalizer-bar"></div>
            <div class="equalizer-bar"></div>
            <div class="equalizer-bar"></div>
            <div class="equalizer-bar"></div>
            <div class="equalizer-bar"></div>
        </div>
    """, unsafe_allow_html=True)

# Utilisation des onglets pour la navigation
tab1, tab2, tab3 = st.tabs(["Song-to-Song", "Mood-to-Playlist", "Activity-to-Playlist"])

with tab1:
    st.markdown('<h2 class="section-header">Découvrez des Sons Similaires</h2>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        song_name = st.text_input("Nom de la chanson", placeholder="Ex: Imagine - John Lennon", key="song_input")
        if st.button("Lancer Similarités", key="launch_similarity_button"):
            if song_name:
                with st.spinner('Analyse en cours...'):
                    time.sleep(2)
                st.success("Recommandations trouvées !")
                # Afficher l'égaliseur quand des recommandations sont trouvées (simule la lecture)
                display_equalizer()
                st.markdown("<div class='song-list'>Voici quelques morceaux similaires (simulés) :</div>", unsafe_allow_html=True)
                st.markdown("1. Imagine - John Lennon (Original)")
                st.markdown("2. Let It Be - The Beatles")
                st.markdown("3. Hallelujah - Leonard Cohen")
            else:
                st.error("Veuillez entrer le nom d'une chanson !")

with tab2:
    st.markdown('<h2 class="section-header">Playlist selon votre Humeur</h2>', unsafe_allow_html=True)

    moods = ["Triste", "Joyeux", "Calme", "Énergique"]
    selected_mood = st.selectbox("Choisissez votre humeur :", moods, key="mood_selector")

    genres_mood = [
        "Tous genres", "Variété française", "Jazz/Blues", "Rap",
        "Classique/Opéra", "Rock/Indie", "Pop", "Électro/Dance"
    ]
    selected_genre_mood = st.selectbox("Affiner par genre :", genres_mood, key="genre_mood_selector")

    if st.button("Créer Playlist Humeur", key="create_mood_playlist_button"):
        with st.spinner('Création playlist...'):
            time.sleep(2)
        genre_text = f" dans le genre {selected_genre_mood}" if selected_genre_mood != "Tous genres" else ""
        st.success(f"Playlist pour {selected_mood}{genre_text}")
        # Afficher l'égaliseur quand la playlist est créée
        display_equalizer()
        st.markdown("<div class='song-list'>Votre playlist (simulée) :</div>", unsafe_allow_html=True)

        mood_dict = {
            "Triste": ["Someone Like You - Adele", "Fix You - Coldplay"],
            "Joyeux": ["Happy - Pharrell Williams", "Walking on Sunshine - Katrina & The Waves"],
            "Calme": ["River Flows in You - Yiruma", "Holocene - Bon Iver"],
            "Énergique": ["Don't Start Now - Dua Lipa", "Thunderstruck - AC/DC"]
        }
        for i, track in enumerate(mood_dict[selected_mood], 1):
            st.markdown(f"{i}. {track}")

with tab3:
    st.markdown('<h2 class="section-header">Musique pour Activité</h2>', unsafe_allow_html=True)

    activities = [
        "Danse & Fête",
        "Sport & Cardio",
        "Méditation & Yoga",
        "Concentration & Travail"
    ]
    selected_activity = st.selectbox("Choisissez votre activité :", activities, key="activity_selector")

    genres_activity = [
        "Tous genres", "Variété française", "Jazz/Blues", "Rap",
        "Classique/Opéra", "Rock/Indie", "Pop", "Électro/Dance"
    ]
    selected_genre_activity = st.selectbox("Affiner par genre :", genres_activity, key="genre_activity_selector")

    if st.button("Créer Playlist Activité", key="create_activity_playlist_button"):
        with st.spinner('Création playlist...'):
            time.sleep(2)
        genre_text = f" dans le genre {selected_genre_activity}" if selected_genre_activity != "Tous genres" else ""
        st.success(f"Playlist pour {selected_activity}{genre_text}")
        # Afficher l'égaliseur quand la playlist est créée
        display_equalizer()
        st.markdown("<div class='song-list'>Votre playlist (simulée) :</div>", unsafe_allow_html=True)

        activity_dict = {
            "Danse & Fête": ["Taki Taki - DJ Snake", "Levitating - Dua Lipa"],
            "Sport & Cardio": ["Eye of the Tiger - Survivor", "Stronger - Kanye West"],
            "Méditation & Yoga": ["Weightless - Marconi Union", "Zen Garden - Meditation Music"],
            "Concentration & Travail": ["Lo-Fi Hip Hop - Chillhop Music", "Time - Hans Zimmer"]
        }
        for i, track in enumerate(activity_dict[selected_activity], 1):
            st.markdown(f"{i}. {track}")

# Pied de page
st.markdown("---")
st.markdown('<div class="footer-style"><p>Créé par Pauline, Gaelle, Bertrand et Hassan</p></div>', unsafe_allow_html=True)