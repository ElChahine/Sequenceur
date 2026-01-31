from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QWidget, QVBoxLayout, 
    QGridLayout, QLabel, QCheckBox, QHBoxLayout, QFrame,
    QSlider
)
from PySide6.QtCore import Qt, QTimer

class FenetrePrincipale(QMainWindow):
    """
    Interface graphique principale de l'application.
    Gère l'affichage de la grille de pattern, les contrôles utilisateur et le timer de lecture.
    """

    def __init__(self, sequenceur_core_instance):
        super().__init__() 
        self.setWindowTitle("Séquenceur Python")
        self.setGeometry(100, 100, 1000, 450)
        self.sequenceur_core = sequenceur_core_instance
        
        # --- Timer de lecture (Métronome) ---
        self.timer = QTimer()
        self.bpm_actuel = 120
        self.update_timer_interval()
        self.timer.timeout.connect(self.boucle_de_lecture)
        self.est_en_lecture = False

        # Matrice stockant les références vers les widgets QCheckBox
        self.matrice_cases = [] 

        # --- Initialisation UI ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # En-tête
        main_layout.addWidget(QLabel("SÉQUENCEUR"), alignment=Qt.AlignmentFlag.AlignCenter)

        # Grille principale
        pistes_grid = QGridLayout()
        main_layout.addLayout(pistes_grid)
        
        pistes_grid.addWidget(QLabel("PISTES"), 0, 0)
        pistes_grid.addWidget(QLabel("PATTERN (16 Pas)"), 0, 1, Qt.AlignmentFlag.AlignCenter)
        pistes_grid.addWidget(QLabel("CONTRÔLES"), 0, 2)

        # Génération dynamique des pistes
        for i, piste in enumerate(self.sequenceur_core.pistes):
            # Nom de la piste
            label_nom = QLabel(piste.nom)
            label_nom.setStyleSheet("font-weight: bold; font-size: 14px;")
            pistes_grid.addWidget(label_nom, i + 1, 0)
            
            # Conteneur des Steps
            widget_steps = QWidget()
            layout_steps = QHBoxLayout()
            layout_steps.setContentsMargins(0, 0, 0, 0) 
            layout_steps.setSpacing(2)
            widget_steps.setLayout(layout_steps)
            
            ligne_cases = []
            
            for step in range(16):
                case = QCheckBox()
                case.setToolTip(f"Piste {piste.nom} - Pas {step + 1}")
                # Utilisation d'une lambda pour capturer les index i et step
                case.toggled.connect(lambda checked, p=i, s=step: self.sequenceur_core.update_step(p, s, checked))
                
                # Style CSS par défaut
                case.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; border: 1px solid #555; background: #333; } QCheckBox::indicator:checked { background: #00d4ff; }")
                
                layout_steps.addWidget(case)
                ligne_cases.append(case)
            
            self.matrice_cases.append(ligne_cases)
            pistes_grid.addWidget(widget_steps, i + 1, 1)

            # Contrôles par piste (Mute / Solo / Test)
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
        
        # --- Barre de Contrôles Globaux ---
        controls_layout = QHBoxLayout()
        
        # 1. Contrôle du Volume
        controls_layout.addWidget(QLabel("Volume :"))
        self.slider_volume = QSlider(Qt.Orientation.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(100)
        self.slider_volume.setFixedWidth(150)
        self.slider_volume.valueChanged.connect(self.changer_volume)
        controls_layout.addWidget(self.slider_volume)
        self.label_vol_text = QLabel("100%")
        self.label_vol_text.setFixedWidth(40)
        controls_layout.addWidget(self.label_vol_text)
        
        controls_layout.addSpacing(30)

        # 2. Contrôle du BPM (Tempo)
        controls_layout.addWidget(QLabel("Tempo :"))
        self.slider_bpm = QSlider(Qt.Orientation.Horizontal)
        self.slider_bpm.setRange(60, 200)
        self.slider_bpm.setValue(120)
        self.slider_bpm.setFixedWidth(150)
        self.slider_bpm.valueChanged.connect(self.changer_bpm)
        controls_layout.addWidget(self.slider_bpm)
        
        self.label_bpm_text = QLabel("120 BPM")
        self.label_bpm_text.setFixedWidth(60)
        controls_layout.addWidget(self.label_bpm_text)

        controls_layout.addStretch()

        # 3. Contrôle de lecture
        self.btn_play_loop = QPushButton("LECTURE ▶")
        self.btn_play_loop.setFixedWidth(200)
        self.btn_play_loop.setStyleSheet("background-color: #00d4ff; color: black; font-weight: bold; padding: 10px; border-radius: 5px;")
        self.btn_play_loop.clicked.connect(self.toggle_lecture)
        controls_layout.addWidget(self.btn_play_loop)
        
        main_layout.addLayout(controls_layout)

    # --- Méthodes de gestion ---

    def changer_volume(self, valeur_int):
        """Met à jour le volume global via le moteur audio."""
        self.label_vol_text.setText(f"{valeur_int}%")
        self.sequenceur_core.moteur_audio.set_volume(valeur_int / 100.0)

    def changer_bpm(self, valeur_bpm):
        """Met à jour le BPM et recalcule l'intervalle du timer."""
        self.bpm_actuel = valeur_bpm
        self.label_bpm_text.setText(f"{valeur_bpm} BPM")
        self.sequenceur_core.bpm = valeur_bpm
        self.update_timer_interval()

    def update_timer_interval(self):
        """Calcule l'intervalle en ms pour une double-croche (1/4 de temps)."""
        if self.bpm_actuel > 0:
            # Formule: 60000ms / BPM / 4 steps par mesure
            ms = int(60000 / self.bpm_actuel / 4)
            self.timer.setInterval(ms)

    def toggle_lecture(self):
        """Active ou désactive le timer de lecture."""
        if self.est_en_lecture:
            self.timer.stop()
            self.est_en_lecture = False
            self.btn_play_loop.setText("LECTURE ▶")
            self.btn_play_loop.setStyleSheet("background-color: #00d4ff; color: black; font-weight: bold; padding: 10px; border-radius: 5px;")
            self.reset_visuel()
        else:
            self.timer.start()
            self.est_en_lecture = True
            self.btn_play_loop.setText("STOP ■")
            self.btn_play_loop.setStyleSheet("background-color: #ff5555; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")

    def boucle_de_lecture(self):
        """Cycle principal appelé par le timer."""
        step = self.sequenceur_core.step_actuel
        self.update_visuel_step(step)
        self.sequenceur_core.jouer_step_actuel()
        self.sequenceur_core.pas_suivant()

    def update_visuel_step(self, step_actif):
        """Met à jour le style des cases pour indiquer le curseur de lecture."""
        for i_piste in range(len(self.matrice_cases)):
            for i_step in range(16):
                case = self.matrice_cases[i_piste][i_step]
                if i_step == step_actif:
                    # Style pour la colonne active (Curseur)
                    if case.isChecked():
                        case.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; border: 2px solid white; background: #00ffff; }")
                    else:
                        case.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; border: 2px solid white; background: #666; }")
                else:
                    # Style par défaut
                    if case.isChecked():
                        case.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; border: 1px solid #555; background: #00d4ff; }")
                    else:
                        case.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; border: 1px solid #555; background: #333; }")

    def reset_visuel(self):
        """Réinitialise l'affichage visuel lors de l'arrêt."""
        for ligne in self.matrice_cases:
            for case in ligne:
                 if case.isChecked():
                    case.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; border: 1px solid #555; background: #00d4ff; }")
                 else:
                    case.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; border: 1px solid #555; background: #333; }")