import sys
from PySide6.QtWidgets import QApplication

from sequenceur.moteur_audio import MoteurAudio
from sequenceur.coeur import SequenceurCore
from interface.fenetre_principale import FenetrePrincipale
from interface.style import THEME_SOMBRE

def main():
    """Point d'entrée principal de l'application."""
    
    # 1. Initialisation de la couche Audio
    moteur_audio = MoteurAudio()
    
    # 2. Initialisation de la couche Logique (Core)
    sequenceur_core = SequenceurCore(moteur_audio)
    
    # 3. Initialisation de l'interface graphique (PySide6)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(THEME_SOMBRE)
    
    # 4. Création et affichage de la fenêtre principale
    window = FenetrePrincipale(sequenceur_core)
    window.show()
    
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()