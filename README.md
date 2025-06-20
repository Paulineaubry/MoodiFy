
# MoodiFy – Recommandation Musicale Contextuelle

## Contexte

Projet réalisé dans le cadre de la formation Data Analyst à la Wild Code School.  
Objectif : créer un moteur de recommandation musicale basé sur l’**humeur**, l’**activité** ou une **chanson donnée**, à partir d’un dataset Spotify enrichi.
Suite à l'étude de marché nous observons l'importance des genres et des tranches d'age dans l'écoute de musique en streaming des français. 
Nous faisons donc un choix par répartition en ce sens... Non, non non ! Notre parti pris : Votre humeur, notre choix !


## Fonctionnalités prévues

- **Song-to-Song** : recommandation de morceaux similaires.
- **Mood-to-Playlist** : génération de playlists en fonction d’une humeur.
- **Activity-to-Playlist** : playlist adaptée à une activité (travail, sport, etc.).

---

## Équipe

- Hassan Saleban
- Bertrand Devulder
- Gaëlle Giovanazzi
- Pauline Aubry
  
## Étude de Contexte

À partir d’une étude de marché sur la consommation musicale en France, nous avons intégré :
- Une **répartition des préférences par tranche d’âge** et **genre musical**
- Un **focus sur les genres francophones** pour mieux refléter les goûts locaux

## 🛠️ Installation & Configuration

### Prérequis
- Python 3.10+
- Fichier `.env` pour les clés d’API

### Installation

```bash
git clone https://github.com/votre-utilisateur/moodify.git
cd moodify
pip install -r requirements.txt
```

## EDA
- Analyse exploratoire du dataset Spotify 
- Nettoyage des valeurs aberrantes
- Suppression de la colonne peu fiable (`genre`), remplacement de valeurs nulles
- Sélection des 10000 lignes les plus populaires 
- DF de 10000 lignes les plus populaires après clean
- Analyse de corrélation préliminaire
- Enrichissement avec vrai nom des genres via l’URI Spotify et API spotify et last_fm
- Simplification de la colonne genre
- Répartition par genre selon stat de l'étude de marché sur les 10000 lignes 
- Enrichissement des lignes de variétés française Pauline 
- Concaténation sur df simplifié 
- Enrichissement tags humeur et activité 
  
## Configuration des APIs
- POUR L'API SPOTIFY:
    - Créer un compte https://developer.spotify.com/documentation/web-api
    - Créer une app:
      - Application URL : mettre http://localhost ou l'URL du projet
      - Récupérer SPOTIFY_CLIENT_ID et SPOTIFY_CLIENT_SECRET
    - Créer un fichier .env et ajouter:
      - SPOTIFY_CLIENT_ID=laclérécupérée
      - SPOTIFY_CLIENT_SECRET=lacléesecrèterécupérée
- POUR L'API LAST.FM:
    - Créer un compte https://www.last.fm/join
    - Créer une application https://www.last.fm/api/account/create:
      - Application URL : mettre http://localhost ou l'URL du projet
      - Récupérer API Key 
    - Placer la clé dans le fichier .env :
      - LASTFM_API_KEY=cléchiffréerécupérée

## En cours

- Analyse de corrélation après enrichissement
- Implémentation des 3 systèmes de recommandation
- Intégrer un appel à l'API pour trouver les pochettes d'album
- Interface utilisateur (Streamlit)

## A faire

- clean notebook pour n'avoir que l'EDA ?
- partie d'Hassan à intégrer au notebook d'analyse
---

## Technologies

- Python, Pandas
- APIs : Spotify, Last.fm
- Jupyter Notebook

---

## Structure du projet

```bash
.
├── notebooks/
│   ├── moodify_preparation.ipynb               # EDA initiale
│   ├── Correlations_préliminaires.ipynb  # Analyse des corrélations
├── scripts/
│   ├── clean_data.py                           # Nettoyage des données
│   ├── genre_par_artist.py                     # Récupération des genres via API Spotify
│   ├── requete_lastfm.py                       # Appels à l'API Last.fm
│   ├── genre_simplifie.py                      # Simplification des genres
│   ├── tagged.py                               # Ajout des tags humeur/activité
│   ├── df_fr_kaggle.py                         # Enrichissement avec des morceaux français
│   ├── df_fr_origin.py                         # Fichiers d'origine pour morceaux français
│   ├── df_clean.py                             # Nettoyage du dataframe enrichi
├── data/
│   ├── clean.csv                               # Données prêtes à l’usage
│   ├── Étude de marché.pdf
│   ├── Analyse_genres_par_age.pdf
├── app/
│   ├── streamlit_app.py                        # Interface utilisateur Streamlit (WIP)
├── .env.example                                # Modèle de fichier d'environnement (.env)
├── README.md                                   # Ce fichier
```




