import pandas as pd

# Liste des artistes à rechercher
artistes_recherches = [
 "Aya Nakamura",     
    "Indila",           
    "Stromae",     
    "GIMS",           
    "Jul",              
    "Daft Punk",        
    "Christine and the Queens",  
    "M. Pokora",
    "Orelsan",         
    "Slimane",          
    "Kendji Girac",
    "Clara Luciani",
    "Louane",
    "Shy'm",
    "Vianney",
    "Calogero",
    "Hoshi",
    "Grand Corps Malade",

    "Francis Cabrel", "Jean-Jacques Goldman", "Florent Pagny", "Michel Sardou",
    "Johnny Hallyday", "Vanessa Paradis", "Julien Clerc", "Mylène Farmer",
    "France Gall", "Françoise Hardy", "Charles Aznavour", "Édith Piaf",
    "Serge Gainsbourg", "Jacques Brel", "Claude François", "Georges Brassens",
    "Claude Nougaro", "Serge Lama", "Michel Polnareff", "Alain Bashung",
    "Alain Souchon", "Véronique Sanson", "Charles Trenet", "Michel Delpech",
    "Daniel Balavoine", "Jacques Dutronc", "Christophe", "Maxime Le Forestier",
    "Laurent Voulzy", "Yves Duteil", "Léo Ferré", "Gérard Lenorman",
    "Pierre Bachelet", "Alizée", "Nolwenn Leroy", "Sheila", "Dalida",
    "Mireille Mathieu", "Pierre Perret", "Jean Ferrat", "Hugues Aufray",
    "Daniel Guichard", "Benjamin Biolay", "Zazie", "Camille", "Cali",
    "Francis Lalanne", "Louis Chedid", "Isabelle Boulay", "Charlotte Gainsbourg",
    "Jane Birkin", "Étienne Daho", "Gaël Faye", "Loïc Nottet", "La Femme",
    "Keren Ann", "Yael Naim", "Bernard Lavilliers", "Matmatah",
    "Louise Attaque", "Soldat Louis", "Gilbert Montagné", "Les Wampas",
    "Hélène Rollès", "Axelle Red", "Suzane", "Tété", "Raphaël",
    "Olivia Ruiz", "Thomas Dutronc", "Pauline Croze", "Féfé",
    "Sébastien Tellier", "Alex Beaupain", "Bénabar", "Renan Luce",
    "Manu Chao", "Tryo", "Zebda", "Sinsemilia", "Vitaa",
    "Zaho", "Superbus", "Alain Chamfort", "Nino Ferrer", "Gilbert Bécaud",
    "Yseult",           

    "Indochine", "Pascal Obispo", "Daniel Lavoie", "Marc Lavoine",
    "Jean-Louis Aubert", "Jacques Higelin", "Renaud", "Camille Lellouche",
    "Jenifer", "Arthur H", "Benjamin Biolay", "Fishbach",
    "Emily Loizeau", "Barbara", "Maurane", "Linda Lemay",
    "Jean-Jacques Debout", "Roch Voisine", "Enrico Macias",
    "Julie Zenatti", "Chimène Badi", "Lara Fabian", "Hélène Ségara",
    "Jeanne Mas", "Patricia Kaas", "Nicole Croisille", "Nicoletta",
    "Stone et Charden", "Peter et Sloane", "Boris Vian",
    "Brigitte Fontaine", "Mano Solo", "Vincent Delerm",
    "Hervé Vilard", "Dave", "Frédéric François", "Colette"
]

# Chargement du dataset
df = pd.read_csv("SpotifyFeatures.csv")  # Remplace par le chemin réel

# Suppose que la colonne avec les noms d’artistes s'appelle "artist" :
artistes_trouves = df[df["artist_name"].isin(artistes_recherches)]
artistes_trouves.to_csv('dataset_fr_origin.csv')
print(artistes_trouves)


