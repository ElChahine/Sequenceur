import sys
import soundfile as sf
import sounddevice as sd
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout

SAMPLE_PATH = "assets\sounds\Cymatics - EDM Starter Pack\Synths - Loops\Arp Loops\Cymatics - Titan Arp Loop 77 - 170 BPM G# Min.wav" 

try:
    # Charge le fichier audio en mémoire (data) et récupère le taux d'échantillonnage (fs)
    AUDIO_DATA, SAMPLE_RATE = sf.read(SAMPLE_PATH, dtype='float32')
    print(f"Fichier chargé: {SAMPLE_PATH} à {SAMPLE_RATE} Hz")
except Exception as e:
    print(f"Erreur de chargement audio: Impossible de charger le fichier. Vérifie le chemin: {SAMPLE_PATH}. Erreur: {e}")
    #eviter un crash
    AUDIO_DATA = None
    SAMPLE_RATE = 0

def play_sample():
    """Joue le sample chargé via sounddevice."""
    if AUDIO_DATA is not None:
        try:
            # sd.play joue le tableau de données (AUDIO_DATA) au taux (SAMPLE_RATE)
            sd.play(AUDIO_DATA, SAMPLE_RATE)
            print("Sample joué.")
        except Exception as e:
            print(f"Erreur de lecture sounddevice: {e}")
    else:
        print("Erreur: Le fichier audio n'est pas chargé ou n'existe pas.")


app = QApplication(sys.argv)
window = QMainWindow()
window.setWindowTitle("Séquenceur Prototype V1 (Octobre)")

central_widget = QWidget()
window.setCentralWidget(central_widget)
layout = QVBoxLayout(central_widget)

play_button = QPushButton("Jouer Sample")
play_button.clicked.connect(play_sample)

layout.addWidget(play_button)

window.show()
sys.exit(app.exec())