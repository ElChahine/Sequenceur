from PySide6.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout

class FenetrePrincipale(QMainWindow):
    """
    Fenêtre principale de l'application. Gère l'entrée utilisateur.
    """
    def __init__(self, moteur_audio_instance):
        super().__init__() 
        self.setWindowTitle("Séquenceur Python - Prototype Décembre")
        self.setGeometry(100, 100, 400, 200)

        self.moteur_audio = moteur_audio_instance 
        
        # Structure de la fenêtre
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Création du bouton Play
        self.play_button = QPushButton("Play Sample (Refactorisé)")
        
        # Connexion : Le bouton appelle la méthode play_sample() du moteur audio
        self.play_button.clicked.connect(self.moteur_audio.play_sample)
        
        layout.addWidget(self.play_button)