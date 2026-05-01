# src/sequenceur/moteur_audio.py
import soundfile as sf
import sounddevice as sd
import numpy as np
import os
import queue

class MoteurAudio:
    """
    Gère le flux audio via une architecture asynchrone (Callback).
    Permet le mixage de plusieurs sources sonores en temps réel sans blocage du thread principal.
    """

    def __init__(self):
        """
        Initialise les paramètres audio, le cache des samples et le flux de sortie.
        """
        self.volume_global = 1.0
        self.intensite_delay = 0.0
        self.sample_rate = 44100
        
        # Cache des données audio chargées (Chemin -> numpy.array)
        self.cache_samples = {}
        
        # Liste des sons en cours de lecture
        # Structure : Dictionnaire {'data': array, 'cursor': int}
        self.active_sounds = []
        
        # File thread-safe pour la communication entre le thread principal et le thread audio
        self.command_queue = queue.Queue()

        # Initialisation du flux audio en sortie
        try:
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=1, # Mono pour simplifier le mixage
                callback=self._audio_callback,
                blocksize=512 # Faible latence
            )
            self.stream.start()
            print("MoteurAudio: Stream actif.")
        except Exception as e:
            print(f"Erreur d'initialisation audio: {e}")

    def charger_sample_en_memoire(self, path: str):
        """
        Charge un fichier WAV, le convertit en mono float32 et le stocke en RAM.
        
        Args:
            path (str): Chemin absolu ou relatif vers le fichier audio.
        """
        if path in self.cache_samples:
            return

        if not os.path.exists(path):
            print(f"Erreur: Fichier introuvable {path}")
            return

        try:
            data, fs = sf.read(path, dtype='float32')
            
            # Conversion Stéréo vers Mono (moyenne des canaux)
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
            
            self.cache_samples[path] = data
            print(f"Audio chargé : {os.path.basename(path)}")
        except Exception as e:
            print(f"Erreur chargement {path}: {e}")

    def jouer_mix(self, liste_chemins: list):
        """"
        Ajoute une liste de sons à la file d'attente pour une lecture immédiate.
                
        Args:
            liste_chemins (list): Liste des chemins vers les samples à mixer.
        """
        if not liste_chemins:
            return

        for path in liste_chemins:
            if path in self.cache_samples:
                data = self.cache_samples[path]
                # Envoi des données au thread audio via la queue
                self.command_queue.put({'data': data, 'cursor': 0})

    def _audio_callback(self, outdata, frames, time, status):
        """
        Callback temps réel exécutée par sounddevice dans un thread haute priorité.
        
        Réalise le mixage additif des sons actifs, applique le volume global 
        et effectue un écrêtage (clipping) pour éviter la saturation numérique.
        """
        if status:
            pass # Gestionnaire d'erreurs de flux (Xrun)
        
        outdata.fill(0)
    
        try:
            while True:
                new_sound = self.command_queue.get_nowait()
                self.active_sounds.append(new_sound)
        except queue.Empty:
            pass

        sons_restants = []
        mix_buffer = np.zeros(frames, dtype='float32')
        
        for sound in self.active_sounds:
            data = sound['data']
            cursor = sound['cursor']
            
            n_frames = min(frames, len(data) - cursor)
            
            if n_frames > 0:
                mix_buffer[:n_frames] += data[cursor : cursor + n_frames]
                
                sound['cursor'] += n_frames
                
                if sound['cursor'] < len(data):
                    sons_restants.append(sound)
        
        # Mise à jour de la liste des sons actifs
        self.active_sounds = sons_restants
        
        # 4. Application du volume global
        mix_buffer *= self.volume_global
        
        # 5. Limiteur (Clipping) pour éviter la saturation numérique
        np.clip(mix_buffer, -1.0, 1.0, out=mix_buffer)
        
        # 6. Écriture dans le buffer de sortie
        outdata[:, 0] = mix_buffer

    def set_volume(self, valeur: float):
        """
        Définit le volume de sortie
        
        Args:
            valeur (float): Coefficient entre 0.0 et 1.0
        """
        self.volume_global = max(0.0, min(1.0, valeur))

    def stop_stream(self):
        """
        Arrête proprement le flux audio et libère les ressources matérielles.
        """
        if self.stream:
            self.stream.stop()
            self.stream.close()
            
    def appliquer_delay(self, signal, temps_ms=200, feedback=0.3):
        """
        Applique un effet d'écho (Delay) sur un son
        
        
        Args:
            signal (np.array): Le signal audio source.
            temps_ms (int): Délai avant la première répétition.
            feedback (float): Intensité de réinjection de l'écho.
        """
        if feedback <= 0:
            return signal
            
        # Conversion du temps en nombre d'échantillons (samples)
        nb_samples_delay = int((temps_ms / 1000.0) * 44100)
        
        # Création d'un buffer plus long pour accueillir l'écho
        signal_traite = np.zeros(len(signal) + nb_samples_delay)
        
        # On place le son original au début
        signal_traite[:len(signal)] = signal
        
        # On ajoute la version retardée et atténuée
        # C'est ici que l'addition mathématique de janvier prend tout son sens
        echo = signal * feedback
        signal_traite[nb_samples_delay:nb_samples_delay + len(signal)] += echo
        
        return np.clip(signal_traite, -1.0, 1.0)
    
    def appliquer_filtre_passe_bas(self, data, intensite=0.5):
        """
        Applique un filtre passe-bas simple (One-pole) via NumPy (Objectif Avril).
        
        Lisse le signal en atténuant les hautes fréquences par moyenne glissante.
        
        Args:
            data (np.array): Le signal à filtrer.
            intensite (float): Force de la coupure (0.0 à 1.0).
        """
        if intensite <= 0: return data
        
        out = np.zeros_like(data)
        alpha = 1.0 - intensite
        val_precedente = 0
        
        for i in range(len(data)):
            out[i] = alpha * data[i] + (1 - alpha) * val_precedente
            val_precedente = out[i]
            
        return out