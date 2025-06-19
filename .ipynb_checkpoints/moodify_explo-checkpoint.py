import pandas as pd
df = pd.read_csv("SpotifyFeatures.csv")
print(df.head())
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Chargement des données
df = pd.read_csv("SpotifyFeatures.csv")

# Aperçu rapide
print("Nombre de lignes :", len(df))
print("\nColonnes disponibles :", df.columns.tolist())
print("\nRésumé statistique :")
print(df.describe())

# Affichage des types de colonnes
print("\nTypes de colonnes :")
print(df.dtypes)

features_audio = [
    "danceability", "energy", "loudness", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence", "tempo"
]
df.head()         # premières lignes
df.tail()         # dernières lignes
df.shape          # nombre de lignes et de colonnes
df.columns        # noms des colonnes
df.dtypes         # types de données


# Visualisation des données audio

plt.figure(figsize=(12, 8))
sns.boxplot(data=df[features_audio])        

df.duplicated().sum()    # nombre de lignes en double

# Visualisation de la distribution des données audio
plt.figure(figsize=(12, 8))
sns.histplot(data=df[features_audio], kde=True) 

# Visualisation de la corrélation entre les caractéristiques audio
plt.figure(figsize=(12, 8))
sns.heatmap(df[features_audio].corr(), annot=True, cmap="coolwarm", fmt=".2f")  
# Visualisation de la distribution de l'énergie
plt.figure(figsize=(12, 6))
sns.histplot(data=df, x="energy", bins=30, kde=True)    
# Visualisation de la distribution de la danse
plt.figure(figsize=(12, 6))
sns.histplot(data=df, x="danceability", bins=30, kde=True)      
plt.show()
import matplotlib.pyplot as plt
import seaborn as sns

# Boxplot des caractéristiques audio
plt.figure(figsize=(12, 8))
sns.boxplot(data=df[features_audio])

# Distribution des caractéristiques audio
plt.figure(figsize=(12, 8))
sns.histplot(data=df[features_audio], kde=True)

# Heatmap des corrélations
plt.figure(figsize=(12, 8))
sns.heatmap(df[features_audio].corr(), annot=True, cmap="coolwarm", fmt=".2f")

# Distribution de l'énergie
plt.figure(figsize=(12, 6))
sns.histplot(data=df, x="energy", bins=30, kde=True)

# Distribution de la danceabilité
plt.figure(figsize=(12, 6))
sns.histplot(data=df, x="danceability", bins=30, kde=True)

# Afficher tous les graphes
plt.show()
import matplotlib.pyplot as plt
import seaborn as sns

# ... tes graphiques ici ...

plt.show()  # ← affiche tous les graphiques ouverts


