# src/sequenceur/coeur.py
import os
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Piste:
    """
    Représente une piste audio individuelle dans le séquenceur.
    """
    def __init__(self, nom: str, sample_path: str):
        """
        Initialise une nouvelle piste avec son pattern rythmique à vide.
        """
        self.nom = nom
        self.sample_path = sample_path 
        self.is_mute = False 
        self.pattern = [False] * 64

class SequenceurCore:
    """
    Logique métier du séquenceur.
    Gère l'état des pistes, le tempo et la coordination de la lecture.
    """
    def __init__(self, moteur_audio_instance):
        self.moteur_audio = moteur_audio_instance
        self.pistes = []
        self._initialiser_pistes()
        
        self.step_actuel = 0
        self.bpm = 120

    def _initialiser_pistes(self):
        """Initialisation des pistes par défaut et chargement des ressources audio."""
        data = [
            ("Kick", "assets/sounds/Club Techno One Shots/Techno Kick 01.wav"),
            ("Snare", "assets/sounds/Club Techno One Shots/Techno Snare 01.wav"),
            ("Hi-Hat", "assets/sounds/Club Techno One Shots/Techno Hi Hat 01.wav")
        ]
        
        for nom, path in data:
            self.pistes.append(Piste(nom, path))
            self.moteur_audio.charger_sample_en_memoire(path)
            
        print("Core: Pistes initialisées.")

    def changer_sample_piste(self, index_piste: int, nouveau_chemin: str):
        """
        Remplace le fichier audio d'une piste spécifique (Objectif Mars).
        Met à jour le cache du moteur audio et génère un nouveau nom de piste.
        """
        if 0 <= index_piste < len(self.pistes):
            # 1. Charger le nouveau son en RAM
            self.moteur_audio.charger_sample_en_memoire(nouveau_chemin)
            
            # 2. Mettre à jour la piste
            self.pistes[index_piste].sample_path = nouveau_chemin
            
            # 3. Déduire un nom court à partir du nom du fichier
            nouveau_nom = os.path.basename(nouveau_chemin).replace('.wav', '')
            self.pistes[index_piste].nom = nouveau_nom
            
            return nouveau_nom
        return None

    def jouer_piste_test(self, index_piste: int):
        """
        Déclenche immédiatement le son d'une piste pour prévisualisation.
        """
        if 0 <= index_piste < len(self.pistes):
            path = self.pistes[index_piste].sample_path
            self.moteur_audio.jouer_mix([path])

    def update_step(self, index_piste: int, index_step: int, est_actif: bool):
        """
        Met à jour l'état d'un pas (activé ou désactivé) dans le pattern d'une piste.
        """
        if 0 <= index_piste < len(self.pistes):
            self.pistes[index_piste].pattern[index_step] = est_actif

    def jouer_step_actuel(self):
        """
        Analyse les patterns de toutes les pistes pour le pas en cours.
        Envoie la liste des sons à jouer au moteur audio de manière synchronisée.
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
        Incrémente le compteur de pas et assure le bouclage (0 à 63).
        """
        self.step_actuel += 1
        if self.step_actuel >= 64:
            self.step_actuel = 0

    def exporter_donnees(self):
        """
        Série de données pour la persistance JSON
        Capture l'état complet : BPM, volume, effets et patterns de 64 pas.
        """
        donnees = {
            "bpm": self.bpm,
            "volume": self.moteur_audio.volume_global,
            "intensite_delay": self.moteur_audio.intensite_delay,
            "pistes": []
        }
        for piste in self.pistes:
            donnees["pistes"].append({
                "nom": piste.nom,
                "sample_path": piste.sample_path,
                "is_mute": piste.is_mute,
                "pattern": piste.pattern.copy()
            })
        return donnees

    def importer_donnees(self, donnees: dict):
        """
        Restaure l'état complet du séquenceur à partir d'un dictionnaire JSON.
        """
        self.bpm = donnees.get("bpm", 120)
        self.moteur_audio.set_volume(donnees.get("volume", 1.0))
        self.moteur_audio.intensite_delay = donnees.get("intensite_delay", 0.0)
        
        pistes_sauvegardees = donnees.get("pistes", [])
        for i, piste_data in enumerate(pistes_sauvegardees):
            if i < len(self.pistes):
                nouveau_chemin = piste_data.get("sample_path", self.pistes[i].sample_path)
                
                # Si le chemin a changé dans la sauvegarde, on charge le nouveau son
                if nouveau_chemin != self.pistes[i].sample_path:
                    self.changer_sample_piste(i, nouveau_chemin)
                else:
                    self.pistes[i].nom = piste_data.get("nom", self.pistes[i].nom)
                    
                self.pistes[i].is_mute = piste_data.get("is_mute", False)
                self.pistes[i].pattern = piste_data.get("pattern", [False] * 64)

    def generer_rendu_audio(self, nb_boucles=2):
        """
        Calcule mathématiquement le mixage de la boucle sans la jouer.
        Retourne un tableau NumPy prêt à être sauvegardé.
        """
        # Calcul de la durée d'un pas en échantillons
        # Formule : (60s / BPM / 4) * 44100
        samples_par_pas = int((60 / self.bpm / 4) * 44100)
        duree_totale_samples = samples_par_pas * 64 * nb_boucles
        
        # Initialisation du buffer (silence)
        rendu_final = np.zeros(duree_totale_samples, dtype='float32')
        
        for piste in self.pistes:
            if piste.is_mute:
                continue
                
            sample_data = self.moteur_audio.cache_samples.get(piste.sample_path)
            if sample_data is None:
                continue
                
            for b in range(nb_boucles):
                for step in range(64):
                    if piste.pattern[step]:
                        pos_start = (b * 64 * samples_par_pas) + (step * samples_par_pas)
                        pos_end = pos_start + len(sample_data)
                        
                        if pos_end > duree_totale_samples:
                            overlap = duree_totale_samples - pos_start
                            rendu_final[pos_start:] += sample_data[:overlap]
                        else:
                            rendu_final[pos_start:pos_end] += sample_data
                            
        rendu_final *= self.moteur_audio.volume_global
        return np.clip(rendu_final, -1.0, 1.0)