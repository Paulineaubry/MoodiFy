import streamlit as st
import pandas as pd
import numpy as np
import time

# Configuration de la page
st.set_page_config(
    page_title="Ecoute Cha 🐈!!!", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 CSS amélioré mais compatible Streamlit
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
    
    .sidebar .sidebar-content {
        background: rgba(0,0,0,0.3);
        border-radius: 15px;
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
    </style>
""", unsafe_allow_html=True)

# 🎧 En-tête principal
st.markdown('<h1 class="main-header">Ecoute moi Cha 🐈!!!</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle"> Ton humeur, mon choix ;-) </p>', unsafe_allow_html=True)

# Ligne de séparation décorative
st.markdown("---")

# 👉 Sidebar
st.sidebar.markdown("## 🎛️ **Menu Musical**")
st.sidebar.markdown("*Choisissez votre expérience :*")

choice = st.sidebar.radio(
    "Navigation",
    options=["🎵 Song-to-Song", "🎭 Mood-to-Playlist", "🏃 Activity-to-Playlist"],
    label_visibility="collapsed"
)

# Informations sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎼 **À Propos**")
st.sidebar.info("MoodiFy utilise l'intelligence artificielle pour vous recommander la musique parfaite selon vos goûts et vos activités.")

# 🎵 SONG-TO-SONG
if choice == "🎵 Song-to-Song":
    st.markdown('<h2 class="section-header">🔄 Découvrez des Sons Similaires</h2>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        song_name = st.text_input("Nom de la chanson", placeholder="Ex: Imagine - John Lennon")
        if st.button("🚀 Lancer Similarités"):
            if song_name:
                with st.spinner('🎵 Analyse en cours...'):
                    time.sleep(2)
                st.success("✨ Recommandations trouvées !")
                # ... reste inchangé pour cet onglet
            else:
                st.error("Veuillez entrer le nom d'une chanson !")

# 🎭 MOOD-TO-PLAYLIST
elif choice == "🎭 Mood-to-Playlist":
    st.markdown('<h2 class="section-header">🎭 Playlist selon votre Humeur</h2>', unsafe_allow_html=True)
    moods = [
        "😢 Triste",
        "😊 Joyeux",
        "🧘 Calme",
        "⚡ Énergique"
    ]
    selected_mood = st.selectbox("Choisissez votre humeur :", moods)
    if st.button("Créer Playlist Humeur"):
        with st.spinner('Création playlist...'):
            time.sleep(2)
        st.success(f"Playlist pour {selected_mood}")
        # Exemple de playlists par humeur
        mood_dict = {
            "😢 Triste": ["Someone Like You - Adele", "Fix You - Coldplay"],
            "😊 Joyeux": ["Happy - Pharrell Williams", "Walking on Sunshine - Katrina & The Waves"],
            "🧘 Calme": ["River Flows in You - Yiruma", "Holocene - Bon Iver"],
            "⚡ Énergique": ["Don't Start Now - Dua Lipa", "Thunderstruck - AC/DC"]
        }
        for i, track in enumerate(mood_dict[selected_mood], 1):
            st.markdown(f"{i}. {track}")

# 🏃 ACTIVITY-TO-PLAYLIST
elif choice == "🏃 Activity-to-Playlist":
    st.markdown('<h2 class="section-header">🏃 Musique pour Activité</h2>', unsafe_allow_html=True)
    activities = [
        "🕺 Danse & Fête",
        "🏃 Sport & Cardio",
        "🧘 Méditation & Yoga",
        "💼 Concentration & Travail"
    ]
    selected_activity = st.selectbox("Choisissez votre activité :", activities)
    if st.button("Créer Playlist Activité"):
        with st.spinner('Création playlist...'):
            time.sleep(2)
        st.success(f"Playlist pour {selected_activity}")
        # Exemple de playlists par activité
        activity_dict = {
            "🕺 Danse & Fête": ["Taki Taki - DJ Snake", "Levitating - Dua Lipa"],
            "🏃 Sport & Cardio": ["Eye of the Tiger - Survivor", "Stronger - Kanye West"],
            "🧘 Méditation & Yoga": ["Weightless - Marconi Union", "Zen Garden - Meditation Music"],
            "💼 Concentration & Travail": ["Lo-Fi Hip Hop - Chillhop Music", "Time - Hans Zimmer"]
        }
        for i, track in enumerate(activity_dict[selected_activity], 1):
            st.markdown(f"{i}. {track}")

# 👣 Pied de page
st.markdown("---")
st.markdown('<div class="footer-style"><p>Créé par Pauline, Gaelle, Bertrand et Hassan</p></div>', unsafe_allow_html=True)
