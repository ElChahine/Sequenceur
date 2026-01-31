# src/sequenceur/coeur.py

class Piste:
    """Représente une piste audio avec son sample associé et son pattern rythmique."""
    def __init__(self, nom: str, sample_path: str):
        self.nom = nom
        self.sample_path = sample_path 
        self.is_mute = False 
        self.pattern = [False] * 16 # Grille de 16 pas (steps)

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
            # Préchargement des samples en RAM via le moteur audio
            self.moteur_audio.charger_sample_en_memoire(path)
            
        print("Core: Pistes initialisées.")

    def jouer_piste_test(self, index_piste: int):
        """Déclenche la lecture immédiate d'une piste (pour test manuel)."""
        if 0 <= index_piste < len(self.pistes):
            path = self.pistes[index_piste].sample_path
            self.moteur_audio.jouer_mix([path])

    def update_step(self, index_piste: int, index_step: int, est_actif: bool):
        """Met à jour l'état d'un pas dans la grille."""
        if 0 <= index_piste < len(self.pistes):
            self.pistes[index_piste].pattern[index_step] = est_actif

    def jouer_step_actuel(self):
        """
        Identifie les sons actifs pour le pas courant et délègue le mixage au moteur audio.
        """
        chemins_a_jouer = []
        
        for piste in self.pistes:
            if piste.pattern[self.step_actuel] and not piste.is_mute:
                chemins_a_jouer.append(piste.sample_path)
                print(f" -> {piste.nom}", end="") # Debug console
        
        if chemins_a_jouer:
            print(f" | Pas {self.step_actuel + 1}")
            self.moteur_audio.jouer_mix(chemins_a_jouer)
        
    def pas_suivant(self):
        """Incrémente le compteur de pas (boucle 0-15)."""
        self.step_actuel += 1
        if self.step_actuel >= 16:
            self.step_actuel = 0