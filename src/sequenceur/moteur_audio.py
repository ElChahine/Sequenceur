import soundfile as sf
import sounddevice as sd
import os

class MoteurAudio:
    """
    Gère le chargement et la lecture des samples.
    """
    def __init__(self, sample_path):
        self.audio_data = None
        self.sample_rate = 0
        self.load_sample(sample_path)
        
    def load_sample(self, path):
        """
        Charge un fichier audio dans la mémoire
        """
        if not os.path.exists(path):
            print("MoteurAudio: Fichier non trouvé", path)
            return
        try:
            data, fs = sf.read(path, dtype='float32')
            self.audio_data = data
            self.sample_rate = fs
            print(f"MoteurAudio: Sample chargé: {path}")
        except Exception as e:
            print(f"Erreur MoteurAudio: Impossible de charger le fichier. {e}")

    def play_sample(self):
        """Joue le sample actuellement chargé de manière non bloquante."""
        if self.audio_data is not None:
            sd.play(self.audio_data, self.sample_rate)
            return True
        return False