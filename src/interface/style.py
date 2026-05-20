THEME_SOMBRE = """
    /* Fond général de la fenêtre */
    QMainWindow, QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
    }

    /* Style des textes*/
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
    
    /* État normal de toutes les cases à l'arrêt ou hors curseur */
    QCheckBox::indicator { 
        width: 18px; 
        height: 18px; 
        border: 1px solid #555; 
        background: #333; 
    }
    QCheckBox::indicator:checked { 
        background: #00d4ff; 
    }

    /* État lorsque la case est sur le pas actif (Curseur de lecture) */
    QCheckBox[actif="true"]::indicator {
        border: 2px solid white;
        background: #666;
    }
    QCheckBox[actif="true"]::indicator:checked {
        border: 2px solid white;
        background: #00ffff;
    }
    
    QPushButton#btn_timeline {
        background-color: #222;
        color: #888;
        border: none;
        font-size: 9px;
        font-weight: bold;
    }
    QPushButton#btn_timeline:hover {
        background-color: #00d4ff;
        color: black;
    }
"""