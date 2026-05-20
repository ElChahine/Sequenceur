# Séquenceur de Musique Électronique

Création d'un séquenceur musical en Python dans le cadre du projet personnel en L3 Sciences du Numérique. Cette application permet de composer, d'éditer et de lire des motifs rythmiques en temps réel avec des effets audio intégrés.

## I. Configuration de l'environnement

L'utilisation d'un environnement virtuel Python est fortement recommandée pour isoler les dépendances du projet.

**1. Création de l'Environnement (À faire une seule fois)**

À la racine du projet (le dossier contenant `README.md` et `.gitignore`), exécutez la commande suivante pour créer le dossier de l'environnement virtuel `venv` :
```bash
python -m venv venv
```

**2. Activation de l'Environnement**

Avant d'utiliser le projet, vous devez toujours activer l'environnement virtuel selon votre système :

* **Windows (Invite de commandes / CMD) :**
  ```cmd
  venv\Scripts\activate
  ```
* **Linux / macOS :**
  ```bash
  source venv/bin/activate
  ```

*(Le prompt de votre terminal affichera `(venv)` au début de la ligne, confirmant que l'environnement est actif).*

**3. Installation des Bibliothèques (Dépendances)**

Une fois l'environnement activé, installez toutes les bibliothèques externes requises (PySide6, NumPy, sounddevice, soundfile) :
```bash
pip install -r requirements.txt
```

---

## II. Lancement de l'application

Une fois l'environnement virtuel activé et les dépendances installées, exécutez le script principal depuis la racine du projet :

```bash
python src/main.py
```

---

## III. Guide d'utilisation & Fonctionnalités

Le logiciel est conçu comme une boîte à rythmes moderne organisée autour d'un workflow fluide :

* **Grille de 64 Pas** : Cochez les cases de la matrice pour programmer vos rythmes sur 4 mesures complètes.
* **Timeline Interactive** : Cliquez directement sur les chiffres ou les points (`1 . . . 2 . . .`) au-dessus de la grille pour faire sauter le curseur de lecture instantanément à l'endroit désiré.
* **Contrôles Globaux** : Ajustez le tempo en temps réel (de 60 à 200 BPM) et le volume général à l’aide des curseurs horizontaux.
* **Gestion des Effets (DSP)** : 
  * **Delay** : Dosable de 0 % à 80 % pour ajouter un écho temporel.
  * **Filtre Passe-Bas** : Permet d'étouffer les fréquences aiguës pour donner de la profondeur aux basses.
* **Gestion des fichiers** :
  * `💾 Sauvegarder Projet` / `📂 Charger Projet` : Enregistre l'état complet de votre composition au format JSON.
  * `💾 Exporter WAV` : Calcule et exporte le mixage audio final dans un fichier physique `.wav` de haute qualité.

### Raccourcis Clavier
* **Barre d'espace** : Déclenche ou arrête la lecture en boucle (`PLAY` / `STOP`), peu importe l'élément sélectionné dans l'interface.

---

## IV. Architecture du Projet

Le code source suit une structure modulaire stricte afin de séparer la logique métier de l'affichage graphique :

* **`src/interface/fenetre_principale.py`** : Gère l'interface utilisateur développée avec PySide6, la zone de défilement de la grille (`QScrollArea`) et les interactions clavier/souris.
* **`src/sequenceur/coeur.py`** : Contient la logique interne du séquenceur, l'état des patterns, la mise à jour des pas et l'algorithme de sommation pour le rendu *offline*.
* **`src/sequenceur/moteur_audio.py`** : Pilote le flux audio asynchrone (*callback* temps réel), le stockage des samples en RAM et les processeurs d'effets mathématiques NumPy.
* **`src/interface/style.py`** : Centralise la feuille de style CSS pour appliquer le thème sombre industriel à l'application.