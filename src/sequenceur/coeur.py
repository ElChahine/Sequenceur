# src/sequenceur/coeur.py
import os
import numpy as np
from sequenceur.export import AudioExporter

base = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(base))
)

class Piste:
    """
    Représente une piste audio individuelle dans le séquenceur.
    """
    def __init__(self, nom: str, sample_path: str):
        """
        Initialise une nouvelle piste avec son nom, le chemin du sample
        et sa grille de 64 pas vide par défaut.
        """
        self.nom = nom
        self.sample_path = sample_path 
        self.is_mute = False 
        self.pattern = [False] * 64

class SequenceurCore:
    """
    Logique principale qui gère le tempo, les pistes et la lecture.
    """
    def __init__(self, moteur_audio_instance):
        """
        Initialise le coeur du séquenceur avec le moteur audio, les 
        pistes par défaut et règle le tempo initial à 120 BPM.
        """
        self.moteur_audio = moteur_audio_instance
        self.pistes = []
        self._initialiser_pistes()
        
        self.step_actuel = 0
        self.bpm = 120

    def _initialiser_pistes(self):
        """
        Crée les trois pistes de base (Kick, Snare, Hi-Hat) et charge
        automatiquement leurs fichiers audio en mémoire RAM.
        """
        path_kick = (
            "assets/sounds/Club Techno One Shots/kick/"
            "Techno Kick 01.wav"
        )
        path_snare = (
            "assets/sounds/Club Techno One Shots/snare/"
            "Techno Snare 01.wav"
        )
        path_hihat = (
            "assets/sounds/Club Techno One Shots/hi-hat/"
            "Techno Hi Hat 01.wav"
        )
        
        data = [
            ("Kick", path_kick),
            ("Snare", path_snare),
            ("Hi-Hat", path_hihat)
        ]
        
        for nom, path in data:
            self.pistes.append(Piste(nom, path))
            self.moteur_audio.charger_sample_en_memoire(path)
            
        print("Core: Pistes initialisées.")

    def changer_sample_piste(self, index_piste: int, nouveau_chemin: str):
        """
        Reçoit l'index d'une piste et le chemin d'un nouveau fichier wav, 
        le charge en mémoire, change la piste et retourne son nouveau nom.
        """
        if 0 <= index_piste < len(self.pistes):
            self.moteur_audio.charger_sample_en_memoire(nouveau_chemin)
            
            self.pistes[index_piste].sample_path = nouveau_chemin
            
            nouveau_nom = os.path.basename(nouveau_chemin).replace(
                '.wav', ''
            )
            self.pistes[index_piste].nom = nouveau_nom
            
            return nouveau_nom
        return None

    def jouer_piste_test(self, index_piste: int):
        """
        Reçoit l'index d'une piste pour envoyer directement son fichier
        audio au moteur et pouvoir l'écouter instantanément.
        """
        if 0 <= index_piste < len(self.pistes):
            path = self.pistes[index_piste].sample_path
            self.moteur_audio.jouer_mix([path])

    def update_step(self, index_piste: int, index_step: int, est_actif: bool):
        """
        Met à jour l'état d'une case précise (cochée ou non) dans la 
        grille de la piste correspondante.
        """
        if 0 <= index_piste < len(self.pistes):
            self.pistes[index_piste].pattern[index_step] = est_actif

    def jouer_step_actuel(self):
        """
        Parcourt toutes les pistes pour le pas en cours et envoie la liste
        des fichiers audio cochés et non mutés au moteur de lecture.
        """
        chemins_a_jouer = []
        for piste in self.pistes:
            if piste.pattern[self.step_actuel] and not piste.is_mute:
                chemins_a_jouer.append(piste.sample_path)
                print(f" -> {piste.nom}", end="") 
        
        if chemins_a_jouer:
            print(f" | Pas {self.step_actuel + 1}")
            self.moteur_audio.jouer_mix(chemins_a_jouer)
        
    def pas_suivant(self):
        """
        Avance le curseur de lecture au pas d'après et le fait revenir
        au début (0) dès qu'il dépasse le 64ème pas.
        """
        self.step_actuel += 1
        if self.step_actuel >= 64:
            self.step_actuel = 0

    def generer_rendu_audio(self, nb_boucles=2):
        """
        Prend le nombre de boucles demandé et transmet les informations 
        au module d'exportation pour générer le tableau audio final.
        """
        return AudioExporter.exporter(
            pistes=self.pistes,
            bpm=self.bpm,
            volume_global=self.moteur_audio.volume_global,
            cache_samples=self.moteur_audio.cache_samples,
            nb_boucles=nb_boucles
        )