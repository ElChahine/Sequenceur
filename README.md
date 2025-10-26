# Sequenceur
Création d'un séquenceur musical en python dans le cadre du projet personnel en L3 Sciences du Numérique


## I. Configuration de l'environnement

L'utilisation d'un environnement virtuel python est recommandé pour l'utilisation de ce projet.

**1. Création de l'Environnement (À faire une seule fois)**


À la racine du projet (le dossier contenant `README.md` et `.gitignore`), exécutez la commande pour créer le dossier de l'environnement virtuel `venv` :
```bash
python -m venv venv
```
**2. Activation de l'Environnement**

Avant d'utiliser le projet, vous devez toujours activer l'environnement virtuel.
```bash
Windows (Invite de commandes/CMD) : venv\Scripts\activate.bat
```
```bash
Linux/macOS : source venv/bin/activate
```
(Le prompt de votre terminal affichera (venv) au début de la ligne, confirmant que vous vous trouvez dans l'environnement du projet.)

**3. Installation des Bibliothèques (Dépendances)**

Une fois l'environnement activé, installez toutes les bibliothèques externes nécessaires (PyGame, etc.) en utilisant le fichier requirements.txt partagé :
```Bash
pip install -r requirements.txt
```

## II. Suite