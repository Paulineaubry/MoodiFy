import streamlit as st
import pandas as pd
import numpy as np
import time

# Configuration de la page
st.set_page_config(
    page_title="🎵 MoodiFy - Votre DJ Personnel", 
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
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
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
st.markdown('<h1 class="main-header">🎵 MoodiFy</h1>', unsafe_allow_html=True)
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
        st.markdown("### 🎶 **Recherche de Similarités**")
        song_name = st.text_input(
            "Nom de la chanson", 
            placeholder="Ex: Imagine - John Lennon",
            help="Tapez le nom d'une chanson et découvrez des morceaux similaires"
        )
        
        if st.button("🚀 **Découvrir des Similarités**"):
            if song_name:
                with st.spinner('🎵 Analyse en cours...'):
                    time.sleep(2)
                
                st.success("✨ **Recommandations trouvées !**")
                
                st.markdown(f'''
                <div class="recommendation-box">
                    <h3>🎯 Inspiré par : <strong>{song_name}</strong></h3>
                    <h4>🎼 Nos Recommandations :</h4>
                </div>
                ''', unsafe_allow_html=True)
                
                recommendations = [
                    "🎸 Let it Be - The Beatles",
                    "🎤 Hey Jude - The Beatles", 
                    "👑 Bohemian Rhapsody - Queen",
                    "🌟 Dream On - Aerosmith",
                    "🎹 Piano Man - Billy Joel",
                    "🎵 Bridge Over Troubled Water - Simon & Garfunkel"
                ]
                
                for i, song in enumerate(recommendations, 1):
                    st.markdown(f'<div class="song-list">{i}. {song}</div>', unsafe_allow_html=True)
                
                st.balloons()
            else:
                st.error("🎵 Veuillez entrer le nom d'une chanson !")

# 🎭 MOOD-TO-PLAYLIST
elif choice == "🎭 Mood-to-Playlist":
    st.markdown('<h2 class="section-header">🎭 Playlist selon votre Humeur</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 😊 **Générateur d'Ambiance**")
        
        mood_options = [
            "😊 Joyeux & Optimiste",
            "🧘 Calme & Relaxant", 
            "😢 Mélancolique & Pensif",
            "⚡ Énergique & Motivant",
            "💕 Romantique & Doux",
            "🎉 Festif & Dansant"
        ]
        
        mood = st.selectbox(
            "Quelle est votre humeur du moment ?", 
            mood_options,
            help="Sélectionnez l'humeur qui correspond à votre état d'esprit actuel"
        )
        
        if st.button("🎨 **Créer ma Playlist Personnalisée**"):
            with st.spinner('🎭 Création de votre playlist...'):
                time.sleep(2)
            
            st.success("🎧 **Votre playlist est prête !**")
            
            st.markdown(f'''
            <div class="recommendation-box">
                <h3>🎵 Playlist {mood}</h3>
                <p><em>Sélection personnalisée pour votre humeur actuelle</em></p>
            </div>
            ''', unsafe_allow_html=True)
            
            mood_playlists = {
                "😊 Joyeux & Optimiste": [
                    "🌈 Happy - Pharrell Williams",
                    "💃 Can't Stop The Feeling - Justin Timberlake",
                    "☀️ Good as Hell - Lizzo",
                    "🎊 Walking on Sunshine - Katrina & The Waves",
                    "🌻 Three Little Birds - Bob Marley"
                ],
                "🧘 Calme & Relaxant": [
                    "🌊 Holocene - Bon Iver",
                    "🎹 River Flows in You - Yiruma",
                    "🌙 Mad World - Gary Jules",
                    "🍃 Breathe Me - Sia",
                    "🌸 Gymnopédie No.1 - Erik Satie"
                ],
                "😢 Mélancolique & Pensif": [
                    "💔 Someone Like You - Adele",
                    "🌧️ Fix You - Coldplay",
                    "🖤 Hurt - Johnny Cash",
                    "😭 The Sound of Silence - Disturbed",
                    "🌫️ Black - Pearl Jam"
                ],
                "⚡ Énergique & Motivant": [
                    "🔥 Don't Start Now - Dua Lipa",
                    "💥 Thunderstruck - AC/DC",
                    "🚀 Pump It - Black Eyed Peas",
                    "⚡ Till I Collapse - Eminem",
                    "💪 Stronger - Kelly Clarkson"
                ],
                "💕 Romantique & Doux": [
                    "❤️ Perfect - Ed Sheeran",
                    "💖 All of Me - John Legend",
                    "🌹 Make You Feel My Love - Adele",
                    "💑 At Last - Etta James",
                    "✨ A Thousand Years - Christina Perri"
                ],
                "🎉 Festif & Dansant": [
                    "🎊 Levitating - Dua Lipa",
                    "🪩 Stayin' Alive - Bee Gees",
                    "🕺 I Wanna Dance with Somebody - Whitney Houston",
                    "🎵 Mr. Brightside - The Killers",
                    "🔥 Uptown Funk - Bruno Mars"
                ]
            }
            
            selected_playlist = mood_playlists.get(mood, [])
            for i, song in enumerate(selected_playlist, 1):
                st.markdown(f'<div class="song-list">{i}. {song}</div>', unsafe_allow_html=True)
            
            st.balloons()

# 🏃 ACTIVITY-TO-PLAYLIST
elif choice == "🏃 Activity-to-Playlist":
    st.markdown('<h2 class="section-header">🏃 Musique pour vos Activités</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### ⚙️ **Optimiseur d'Activité**")
        
        activity_options = [
            "🏃 Sport & Cardio",
            "🧘 Méditation & Yoga",
            "🕺 Danse & Fête",
            "💼 Concentration & Travail",
            "😴 Sommeil & Détente",
            "🚗 Conduite & Route",
            "🍳 Cuisine & Créativité"
        ]
        
        activity = st.selectbox(
            "Quelle activité pratiquez-vous ?", 
            activity_options,
            help="Choisissez l'activité pour laquelle vous voulez une playlist adaptée"
        )
        
        if st.button("🎯 **Générer la Playlist Parfaite**"):
            with st.spinner('⚙️ Optimisation de votre playlist...'):
                time.sleep(2)
            
            st.success("🎶 **Playlist optimisée créée !**")
            
            st.markdown(f'''
            <div class="recommendation-box">
                <h3>🎵 Playlist pour {activity}</h3>
                <p><em>Musique spécialement sélectionnée pour votre activité</em></p>
            </div>
            ''', unsafe_allow_html=True)
            
            activity_playlists = {
                "🏃 Sport & Cardio": [
                    "🥊 Eye of the Tiger - Survivor",
                    "💪 Stronger - Kanye West",
                    "🔥 Lose Yourself - Eminem",
                    "⚡ Thunder - Imagine Dragons",
                    "🏃 Run the World - Beyoncé"
                ],
                "🧘 Méditation & Yoga": [
                    "🌸 Weightless - Marconi Union",
                    "🌊 Ocean Waves - Nature Sounds",
                    "🎋 Zen Garden - Meditation Music",
                    "☯️ Inner Peace - Yoga Sounds",
                    "🕉️ Om Mani Padme Hum - Tibetan Chants"
                ],
                "🕺 Danse & Fête": [
                    "💃 Taki Taki - DJ Snake",
                    "🪩 Blinding Lights - The Weeknd",
                    "🎊 Shut Up and Dance - Walk the Moon",
                    "🔥 Despacito - Luis Fonsi",
                    "🕺 Dancing Queen - ABBA"
                ],
                "💼 Concentration & Travail": [
                    "🎵 Lo-Fi Hip Hop - Chillhop Music",
                    "⏰ Time - Hans Zimmer",
                    "🌙 Moonlight Sonata - Beethoven",
                    "☕ Coffee Shop Ambience",
                    "🧠 Focus Flow - Brain.fm"
                ],
                "😴 Sommeil & Détente": [
                    "🌙 Clair de Lune - Debussy",
                    "🌧️ Rain Sounds - Relaxing Audio",
                    "🎼 Gymnopédie No.1 - Erik Satie",
                    "🌊 Gentle Waves - Sleep Sounds",
                    "✨ Sleepy Time - Ambient Music"
                ],
                "🚗 Conduite & Route": [
                    "🛣️ Life is a Highway - Tom Cochrane",
                    "🎸 Born to Be Wild - Steppenwolf",
                    "🌅 Take It Easy - Eagles",
                    "🎵 On the Road Again - Willie Nelson",
                    "🚗 Drive - Incubus"
                ],
                "🍳 Cuisine & Créativité": [
                    "🎺 Puttin' On the Ritz - Taco",
                    "🎵 Mambo No. 5 - Lou Bega",
                    "🍝 That's Amore - Dean Martin",
                    "🎶 Copacabana - Barry Manilow",
                    "👨‍🍳 Chef's Special - Instrumental Jazz"
                ]
            }
            
            selected_playlist = activity_playlists.get(activity, [])
            for i, song in enumerate(selected_playlist, 1):
                st.markdown(f'<div class="song-list">{i}. {song}</div>', unsafe_allow_html=True)
            
            st.balloons()

# 👣 Pied de page
st.markdown("---")
st.markdown('''
<div class="footer-style">
    <h4>🎵 MoodiFy - Votre compagnon musical intelligent</h4>
    <p>Créé par Pauline, Gaelle, Bertrand et Hassan</p>
</div>
''', unsafe_allow_html=True)