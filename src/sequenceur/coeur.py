# src/sequenceur/coeur.py

class Piste:
    """
    Représente une seule ligne temporelle pour organiser des sons ou des patterns.
    
    Cette classe agit comme un conteneur de données pour une piste audio spécifique
    (ex: Kick, Snare) et son état actuel.
    """

    def __init__(self, nom: str, sample_path: str):
        """
        Initialise une nouvelle piste.

        Args:
            nom (str): Le nom d'affichage de la piste (ex: "Kick").
            sample_path (str): Le chemin relatif vers le fichier audio (.wav).
        """
        self.nom = nom
        self.sample_path = sample_path # Chemin vers le son à jouer
        self.is_mute = False # Piste muette ou non

    def __str__(self):
        """
        Retourne une représentation textuelle de la piste pour le débogage.

        Returns:
            str: Une chaîne décrivant la piste et son fichier associé.
        """
        return f"Piste '{self.nom}' - Sample: {self.sample_path[-20:]}"


class SequenceurCore:
    """
    Gère la structure logique du séquenceur.

    Cette classe centralise la gestion des données musicales (pistes, patterns, tempo)
    et fait le lien entre l'interface utilisateur et le moteur audio.
    Elle remplace l'implémentation abstraite "Core" du cahier des charges.
    """

    def __init__(self, moteur_audio_instance):
        """
        Initialise le cœur du séquenceur.

        Args:
            moteur_audio_instance (MoteurAudio): Une instance initialisée du moteur
                                                 audio pour la lecture des sons.
        """
        self.moteur_audio = moteur_audio_instance
        self.pistes = []
        self._initialiser_pistes_test() # Crée les pistes par défaut

    def _initialiser_pistes_test(self):
        """
        Méthode interne pour créer des pistes par défaut.
        
        Sert à peupler le séquenceur avec des pistes de démonstration (Kick, Snare, Hi-Hat)
        en attendant le système de chargement de projet complet.
        """
        self.pistes.append(Piste("Kick", "assets/sounds/Club Techno One Shots/Techno Kick 01.wav"))
        self.pistes.append(Piste("Snare", "assets/sounds/Club Techno One Shots/Techno Snare 01.wav"))
        self.pistes.append(Piste("Hi-Hat", "assets/sounds/Club Techno One Shots/Techno Hi Hat 01.wav"))
        
        print("\nCore: Pistes initialisées.")
        for piste in self.pistes:
            print(piste)

    def jouer_piste_test(self, index_piste: int):
        """
        Déclenche la lecture immédiate du sample associé à une piste.

        Cette fonction sert de test pour valider la chaîne de connexion 
        Interface -> Core -> Moteur Audio.

        Args:
            index_piste (int): L'index de la piste dans la liste self.pistes.

        Returns:
            bool: True si la lecture a été lancée, False si l'index est invalide.
        """
        if 0 <= index_piste < len(self.pistes):
            piste = self.pistes[index_piste]
            
            
            if piste.is_mute:
                print(f"Core: Piste '{piste.nom}' est muette. Lecture annulée.")
                return False
            
            # 1. Charger le son de la piste
            self.moteur_audio.load_sample(piste.sample_path)
            
            # 2. Jouer le son
            self.moteur_audio.play_sample()
            print(f"Core: Son de la piste '{piste.nom}' lancé.")
            return True
        return False