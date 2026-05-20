# src/sequenceur/dsp.py
import numpy as np

class DelayEffect:
    """
    Classe pour gérer l'effet d'écho (delay) sur un son.
    """
    def __init__(self, temps_ms=220, feedback=0.0):
        """
        Initialise le temps en ms et le feedback entre 0.0 et 1.0.
        """
        self.temps_ms = temps_ms
        self.feedback = feedback

    def appliquer(self, signal):
        """
        Prend le signal de base, lui ajoute de l'écho selon le
        feedback configuré et renvoie le tableau de données modifié.
        """
        if self.feedback <= 0:
            return signal
            
        nb_samples_delay = int((self.temps_ms / 1000.0) * 44100)
        signal_traite = np.zeros(len(signal) + nb_samples_delay)
        signal_traite[:len(signal)] = signal
        
        echo = signal * self.feedback
        fin = nb_samples_delay + len(signal)
        signal_traite[nb_samples_delay:fin] += echo
        
        return np.clip(signal_traite, -1.0, 1.0)


class LowPassFilterEffect:
    """
    Classe pour gérer le filtre passe-bas qui étouffe les aigus.
    """
    def __init__(self, intensite=0.0):
        """
        Initialise le filtre avec une intensité entre 0.0 et 1.0.
        """
        self.intensite = intensite

    def appliquer(self, data):
        """
        Prend le signal data en entrée, lui applique le lissage pour
        couper les fréquences aiguës et retourne le signal filtré.
        """
        if self.intensite <= 0: 
            return data
            
        out = np.zeros_like(data)
        alpha = (1.0 - self.intensite) ** 3
        
        if alpha < 0.01:
            alpha = 0.01
            
        val_precedente = 0
        for i in range(len(data)):
            out[i] = alpha * data[i] + (1 - alpha) * val_precedente
            val_precedente = out[i]
            
        return out