# src/sequenceur/coeur.py
import os

class Piste:
    """Représente une piste audio avec son sample associé et son pattern rythmique."""
    def __init__(self, nom: str, sample_path: str):
        self.nom = nom
        self.sample_path = sample_path 
        self.is_mute = False 
        self.pattern = [False] * 16

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
        NOUVEAUTÉ MARS : Change le sample d'une piste et met à jour son nom.
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
        if 0 <= index_piste < len(self.pistes):
            path = self.pistes[index_piste].sample_path
            self.moteur_audio.jouer_mix([path])

    def update_step(self, index_piste: int, index_step: int, est_actif: bool):
        if 0 <= index_piste < len(self.pistes):
            self.pistes[index_piste].pattern[index_step] = est_actif

    def jouer_step_actuel(self):
        chemins_a_jouer = []
        for piste in self.pistes:
            if piste.pattern[self.step_actuel] and not piste.is_mute:
                chemins_a_jouer.append(piste.sample_path)
                print(f" -> {piste.nom}", end="") 
        
        if chemins_a_jouer:
            print(f" | Pas {self.step_actuel + 1}")
            self.moteur_audio.jouer_mix(chemins_a_jouer)
        
    def pas_suivant(self):
        self.step_actuel += 1
        if self.step_actuel >= 16:
            self.step_actuel = 0

    def exporter_donnees(self):
        donnees = {
            "bpm": self.bpm,
            "volume": self.moteur_audio.volume_global,
            "pistes": []
        }
        for piste in self.pistes:
            donnees["pistes"].append({
                "nom": piste.nom,
                "sample_path": piste.sample_path, # On sauvegarde le chemin du son 
                "is_mute": piste.is_mute,
                "pattern": piste.pattern.copy()
            })
        return donnees

    def importer_donnees(self, donnees: dict):
        self.bpm = donnees.get("bpm", 120)
        self.moteur_audio.set_volume(donnees.get("volume", 1.0))
        
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
                self.pistes[i].pattern = piste_data.get("pattern", [False] * 16)