# src/interface/timeline.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt

class TimelineWidget(QWidget):
    """
    Le petit bandeau du haut qui affiche les numéros des pas 
    et permet de cliquer pour sauter directement à un endroit.
    """
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        layout = QHBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)

        for step in range(64):
            texte = str((step // 4) + 1) if step % 4 == 0 else "."
            btn_time = QPushButton(texte)
            btn_time.setFixedWidth(18)
            btn_time.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn_time.setObjectName("btn_timeline")
            btn_time.clicked.connect(
                lambda _, s=step: (
                    self.parent_window.sauter_au_pas(s)
                )
            )
            layout.addWidget(btn_time)