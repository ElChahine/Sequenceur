# src/sequenceur/moteur_audio.py

import soundfile as sf
import sounddevice as sd
import os

class MoteurAudio:
    """
    Gère le chargement et la lecture bas niveau des samples audio.

    Cette classe encapsule les bibliothèques soundfile (chargement) et 
    sounddevice (lecture) pour offrir une interface simple au reste de l'application.
    """

    def __init__(self, sample_path: str):
        """
        Initialise le moteur audio et tente de charger un premier sample.

        Args:
            sample_path (str): Le chemin vers un fichier audio pour l'initialisation.
        """
        self.audio_data = None
        self.sample_rate = 0
        self.volume_global = 1.0
        self.load_sample(sample_path)
        
    def load_sample(self, path: str):
        """
        Charge un fichier audio (.wav) dans la mémoire RAM.

        Cette méthode lit le fichier audio et stocke les données brutes (float32)
        ainsi que la fréquence d'échantillonnage.

        Args:
            path (str): Le chemin absolu ou relatif vers le fichier audio.
        """
        if not os.path.exists(path):
            print("MoteurAudio: Fichier non trouvé", path)
            return
        try:
            # dtype='float32' est le format standard pour sounddevice
            data, fs = sf.read(path, dtype='float32')
            self.audio_data = data
            self.sample_rate = fs
            print(f"MoteurAudio: Sample chargé: {path}")
        except Exception as e:
            print(f"Erreur MoteurAudio: Impossible de charger le fichier. {e}")

    def play_sample(self):
        """
        Joue le sample actuellement chargé en mémoire.

        La lecture se fait de manière non bloquante (asynchrone), permettant
        à l'interface graphique de rester réactive.

        Returns:
            bool: True si la lecture a démarré, False si aucune donnée audio n'est chargée.
        """
        if self.audio_data is not None:
            # On crée une variable temporaire pour ne pas modifier le son original définitivement
            data_volume = self.audio_data * self.volume_global
            sd.play(data_volume, self.sample_rate)
            return True
        return False
    
    def set_volume(self, valeur_0_a_1: float):
        """
        Change le volume global.
        Args:
            valeur_0_a_1 (float): Entre 0.0 (silence) et 1.0 (max).
        """
        # On s'assure que la valeur reste entre 0 et 1
        self.volume_global = max(0.0, min(1.0, valeur_0_a_1))
        
        # Affichage sans f-string
        pourcentage = int(self.volume_global * 100)
        print(f"MoteurAudio: Volume réglé à %d %% {pourcentage}")