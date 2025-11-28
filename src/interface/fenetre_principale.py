from PySide6.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout, QGridLayout, QLabel, QCheckBox
from PySide6.QtCore import Qt

class FenetrePrincipale(QMainWindow):
    """
    Fenêtre principale de l'application (GUI).

    Cette classe gère l'affichage de l'interface utilisateur avec PySide6 
    et capture les interactions (clics) pour les transmettre au SequenceurCore.
    """

    def __init__(self, sequenceur_core_instance):
        """
        Initialise l'interface graphique et construit les widgets.

        Args:
            sequenceur_core_instance (SequenceurCore): Une référence vers le cœur logique
                                                       de l'application pour connecter les boutons.
        """
        super().__init__() 
        self.setWindowTitle("Séquenceur Python - Prototype pistes (Novembre)")
        self.setGeometry(100, 100, 600, 400)
        self.sequenceur_core = sequenceur_core_instance
        
        # Structure de la fenêtre (Widget central et Layout principal)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Grille pour aligner les noms de pistes et les boutons
        pistes_grid = QGridLayout()
        main_layout.addLayout(pistes_grid)
        
        # En-tête de la grille
        pistes_grid.addWidget(QLabel("PISTES:"), 0, 0, Qt.AlignmentFlag.AlignLeft) 

        # Génération dynamique des contrôles pour chaque piste
        for i, piste in enumerate(self.sequenceur_core.pistes):
                    # 1. Nom de la piste
                    pistes_grid.addWidget(QLabel(piste.nom), i + 1, 0)
                    
                    # 2. Bouton de test
                    # On remplace le f-string ici aussi par une concaténation simple ou format %
                    nom_bouton = "Test %s" % piste.nom
                    btn = QPushButton(nom_bouton)
                    
                    btn.clicked.connect(lambda _, index=i: self.sequenceur_core.jouer_piste_test(index))
                    pistes_grid.addWidget(btn, i + 1, 1)

                    # 3. Case pour muter une piste
                    mute_box = QCheckBox("Mute")
                    # de couleur rouge
                    mute_box.setStyleSheet("color: #ff5555;") 
                    
                    # Connexion : Change la variable 'is_mute' de la piste quand on coche
                    mute_box.toggled.connect(lambda checked, p=piste: setattr(p, 'is_mute', checked))
                    
                    pistes_grid.addWidget(mute_box, i + 1, 2)
                    
        
        #Contrôle du volume (prototype)
        
        # Bouton pour mettre le volume à 50%
        btn_vol_low = QPushButton("Volume 50%")
        # On passe par sequenceur_core -> moteur_audio
        btn_vol_low.clicked.connect(lambda: self.sequenceur_core.moteur_audio.set_volume(0.5))
        main_layout.addWidget(btn_vol_low)

        # Bouton pour remettre le volume à 100%
        btn_vol_high = QPushButton("Volume 100%")
        btn_vol_high.clicked.connect(lambda: self.sequenceur_core.moteur_audio.set_volume(1.0))
        main_layout.addWidget(btn_vol_high)

        # Ajout d'un bouton de contrôle général
        main_layout.addWidget(QPushButton("Lecture/Stop Global (à implémenter en Décembre)"))