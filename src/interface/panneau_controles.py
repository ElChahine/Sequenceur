# src/interface/panneau_controles.py
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QSlider, QPushButton
)
from PySide6.QtCore import Qt

class PanneauControlesWidget(QWidget):
    """
    Le panneau du bas qui regroupe tous les sliders pour gérer 
    le volume, le tempo, les effets et le gros bouton de lecture.
    """
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.core = parent_window.sequenceur_core
        
        layout = QHBoxLayout(self)
        
        layout.addWidget(QLabel("Volume :"))
        self.slider_volume = QSlider(Qt.Orientation.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(100)
        self.slider_volume.setFixedWidth(150)
        self.slider_volume.valueChanged.connect(
            self.parent_window.changer_volume
        )
        layout.addWidget(self.slider_volume)
        
        self.label_vol_text = QLabel("100%")
        self.label_vol_text.setFixedWidth(40)
        layout.addWidget(self.label_vol_text)
        
        layout.addSpacing(30)
        layout.addWidget(QLabel("Tempo :"))
        self.slider_bpm = QSlider(Qt.Orientation.Horizontal)
        self.slider_bpm.setRange(60, 200)
        self.slider_bpm.setValue(120)
        self.slider_bpm.setFixedWidth(150)
        self.slider_bpm.valueChanged.connect(
            self.parent_window.changer_bpm
        )
        layout.addWidget(self.slider_bpm)
        
        self.label_bpm_text = QLabel("120 BPM")
        self.label_bpm_text.setFixedWidth(60)
        layout.addWidget(self.label_bpm_text)
        
        layout.addSpacing(30)
        layout.addWidget(QLabel("Effet Delay :"))
        self.slider_delay = QSlider(Qt.Orientation.Horizontal)
        self.slider_delay.setRange(0, 80)
        self.slider_delay.setValue(0)
        self.slider_delay.setFixedWidth(120)
        self.slider_delay.valueChanged.connect(
            self.parent_window.changer_intensite_delay
        )
        layout.addWidget(self.slider_delay)
        
        self.label_delay_text = QLabel("0%")
        self.label_delay_text.setFixedWidth(40)
        layout.addWidget(self.label_delay_text)
        
        layout.addSpacing(30)
        layout.addWidget(QLabel("Filtre Passe-Bas :"))
        self.slider_filtre = QSlider(Qt.Orientation.Horizontal)
        self.slider_filtre.setRange(0, 100)
        self.slider_filtre.setValue(0)
        self.slider_filtre.setFixedWidth(120)
        self.slider_filtre.valueChanged.connect(
            self.parent_window.changer_intensite_filtre
        )
        layout.addWidget(self.slider_filtre)
        
        self.label_filtre_text = QLabel("0%")
        self.label_filtre_text.setFixedWidth(40)
        layout.addWidget(self.label_filtre_text)
        
        layout.addStretch()
        
        self.btn_play_loop = QPushButton("LECTURE ▶")
        self.btn_play_loop.setFixedWidth(200)
        style_play = (
            "background-color: #00d4ff; color: black; "
            "font-weight: bold; padding: 10px; border-radius: 5px;"
        )
        self.btn_play_loop.setStyleSheet(style_play)
        self.btn_play_loop.clicked.connect(
            self.parent_window.toggle_lecture
        )
        layout.addWidget(self.btn_play_loop)