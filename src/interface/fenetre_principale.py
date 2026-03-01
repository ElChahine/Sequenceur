import json
from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QWidget, QVBoxLayout, 
    QGridLayout, QLabel, QCheckBox, QHBoxLayout, QSlider, QFileDialog
)
from PySide6.QtCore import Qt, QTimer

class FenetrePrincipale(QMainWindow):
    """
    Interface graphique principale de l'application.
    Version Mars : Ajout de l'import de samples personnalisés.
    """

    def __init__(self, sequenceur_core_instance):
        super().__init__() 
        self.setWindowTitle("Séquenceur Python - Mars")
        self.setGeometry(100, 100, 1000, 500)
        self.sequenceur_core = sequenceur_core_instance
        
        self.timer = QTimer()
        self.bpm_actuel = 120
        self.update_timer_interval()
        self.timer.timeout.connect(self.boucle_de_lecture)
        self.est_en_lecture = False

        self.matrice_cases = [] 
        self.liste_mute_boxes = []
        self.liste_labels_nom = [] # Pour pouvoir changer les noms des pistes (Nouveau)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        file_layout = QHBoxLayout()
        btn_save = QPushButton("💾 Sauvegarder Projet")
        btn_save.clicked.connect(self.sauvegarder_projet)
        file_layout.addWidget(btn_save)

        btn_load = QPushButton("📂 Charger Projet")
        btn_load.clicked.connect(self.charger_projet)
        file_layout.addWidget(btn_load)
        
        file_layout.addStretch()
        main_layout.addLayout(file_layout)
        
        main_layout.addWidget(QLabel("SÉQUENCEUR"), alignment=Qt.AlignmentFlag.AlignCenter)

        pistes_grid = QGridLayout()
        main_layout.addLayout(pistes_grid)
        
        pistes_grid.addWidget(QLabel("PISTES"), 0, 0)
        pistes_grid.addWidget(QLabel("PATTERN (16 Pas)"), 0, 1, Qt.AlignmentFlag.AlignCenter)
        pistes_grid.addWidget(QLabel("CONTRÔLES"), 0, 2)

        for i, piste in enumerate(self.sequenceur_core.pistes):
            
            widget_nom = QWidget()
            layout_nom = QHBoxLayout(widget_nom)
            layout_nom.setContentsMargins(0, 0, 0, 0)
            
            label_nom = QLabel(piste.nom)
            label_nom.setStyleSheet("font-weight: bold; font-size: 14px;")
            self.liste_labels_nom.append(label_nom)
            layout_nom.addWidget(label_nom)
            
            btn_charger_son = QPushButton("📂")
            btn_charger_son.setFixedWidth(30)
            btn_charger_son.setToolTip("Remplacer le sample de cette piste")
            btn_charger_son.clicked.connect(lambda _, idx=i, lbl=label_nom: self.choisir_nouveau_sample(idx, lbl))
            layout_nom.addWidget(btn_charger_son)
            
            pistes_grid.addWidget(widget_nom, i + 1, 0)
            
            
            widget_steps = QWidget()
            layout_steps = QHBoxLayout()
            layout_steps.setContentsMargins(0, 0, 0, 0) 
            layout_steps.setSpacing(2)
            widget_steps.setLayout(layout_steps)
            
            ligne_cases = []
            for step in range(16):
                case = QCheckBox()
                case.setToolTip(f"Pas {step + 1}")
                case.toggled.connect(lambda checked, p=i, s=step: self.sequenceur_core.update_step(p, s, checked))
                case.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; border: 1px solid #555; background: #333; } QCheckBox::indicator:checked { background: #00d4ff; }")
                layout_steps.addWidget(case)
                ligne_cases.append(case)
            
            self.matrice_cases.append(ligne_cases)
            pistes_grid.addWidget(widget_steps, i + 1, 1)

            widget_controles = QWidget()
            layout_controles = QHBoxLayout()
            layout_controles.setContentsMargins(0, 0, 0, 0)
            widget_controles.setLayout(layout_controles)
            
            mute_box = QCheckBox("Mute")
            mute_box.setStyleSheet("color: #ff5555;") 
            mute_box.toggled.connect(lambda checked, p=piste: setattr(p, 'is_mute', checked))
            self.liste_mute_boxes.append(mute_box)
            layout_controles.addWidget(mute_box)

            btn_test = QPushButton("Test")
            btn_test.setFixedWidth(50) 
            btn_test.clicked.connect(lambda _, index=i: self.sequenceur_core.jouer_piste_test(index))
            layout_controles.addWidget(btn_test)

            pistes_grid.addWidget(widget_controles, i + 1, 2)

        main_layout.addSpacing(20) 
        
    
        controls_layout = QHBoxLayout()
        
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

        self.btn_play_loop = QPushButton("LECTURE ▶")
        self.btn_play_loop.setFixedWidth(200)
        self.btn_play_loop.setStyleSheet("background-color: #00d4ff; color: black; font-weight: bold; padding: 10px; border-radius: 5px;")
        self.btn_play_loop.clicked.connect(self.toggle_lecture)
        controls_layout.addWidget(self.btn_play_loop)
        
        main_layout.addLayout(controls_layout)


    def choisir_nouveau_sample(self, index_piste, label_nom_widget):
        """Ouvre un dialogue pour choisir un nouveau fichier .wav pour la piste."""
        chemin_fichier, _ = QFileDialog.getOpenFileName(self, "Choisir un sample audio", "", "Fichiers WAV (*.wav)")
        if chemin_fichier:
            nouveau_nom = self.sequenceur_core.changer_sample_piste(index_piste, chemin_fichier)
            if nouveau_nom:
                label_nom_widget.setText(nouveau_nom)


    def sauvegarder_projet(self):
        chemin_fichier, _ = QFileDialog.getSaveFileName(self, "Sauvegarder le projet", "", "JSON Files (*.json)")
        if chemin_fichier:
            if not chemin_fichier.endswith(".json"):
                chemin_fichier += ".json"
            donnees = self.sequenceur_core.exporter_donnees()
            try:
                with open(chemin_fichier, 'w') as f:
                    json.dump(donnees, f, indent=4)
                print(f"Projet sauvegardé avec succès dans {chemin_fichier}")
            except Exception as e:
                print(f"Erreur lors de la sauvegarde : {e}")

    def charger_projet(self):
        chemin_fichier, _ = QFileDialog.getOpenFileName(self, "Charger un projet", "", "JSON Files (*.json)")
        if chemin_fichier:
            try:
                with open(chemin_fichier, 'r') as f:
                    donnees = json.load(f)
                
                self.sequenceur_core.importer_donnees(donnees)
                
                self.slider_bpm.setValue(self.sequenceur_core.bpm)
                self.slider_volume.setValue(int(self.sequenceur_core.moteur_audio.volume_global * 100))
                
                for i_piste in range(len(self.sequenceur_core.pistes)):
                    # Mise à jour du nom de la piste qui aurait pu changer
                    self.liste_labels_nom[i_piste].setText(self.sequenceur_core.pistes[i_piste].nom)
                    self.liste_mute_boxes[i_piste].setChecked(self.sequenceur_core.pistes[i_piste].is_mute)
                    for i_step in range(16):
                        etat_step = self.sequenceur_core.pistes[i_piste].pattern[i_step]
                        self.matrice_cases[i_piste][i_step].setChecked(etat_step)

                print(f"Projet chargé avec succès depuis {chemin_fichier}")
            except Exception as e:
                print(f"Erreur lors du chargement : {e}")

    def changer_volume(self, valeur_int):
        self.label_vol_text.setText(f"{valeur_int}%")
        self.sequenceur_core.moteur_audio.set_volume(valeur_int / 100.0)

    def changer_bpm(self, valeur_bpm):
        self.bpm_actuel = valeur_bpm
        self.label_bpm_text.setText(f"{valeur_bpm} BPM")
        self.sequenceur_core.bpm = valeur_bpm
        self.update_timer_interval()

    def update_timer_interval(self):
        if self.bpm_actuel > 0:
            ms = int(60000 / self.bpm_actuel / 4)
            self.timer.setInterval(ms)

    def toggle_lecture(self):
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
        step = self.sequenceur_core.step_actuel
        self.update_visuel_step(step)
        self.sequenceur_core.jouer_step_actuel()
        self.sequenceur_core.pas_suivant()

    def update_visuel_step(self, step_actif):
        for i_piste in range(len(self.matrice_cases)):
            for i_step in range(16):
                case = self.matrice_cases[i_piste][i_step]
                if i_step == step_actif:
                    if case.isChecked():
                        case.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; border: 2px solid white; background: #00ffff; }")
                    else:
                        case.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; border: 2px solid white; background: #666; }")
                else:
                    if case.isChecked():
                        case.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; border: 1px solid #555; background: #00d4ff; }")
                    else:
                        case.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; border: 1px solid #555; background: #333; }")

    def reset_visuel(self):
        for ligne in self.matrice_cases:
            for case in ligne:
                 if case.isChecked():
                    case.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; border: 1px solid #555; background: #00d4ff; }")
                 else:
                    case.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; border: 1px solid #555; background: #333; }")