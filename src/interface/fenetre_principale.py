# src/interface/fenetre_principale.py
import json
import soundfile as sf
from interface.style import THEME_SOMBRE
from interface.timeline import TimelineWidget
from interface.panneau_controles import PanneauControlesWidget
from sequenceur.persistance import ProjectPersistenceManager

from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QWidget, QVBoxLayout, 
    QGridLayout, QLabel, QCheckBox, QHBoxLayout, 
    QScrollArea, QFileDialog
)
from PySide6.QtCore import Qt, QTimer


class FenetrePrincipale(QMainWindow):
    """
    La fenêtre principale de l'application qui rassemble la grille, 
    les boutons de fichiers et connecte le tout au coeur du code.
    """
    def __init__(self, sequenceur_core_instance):
        """
        Initialise l'interface, crée les boutons du haut, la zone 
        de défilement pour la grille et le panneau du bas.
        """
        super().__init__()
        self.setStyleSheet(THEME_SOMBRE)
        self.setWindowTitle("Séquenceur Python")
        self.setGeometry(100, 100, 1000, 500)
        self.sequenceur_core = sequenceur_core_instance
        
        self.timer = QTimer()
        self.bpm_actuel = 120
        self.update_timer_interval()
        self.timer.timeout.connect(self.boucle_de_lecture)
        self.est_en_lecture = False

        self.matrice_cases = [] 
        self.liste_mute_boxes = []
        self.liste_labels_nom = []

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        file_layout = QHBoxLayout()
        btn_save = QPushButton("Sauvegarder Projet")
        btn_save.clicked.connect(self.sauvegarder_projet)
        file_layout.addWidget(btn_save)

        btn_load = QPushButton("Charger Projet")
        btn_load.clicked.connect(self.charger_projet)
        file_layout.addWidget(btn_load)
        
        btn_export = QPushButton("Exporter WAV")
        btn_export.clicked.connect(self.exporter_wav)
        file_layout.addWidget(btn_export)
        
        file_layout.addStretch()
        main_layout.addLayout(file_layout)
        
        lbl_titre = QLabel("SÉQUENCEUR")
        main_layout.addWidget(
            lbl_titre, alignment=Qt.AlignmentFlag.AlignCenter
        )

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedHeight(350)
        
        self.container_grille = QWidget()
        pistes_grid = QGridLayout(self.container_grille)
        self.scroll_area.setWidget(self.container_grille)
       
        main_layout.addWidget(self.scroll_area)
        
        pistes_grid.addWidget(QLabel("PISTES"), 0, 0)
        pistes_grid.addWidget(QLabel("CONTRÔLES"), 0, 2)

        self.timeline = TimelineWidget(self)
        pistes_grid.addWidget(self.timeline, 0, 1)

        for i, piste in enumerate(self.sequenceur_core.pistes):
            widget_nom = QWidget()
            layout_nom = QHBoxLayout(widget_nom)
            label_nom = QLabel(piste.nom)
            label_nom.setStyleSheet("font-weight: bold; font-size: 14px;")
            self.liste_labels_nom.append(label_nom)
            layout_nom.addWidget(label_nom)
            
            btn_charger_son = QPushButton("📂")
            btn_charger_son.setFixedWidth(30)
            btn_charger_son.clicked.connect(
                lambda _, idx=i, lbl=label_nom: (
                    self.choisir_nouveau_sample(idx, lbl)
                )
            )
            layout_nom.addWidget(btn_charger_son)
            pistes_grid.addWidget(widget_nom, i + 1, 0)
            
            widget_steps = QWidget()
            layout_steps = QHBoxLayout(widget_steps)
            layout_steps.setSpacing(2)
            
            ligne_cases = []
            for step in range(64):
                case = QCheckBox()
                case.setToolTip(f"Pas {step + 1}")
                case.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                case.toggled.connect(
                    lambda checked, p=i, s=step: (
                        self.case_cliquee(checked, p, s)
                    )
                )
                layout_steps.addWidget(case)
                ligne_cases.append(case)
            
            self.matrice_cases.append(ligne_cases)
            pistes_grid.addWidget(widget_steps, i + 1, 1)

            widget_controles = QWidget()
            layout_controles = QHBoxLayout(widget_controles)
            mute_box = QCheckBox("Mute")
            mute_box.toggled.connect(
                lambda checked, p=piste: setattr(p, 'is_mute', checked)
            )
            self.liste_mute_boxes.append(mute_box)
            layout_controles.addWidget(mute_box)
            
            btn_test = QPushButton("Test")
            btn_test.clicked.connect(
                lambda _, index=i: (
                    self.sequenceur_core.jouer_piste_test(index)
                )
            )
            layout_controles.addWidget(btn_test)
            pistes_grid.addWidget(widget_controles, i + 1, 2)

        main_layout.addSpacing(20) 
        
        self.panneau_controles = PanneauControlesWidget(self)
        main_layout.addWidget(self.panneau_controles)

    def choisir_nouveau_sample(self, index_piste, label_nom_widget):
        """
        Ouvre une fenêtre pour chercher un fichier WAV et l'attribuer 
        à la piste sélectionnée.
        """
        chemin_fichier, _ = QFileDialog.getOpenFileName(
            self, "Choisir un sample audio", "", "Fichiers WAV (*.wav)"
        )
        if chemin_fichier:
            core = self.sequenceur_core
            nouveau_nom = core.changer_sample_piste(
                index_piste, chemin_fichier
            )
            if nouveau_nom:
                label_nom_widget.setText(nouveau_nom)

    def sauvegarder_projet(self):
        """
        Ouvre une boîte de dialogue pour enregistrer le rythme 
        actuel dans un fichier JSON.
        """
        chemin_fichier, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder le projet", "", "JSON Files (*.json)"
        )
        if chemin_fichier:
            if not chemin_fichier.endswith(".json"):
                chemin_fichier += ".json"
            try:
                ProjectPersistenceManager.sauvegarder_projet(
                    chemin_fichier, self.sequenceur_core
                )
                print(f"Projet sauvegardé dans {chemin_fichier}")
            except Exception as e:
                print(f"Erreur lors de la sauvegarde : {e}")

    def charger_projet(self):
        """
        Permet de sélectionner un fichier JSON de sauvegarde pour 
        charger le morceau et remettre à jour tous les boutons.
        """
        chemin_fichier, _ = QFileDialog.getOpenFileName(
            self, "Charger un projet", "", "JSON Files (*.json)"
        )
        if chemin_fichier:
            try:
                ProjectPersistenceManager.charger_projet(
                    chemin_fichier, self.sequenceur_core
                )
                
                core = self.sequenceur_core
                moteur = core.moteur_audio
                panneau = self.panneau_controles
                
                panneau.slider_bpm.setValue(core.bpm)
                panneau.slider_volume.setValue(
                    int(moteur.volume_global * 100)
                )
                panneau.slider_delay.setValue(
                    int(moteur.intensite_delay * 100)
                )
                panneau.slider_filtre.setValue(
                    int(moteur.intensite_filtre * 100)
                )
                
                for i_piste in range(len(core.pistes)):
                    self.liste_labels_nom[i_piste].setText(
                        core.pistes[i_piste].nom
                    )
                    self.liste_mute_boxes[i_piste].setChecked(
                        core.pistes[i_piste].is_mute
                    )
                    for i_step in range(64):
                        etat_step = core.pistes[i_piste].pattern[i_step]
                        case = self.matrice_cases[i_piste][i_step]
                        
                        case.blockSignals(True)
                        case.setChecked(etat_step)
                        case.blockSignals(False)

                print(f"Projet chargé depuis {chemin_fichier}")
            except Exception as e:
                print(f"Erreur lors du chargement : {e}")

    def changer_volume(self, valeur_int):
        """
        Met à jour le texte du pourcentage du volume et change la 
        valeur du volume général dans le moteur audio.
        """
        self.panneau_controles.label_vol_text.setText(f"{valeur_int}%")
        self.sequenceur_core.moteur_audio.set_volume(valeur_int / 100.0)

    def changer_bpm(self, valeur_bpm):
        """
        Change la vitesse (BPM), ajuste le texte et règle la vitesse 
        du timer de lecture.
        """
        self.bpm_actuel = valeur_bpm
        self.panneau_controles.label_bpm_text.setText(
            f"{valeur_bpm} BPM"
        )
        self.sequenceur_core.bpm = valeur_bpm
        self.update_timer_interval()

    def update_timer_interval(self):
        """
        Calcule le nombre de millisecondes entre chaque pas selon 
        le tempo configuré.
        """
        if self.bpm_actuel > 0:
            ms = int(60000 / self.bpm_actuel / 4)
            self.timer.setInterval(ms)

    def toggle_lecture(self):
        """
        Gère le bouton de lecture pour lancer ou arrêter la musique 
        et change la couleur du bouton.
        """
        panneau = self.panneau_controles
        if self.est_en_lecture:
            self.timer.stop()
            self.est_en_lecture = False
            panneau.btn_play_loop.setText("LECTURE ▶")
            style_play = (
                "background-color: #00d4ff; color: black; "
                "font-weight: bold; padding: 10px; border-radius: 5px;"
            )
            panneau.btn_play_loop.setStyleSheet(style_play)
            self.reset_visuel()
        else:
            self.timer.start()
            self.est_en_lecture = True
            panneau.btn_play_loop.setText("STOP ■")
            style_stop = (
                "background-color: #ff5555; color: white; "
                "font-weight: bold; padding: 10px; border-radius: 5px;"
            )
            panneau.btn_play_loop.setStyleSheet(style_stop)

    def boucle_de_lecture(self):
        """
        Fonction appelée à chaque pas par le timer pour faire avancer 
        le curseur graphique et déclencher les sons.
        """
        step = self.sequenceur_core.step_actuel
        self.update_visuel_step(step)
        self.sequenceur_core.jouer_step_actuel()
        self.sequenceur_core.pas_suivant()

    def update_visuel_step(self, step_actif):
        """
        Allume la colonne de la grille correspondant au pas en train 
        d'être joué en changeant sa propriété Qt.
        """
        for i_piste in range(len(self.matrice_cases)):
            for i_step in range(64):
                case = self.matrice_cases[i_piste][i_step]
                est_etape_active = (i_step == step_actif)
                case.setProperty("actif", est_etape_active)
                case.style().unpolish(case)
                case.style().polish(case)

    def reset_visuel(self):
        """
        Éteint toutes les lumières du curseur de lecture sur la grille.
        """
        for ligne in self.matrice_cases:
            for case in ligne:
                case.setProperty("actif", False)
                case.style().unpolish(case)
                case.style().polish(case)
        
    def exporter_wav(self):
        """
        Génère le fichier audio final (.wav) de notre grille en 
        faisant appel au module d'exportation.
        """
        chemin_fichier, _ = QFileDialog.getSaveFileName(
            self, "Exporter la boucle", "ma_composition.wav", 
            "WAV Files (*.wav)"
        )
        if chemin_fichier:
            try:
                core = self.sequenceur_core
                data_audio = core.generer_rendu_audio(
                    nb_boucles=4
                )
                sf.write(chemin_fichier, data_audio, 44100)
                print(f"Exportation réussie : {chemin_fichier}")
            except Exception as e:
                print(f"Erreur lors de l'exportation : {e}")
                
    def changer_intensite_delay(self, valeur_int):
        """
        Met à jour la valeur et le pourcentage de l'effet delay.
        """
        panneau = self.panneau_controles
        panneau.label_delay_text.setText(f"{valeur_int}%")
        moteur = self.sequenceur_core.moteur_audio
        moteur.intensite_delay = valeur_int / 100.0
        
    def changer_intensite_filtre(self, valeur_int):
        """
        Met à jour la valeur et le pourcentage du filtre passe-bas.
        """
        panneau = self.panneau_controles
        panneau.label_filtre_text.setText(f"{valeur_int}%")
        moteur = self.sequenceur_core.moteur_audio
        moteur.intensite_filtre = valeur_int / 100.0
        
    def keyPressEvent(self, event):
        """
        Permet de lancer ou stopper la lecture avec la touche espace.
        """
        if event.key() == Qt.Key.Key_Space:
            self.toggle_lecture()
        else:
            super().keyPressEvent(event)
            
    def sauter_au_pas(self, index_step):
        """
        Permet de forcer le curseur à aller sur un pas spécifique.
        """
        self.sequenceur_core.step_actuel = index_step
        self.update_visuel_step(index_step)
        
    def case_cliquee(self, checked, index_piste, index_step):
        """
        Enregistre le choix de la case cliquée dans le coeur et 
        joue un petit son de prévisualisation si on n'est pas en lecture.
        """
        self.sequenceur_core.update_step(
            index_piste, index_step, checked
        )
        if checked and not self.est_en_lecture:
            piste = self.sequenceur_core.pistes[index_piste]
            self.sequenceur_core.moteur_audio.jouer_mix(
                [piste.sample_path]
            )