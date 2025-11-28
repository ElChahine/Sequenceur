import sys
from PySide6.QtWidgets import QApplication

#imports relatifs aux sous-dossiers
from sequenceur.moteur_audio import MoteurAudio
from interface.fenetre_principale import FenetrePrincipale

#chemin sample test
SAMPLE_TEST_PATH = "assets\sounds\Cymatics - EDM Starter Pack\Synths - Loops\Chord Loops\Cymatics - Chord Loop 22 - Gm 150 BPM.wav"

def main():
    """
    Point d'entrée principal: Assemble les classes et lance l'application
    """
    
    #1. Initialiser le moteur audio
    moteur_audio = MoteurAudio(SAMPLE_TEST_PATH)
    
    #2. Créer l'application PySide
    app = QApplication(sys.argv)
    
    # 3. Créer la fenêtre, en lui passant le moteur audio pour la connexion
    window = FenetrePrincipale(moteur_audio)
    window.show()
    
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()