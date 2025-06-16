
# MoodiFy – Recommandation Musicale Contextuelle

## Contexte

Projet réalisé dans le cadre de la formation Data Analyst à la Wild Code School.  
Objectif : créer un moteur de recommandation musicale basé sur l’**humeur**, l’**activité** ou une **chanson donnée**, à partir d’un dataset Spotify enrichi.

---

## Fonctionnalités prévues

- **Song-to-Song** : recommandation de morceaux similaires.
- **Mood-to-Playlist** : génération de playlists en fonction d’une humeur.
- **Activity-to-Playlist** : playlist adaptée à une activité (travail, sport, etc.).

---

## Avancement

- Nettoyage et analyse exploratoire du dataset Spotify
- Suppression des colonnes peu fiables (`genre`), remplacement de valeurs nulles
- Ajout du vrai nom des titres via l’URI Spotify
- Enrichissement en cours via API Spotify & Last.fm (tags `mood` et `activity`)

---

## Technologies

- Python, Pandas, Scikit-learn
- APIs : Spotify, Last.fm
- Jupyter Notebook

---

## 📁 Structure du repo


---

## 👥 Équipe

- Alice Dupont
- Bob Martin
- Clara Meunier
- David Morel

---

## 📌 À venir

- Finalisation du tagging humeur/activité
- Implémentation des 3 systèmes de recommandation
- Interface utilisateur (Streamlit ou autre)

---



