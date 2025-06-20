import pandas as pd

df = pd.read_csv('df_concat.csv')
def creer_tags_manuel(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute deux colonnes :
      - tags_humeur  : #joyeux, #triste, #energique, #calme
      - tags_activité: #dance/#fête, #concentration/#travail,
                       #sport/#cardio, #meditation/#yoga
    """
    # Définition du tag d'humeur
    def tag_humeur(valence, acousticness, loudness):
        if valence >= 0.75:
            return "#joyeux"
        if valence < 0.25:
            return "#triste"
        if loudness >= -20 or acousticness < 0.3:
            return "#energique"
        return "#calme"

    # Définition du tag d'activité
    def tag_activite(danceability, energy, tempo):
        if danceability >= 0.5:
            return "#dance/#fête"
        if energy >= 0.6 or tempo >= 110:
            return "#sport/#cardio"
        if energy >= 0.3:
            return "#concentration/#travail"
        return "#meditation/#yoga"

    # Application ligne par ligne
    df["tags_humeur"] = df.apply(
        lambda r: tag_humeur(r["valence"], r["acousticness"], r["loudness"]), axis=1
    )
    df["tags_activité"] = df.apply(
        lambda r: tag_activite(r["danceability"], r["energy"], r["tempo"]), axis=1
    )

    # Vérification des tags uniques et comptages
    uniques_humeur = df["tags_humeur"].unique().tolist()
    compte_humeur = df["tags_humeur"].value_counts().reset_index()
    compte_humeur.columns = ["tag_humeur", "occurrences"]

    uniques_activite = df["tags_activité"].unique().tolist()
    compte_activite = df["tags_activité"].value_counts().reset_index()
    compte_activite.columns = ["tag_activité", "occurrences"]

    # Affichage des vérifications
    print("Tags d'humeur uniques :", uniques_humeur)
    print("\nRépartition des tags d'humeur :")
    print(compte_humeur)

    print("\nTags d'activité uniques :", uniques_activite)
    print("\nRépartition des tags d'activité :")
    print(compte_activite)

    return df


df_final = creer_tags_manuel(df)
df_final.to_csv('df_final.csv', index=False)