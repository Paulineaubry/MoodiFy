
# MoodiFy – Recommandation Musicale Contextuelle

## Contexte

Projet réalisé dans le cadre de la formation Data Analyst à la Wild Code School.  
Objectif : créer un moteur de recommandation musicale basé sur l’**humeur**, l’**activité** ou une **chanson donnée**, à partir d’un dataset Spotify enrichi.
Suite à l'étude de marché nous observons l'importance des genres et des tranches d'age dans l'écoute de musique en streaming des français. Nous faisons donc un choix par répartition en ce sens.
---

## Fonctionnalités prévues

- **Song-to-Song** : recommandation de morceaux similaires.
- **Mood-to-Playlist** : génération de playlists en fonction d’une humeur.
- **Activity-to-Playlist** : playlist adaptée à une activité (travail, sport, etc.).

---

## 👥 Équipe

- Hassan Saleban
- Bertrand Devulder
- Gaëlle Giovanazzi
- Pauline Aubry
  
## Avancement

- Etude de marché : Étude de marché.pdf
- Repartition par genre musical et tranche d'age: A AJOUTER
- Analyse exploratoire du dataset Spotify : notebook: moodify_preparation.ipynb
- Nettoyage des valeurs aberrantes : script: clean_data.py
- Suppression de la colonne peu fiable (`genre`), remplacement de valeurs nulles : script: clean_data.py
- Analyse de corrélation préliminaire
- Enrichissement avec vrai nom des genres via l’URI Spotify :  script: genre_par_artist.py
- DF de 10000 lignes les plus populaires après clean: df_test.csv 


## En cours
- Enrichissement des noms d'album
- Enrichissement des dates de sorties
- Enrichissement des pochettes
- Enrichissement des paroles


---

## Technologies

- Python, Pandas
- APIs : Spotify, Last.fm
- Jupyter Notebook

---

## 📁 Structure du repo

---

## 📌 À venir

- Analyse de corrélation après enrichissement
- Enrichissement via API Spotify & Last.fm (tags `mood` et `activity`)
- Implémentation des 3 systèmes de recommandation
- Interface utilisateur (Streamlit ou autre)

---



