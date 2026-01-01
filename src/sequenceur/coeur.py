# src/sequenceur/coeur.py

class Piste:
    """
    Représente une seule ligne temporelle pour organiser des sons ou des patterns.
    """

    def __init__(self, nom: str, sample_path: str):
        self.nom = nom
        self.sample_path = sample_path 
        self.is_mute = False 
        # Pattern de 16 pas (False = silence, True = son)
        self.pattern = [False] * 16 

    def __str__(self):
        return f"Piste '{self.nom}' - Sample: {self.sample_path[-20:]}"


class SequenceurCore:
    """
    Gère la structure logique du séquenceur : Pistes, Pattern et Lecture.
    """

    def __init__(self, moteur_audio_instance):
        self.moteur_audio = moteur_audio_instance
        self.pistes = []
        self._initialiser_pistes_test()
        
        # --- NOUVEAU DECEMBRE : Gestion du Temps ---
        self.step_actuel = 0  # On commence au pas 0
        self.bpm = 120        # Tempo par défaut

    def _initialiser_pistes_test(self):
        # NOTE: Assure-toi que ces fichiers existent bien dans ton dossier assets
        self.pistes.append(Piste("Kick", "assets/sounds/Club Techno One Shots/Techno Kick 01.wav"))
        self.pistes.append(Piste("Snare", "assets/sounds/Club Techno One Shots/Techno Snare 01.wav"))
        self.pistes.append(Piste("Hi-Hat", "assets/sounds/Club Techno One Shots/Techno Hi Hat 01.wav"))
        print("\nCore: Pistes initialisées.")

    def jouer_piste_test(self, index_piste: int):
        """Test manuel d'un son (Bouton Test)"""
        if 0 <= index_piste < len(self.pistes):
            piste = self.pistes[index_piste]
            if piste.is_mute: return False
            
            # Lecture directe (Attention: sounddevice peut couper le son précédent)
            self.moteur_audio.load_sample(piste.sample_path)
            self.moteur_audio.play_sample()
            return True
        return False

    def update_step(self, index_piste: int, index_step: int, est_actif: bool):
        """Met à jour la mémoire quand on coche une case"""
        if 0 <= index_piste < len(self.pistes):
            self.pistes[index_piste].pattern[index_step] = est_actif
            etat = "Active" if est_actif else "Desactive"
            print(f"GRID: {self.pistes[index_piste].nom} -> Pas {index_step + 1} : {etat}")

    # --- NOUVEAU : LA LOGIQUE DE LECTURE EN BOUCLE ---
    def jouer_step_actuel(self):
        """
        Appelé automatiquement par le Timer à chaque temps.
        Vérifie toutes les pistes et joue les sons si la case est cochée.
        """
        sons_a_jouer = []
        
        # 1. On regarde quelles pistes doivent jouer sur ce pas
        for piste in self.pistes:
            if piste.pattern[self.step_actuel] and not piste.is_mute:
                sons_a_jouer.append(piste)
        
        # 2. On joue les sons (Pour l'instant, on joue le dernier trouvé car sounddevice est simple)
        # Note: En Janvier, on apprendra à mixer les sons ensemble.
        for piste in sons_a_jouer:
            # On charge et on joue (C'est brut, mais ça marche pour le prototype)
            self.moteur_audio.load_sample(piste.sample_path)
            self.moteur_audio.play_sample()
            print(f"♫ JOUE: {piste.nom} (Pas {self.step_actuel + 1})")

    def pas_suivant(self):
        """Avance le curseur de lecture et boucle à 0 si on dépasse 15"""
        self.step_actuel += 1
        if self.step_actuel >= 16:
            self.step_actuel = 0