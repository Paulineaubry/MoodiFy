# pour savoir où on se trouve
pwd

# pour aller dans le dossier où on veut se rendre
cd < + le chemin >

# pour changer de branche : 
git checkout < + nom de la branche >

# copie d'un fichier sur l'OS windowd vers Ubuntu
cp /media/didou/Windows/Users/Administrateur/Desktop/formation\ wild/moodify/* . 

# permet de verifier la connexion du local au distant
git remote show

# origin = source du distant
git remote show origin

# créer un environnement virtuel
python3 -m venv venv_moodify
# l'active
# source lance un programme bash
source venv_moodify/bin/activate

# installe les modules 
pip install pandas

# créer une liste des modules installés avec leur version
pip freeze > requirements.txt

# on déclare ignorer les fichiers 
touch .gitignore
# ici on ignore l'environnement virtuel
echo "venv_moodify/" >> .gitignore

# ajout du fichier dans le cache git
git add df.ipynb
# pour ajouter l'ensemble des fichiers : git add.

# commente et sauvegarde la modif
git commit -m "ajout notebook première lecture du df"
# envoie au distant pour la première fois
git push -u origin branche-de-Pauline

# envoie au distant
git push


