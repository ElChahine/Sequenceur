from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QWidget, QVBoxLayout, 
    QGridLayout, QLabel, QCheckBox, QHBoxLayout
)
from PySide6.QtCore import Qt, QTimer  # <--- AJOUT IMPORTANT : QTimer

class FenetrePrincipale(QMainWindow):
    """
    Fenêtre principale de l'application (GUI).
    Version : Décembre Finale (Lecture en Boucle)
    """

    def __init__(self, sequenceur_core_instance):
        super().__init__() 
        self.setWindowTitle("Séquenceur Python - Décembre (Final)")
        self.setGeometry(100, 100, 850, 400)
        self.sequenceur_core = sequenceur_core_instance
        
        # --- TIMER (Le Métronome) ---
        self.timer = QTimer()
        # Calcul du temps en ms pour 120 BPM (4 steps par temps)
        # 60 sec / 120 BPM / 4 = 0.125 sec = 125 ms
        self.timer.setInterval(125) 
        self.timer.timeout.connect(self.boucle_de_lecture)
        self.est_en_lecture = False

        # --- UI ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        pistes_grid = QGridLayout()
        main_layout.addLayout(pistes_grid)
        
        pistes_grid.addWidget(QLabel("PISTES"), 0, 0)
        pistes_grid.addWidget(QLabel("PATTERN (16 Steps)"), 0, 1, Qt.AlignmentFlag.AlignCenter)
        pistes_grid.addWidget(QLabel("CONTRÔLES"), 0, 2)

        for i, piste in enumerate(self.sequenceur_core.pistes):
            # Nom
            label_nom = QLabel(piste.nom)
            label_nom.setStyleSheet("font-weight: bold; font-size: 14px;")
            pistes_grid.addWidget(label_nom, i + 1, 0)
            
            # Steps
            widget_steps = QWidget()
            layout_steps = QHBoxLayout()
            layout_steps.setContentsMargins(0, 0, 0, 0) 
            widget_steps.setLayout(layout_steps)
            
            for step in range(16):
                case = QCheckBox()
                case.setToolTip("Pas %d" % (step + 1))
                case.toggled.connect(lambda checked, p=i, s=step: self.sequenceur_core.update_step(p, s, checked))
                layout_steps.addWidget(case)
            
            pistes_grid.addWidget(widget_steps, i + 1, 1)

            # Contrôles
            widget_controles = QWidget()
            layout_controles = QHBoxLayout()
            layout_controles.setContentsMargins(0, 0, 0, 0)
            widget_controles.setLayout(layout_controles)
            
            mute_box = QCheckBox("Mute")
            mute_box.setStyleSheet("color: #ff5555;") 
            mute_box.toggled.connect(lambda checked, p=piste: setattr(p, 'is_mute', checked))
            layout_controles.addWidget(mute_box)

            btn_test = QPushButton("Test")
            btn_test.setFixedWidth(50) 
            btn_test.clicked.connect(lambda _, index=i: self.sequenceur_core.jouer_piste_test(index))
            layout_controles.addWidget(btn_test)

            pistes_grid.addWidget(widget_controles, i + 1, 2)

        main_layout.addSpacing(20) 
        
        # Volume
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volume Global :"))
        btn_vol_low = QPushButton("50%")
        btn_vol_low.clicked.connect(lambda: self.sequenceur_core.moteur_audio.set_volume(0.5))
        volume_layout.addWidget(btn_vol_low)
        btn_vol_high = QPushButton("100%")
        btn_vol_high.clicked.connect(lambda: self.sequenceur_core.moteur_audio.set_volume(1.0))
        volume_layout.addWidget(btn_vol_high)
        volume_layout.addStretch() 
        main_layout.addLayout(volume_layout)

        # Bouton play
        self.btn_play_loop = QPushButton("LECTURE ▶")
        self.btn_play_loop.setStyleSheet("""
            QPushButton {
                background-color: #00d4ff; 
                color: black; 
                font-weight: bold; 
                padding: 15px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #55e4ff; }
        """)
        # Connexion à la fonction toggle_lecture
        self.btn_play_loop.clicked.connect(self.toggle_lecture)
        main_layout.addWidget(self.btn_play_loop)

    def toggle_lecture(self):
        """Active ou désactive le Timer"""
        if self.est_en_lecture:
            # On stoppe
            self.timer.stop()
            self.est_en_lecture = False
            self.btn_play_loop.setText("LECTURE ▶")
            self.btn_play_loop.setStyleSheet("background-color: #00d4ff; color: black; font-weight: bold; padding: 15px; font-size: 16px; border-radius: 5px;")
        else:
            # On démarre
            self.timer.start()
            self.est_en_lecture = True
            self.btn_play_loop.setText("STOP ■")
            self.btn_play_loop.setStyleSheet("background-color: #ff5555; color: white; font-weight: bold; padding: 15px; font-size: 16px; border-radius: 5px;")

    def boucle_de_lecture(self):
        """
        Cette fonction est appelée automatiquement toutes les 125ms.
        Elle orchestre le séquenceur.
        """
        # 1. Jouer les sons du pas actuel
        self.sequenceur_core.jouer_step_actuel()
        
        # 2. Passer au pas suivant pour la prochaine fois
        self.sequenceur_core.pas_suivant()