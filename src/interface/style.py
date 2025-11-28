THEME_SOMBRE = """
    /* Fond général de la fenêtre */
    QMainWindow, QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
    }

    /* Style des textes (Labels) */
    QLabel {
        color: #e0e0e0;
        font-size: 14px;
        font-weight: bold;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Style des boutons par défaut */
    QPushButton {
        background-color: #3d3d3d;
        color: #00d4ff; /* Bleu cyan "Techno" */
        border: 1px solid #555;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 13px;
    }

    /* Quand on passe la souris sur un bouton */
    QPushButton:hover {
        background-color: #505050;
        border: 1px solid #00d4ff;
    }

    /* Quand on clique sur un bouton */
    QPushButton:pressed {
        background-color: #00d4ff;
        color: #000000;
    }
    
    /* Style pour la case à cocher (si tu l'ajoutes plus tard) */
    QCheckBox {
        color: #ff5555;
        spacing: 5px;
    }
    QCheckBox::indicator {
        width: 15px;
        height: 15px;
    }
"""