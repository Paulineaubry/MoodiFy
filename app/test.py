import pickle

with open("meilleur_modele.pkl", "rb") as f:  # <- remplace ici
    obj = pickle.load(f)

print(type(obj))
