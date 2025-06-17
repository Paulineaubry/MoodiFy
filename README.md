# MoodiFy


## Objectif & Enjeux
Vous êtes un AI Engineer junior freelance. Une start-up française spécialisée dans les applications musicales vous contacte. Elle souhaite lancer une nouvelle application qui se démarque de la concurrence par ses recommandations musicales innovantes.

La start-up vous demande de développer trois fonctionnalités principales :

### Song-to-Song : 
      Recommander des chansons similaires à partir d’une chanson sélectionnée par l’utilisateur
### Mood-to-Playlist : 
Générer une playlist adaptée à l’humeur exprimée par l’utilisateur (joyeux, mélancolique, énergique, etc.)
### Activity-to-Playlist : 
Proposer une playlist adaptée à une activité spécifique (sport, méditation, travail, conduite, etc.)
Pour mener à bien ce projet, la start-up vous fournit un accès au dataset public de Spotify, mais celui-ci présente un défi majeur : il ne contient pas de données explicites sur l’humeur ou les activités associées aux chansons. Vous devrez donc enrichir ces données pour répondre aux objectifs du projet.

Commencez par une étude de marché sur les habitudes d’écoute musicale des français et sur les applications de recommandation musicale existantes. Cette analyse vous permettra de mieux comprendre les attentes des utilisateurs et de positionner votre solution de manière pertinente.

Après cette étude, réalisez une analyse approfondie de la base de données Spotify pour identifier les corrélations entre les caractéristiques audio et les perceptions humaines. Cette exploration devrait inclure : l’analyse des attributs audio (tempo, énergie, dansabilité, etc.), l’évolution des préférences musicales au fil du temps, la popularité des genres musicaux, et les caractéristiques communes aux titres les plus écoutés.

Sur la base de ces informations, vous devrez développer une stratégie d’enrichissement des données pour attribuer des “tags” d’humeur et d’activité aux chansons de la base de données.

# ressources:
- Spotify Dataset sur Kaggle: https://www.kaggle.com/datasets/zaheenhamidani/ultimate-spotify-tracks-db?resource=download
- Documentation de l’API Spotify: https://developer.spotify.com/documentation/web-api
- ressource complémentaire : http://millionsongdataset.com/
- pour l’enrichissement des données : https://musicbrainz.org/
- pour les tags communautaires : https://www.last.fm/api


# Questions à vous poser :
1. Quelles caractéristiques audio semblent les plus pertinentes pour identifier une humeur spécifique?

D'après nos premiers analyses, plusieurs caractéristiques musicale semblent être des indicateurs de l'humeur : 
- acousticness : probabilité que la piste soit acoustique (entre 0 et 1, 0 pas accoustique, 1 accoustique). 
Un morceau plutôt acoustique (valeur proche de 1) indique une humeur plutôt calme et mélancolique (ambiance relaxante), voir triste (si le mode est mineur). Catalogue dominé par la musique électronique (acousticness proche de zéro, 75% des morceaux du catalogue)
- danceability (probabilité que la piste soit dansable entre 0 et 1), 0 pas dansant, 1 dansant. 
Un morceau ayant une danceability proche de 1 indique un morceau plutôt dançant (musique de danse ou de fête). Excellente variable pour détecter l'humeur festive-sociale (30% des morceaux de catalogue)
- energy : niveau d’intensité de la piste (entre 0 et 1), 0 équivaut à calme et 1 à énergique.
Catalogue orienté musique dynamique (75% des morceaux ont une énergie > 0.39) voire une musique très énergique pour motivation ou sport (valeur supérieur à 0,8).
- instrumentalness : estimation du degré d’instrumentalité (entre 0 et 1).
0 peu ou pas instrumental (avec voix), 1 instrumental (peu ou pas de voix). La majorité du catalogue contient des morceaux non-instrumental (75% des morceaux < 0.000044). Pour la concentration et al méditation, la musique instrumentale est idéale (valeur supérieur à 0,5)
- loudness: niveau sonore moyen de la piste en décibel (dB).
Norme : -35 à 0. Permet de détecter une musique douce (valeurs proches allant vers -60db) ou bruyante (proche de 0). 25% des morceaux < -11.77 dB.
- mode : indique si la piste est en mode majeur ou mineur.
Le mode mineur (minor) indique des morceaux d'humeur triste. Le mode majeur (major) indique quant à lui des morceaux limineux (voire joyeux).
- tempo : estimation du tempo en battements par minute (BPM).
ex. : 120 BPM = tempo modéré, 180 BPM = très rapide. Permet de décrire des morceaux écouter dans certaine activités (sport : tempo modéré à rapide, relaxation-sommeil: tempo lent à très lent)
- valence : mesure de positivité véhiculée par la piste (0 sobre, 1 joyeux).
Seuils critiques : Q1=0.24 (musique triste), Q3=0.66 (musique joyeuse). Permet une classification binaire efficace (humeur positive-négative).

2. Comment combiner plusieurs attributs pour obtenir une classification plus précise?

La recherche de corrélation entre différentes variables permettra d'obtenir une classification plus précise : loudness/energy, acousticness/tempo, danceability/tempo, energy/danceability, energy/tempo, mode/valence. 

Analyse exploratoire des données
L’analyse des caractéristiques audio révèle des patterns intéressants. Les données montrent des corrélations significatives entre différentes dimensions :
	•	Valence et Energy : corrélation de 0.72, indiquant que les morceaux joyeux tendent à être énergiques
	•	Energy et Tempo : corrélation très forte de 0.95, confirmant le lien entre rythme et énergie
	•	Valence et Tempo : corrélation de 0.87, suggérant que les tempos rapides sont associés à des émotions positives
Les statistiques descriptives montrent :
	•	Valence : moyenne de 0.5 (écart-type 0.26), distribution équilibrée entre émotions positives et négatives
	•	Energy : moyenne de 0.57 (écart-type 0.22), légèrement orientée vers les morceaux énergiques
	•	Tempo : moyenne de 125.8 BPM (écart-type 13.9), centré sur les tempos modérés


Humeurs émotionnelles :
	•	Joie/Bonheur : valence élevée, energy élevée
	•	Tristesse/Mélancolie : valence faible, energy faible
	•	Calme/Sérénité : valence modérée-élevée, energy faible
	•	Excitation/Énergie : valence élevée, energy très élevée
	•	Colère/Frustration : valence faible, energy élevée
Activités contextuelles :
	•	Sport/Entraînement : energy très élevée, tempo rapide
	•	Travail/Concentration : energy modérée, instrumentalness élevée
	•	Détente/Relaxation : energy faible, acousticness élevée
	•	Fête/Social : danceability élevée, valence élevée
	•	Étude : speechiness faible, energy modérée


3. Quels genres musicaux sont généralement associés à certaines activités?

Pistes : 
- Sport : rock, dance, electro, métal, pop
- Médiatition : chants tibétains, electro
- Sommeil : playlist zen, classique
- Travail/concentration : electro, ambiant, classique
- Fêtes/soirées : electro, disco, funk, pop

4. Comment gérer les cas ambigus ou les chansons qui pourraient appartenir à plusieurs catégories?

Piste : ratacher la morceau au style principal de l'artiste

5. Quelles sources externes pourraient vous aider à valider vos classifications?

Pistes :
- bases de données externes
- enrichissement des données : API Spotify, Last FM ...


6. Veillez à documenter soigneusement votre code et vos méthodologies d’enrichissement de données pour faciliter la maintenance future du projet.


