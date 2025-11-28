import sys
from PySide6.QtWidgets import QApplication

# Imports des classes POO
from sequenceur.moteur_audio import MoteurAudio
from sequenceur.coeur import SequenceurCore
from interface.fenetre_principale import FenetrePrincipale
from interface.style import THEME_SOMBRE

# Chemin sample test
# NOTE: Nous allons utiliser un sample général pour initialiser le moteur
# car le SequenceurCore chargera les samples spécifiques des pistes.
SAMPLE_TEST_PATH = "assets/sounds/KICK/kick_01.wav" 

def main():
    """Point d'entrée principal: Assemble les classes et lance l'application."""
    
    # 1. Initialiser le Moteur Audio
    moteur_audio = MoteurAudio(SAMPLE_TEST_PATH)
    
    # 2. Initialiser le Cœur du Séquenceur, en lui passant le moteur audio
    sequenceur_core = SequenceurCore(moteur_audio)
    
    # 3. Créer l'application PySide
    app = QApplication(sys.argv)
    
    #Application du style
    app.setStyle("Fusion")
    app.setStyleSheet(THEME_SOMBRE)
    
    # 4. Créer la fenêtre, en lui passant le Cœur
    # L'interface aura accès aux pistes via le Core.
    window = FenetrePrincipale(sequenceur_core)
    window.show()
    
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()