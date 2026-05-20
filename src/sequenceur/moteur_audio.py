# src/sequenceur/moteur_audio.py
import os
import queue
import numpy as np
import sounddevice as sd
import soundfile as sf
from sequenceur.dsp import DelayEffect, LowPassFilterEffect

class MoteurAudio:
    """
    Gère toute la partie audio de l'application. Elle permet de mixer
    plusieurs sons en même temps sans faire ramer l'interface.
    """

    def __init__(self):
        """
        Initialise le volume, les réglages d'effets, le cache des 
        samples et lance le flux audio de sortie.
        """
        self.volume_global = 1.0
        self.intensite_delay = 0.0
        self.intensite_filtre = 0.0
        self.sample_rate = 44100
        
        # Cache des données audio chargées (Chemin -> numpy.array)
        self.cache_samples = {}
        
        # Liste des sons en cours de lecture
        # Structure : Dictionnaire {'data': array, 'cursor': int}
        self.active_sounds = []
        
        # File pour communiquer entre le thread principal et l'audio
        self.command_queue = queue.Queue()

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
        Prend le chemin d'un fichier WAV, vérifie s'il existe, le 
        convertit en mono et le met dans le dictionnaire du cache.
        """
        if path in self.cache_samples:
            return

        if not os.path.exists(path):
            print(f"Erreur: Fichier introuvable {path}")
            return

        try:
            data, fs = sf.read(path, dtype='float32')
            
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
            
            self.cache_samples[path] = data
            msg = f"Audio chargé : {os.path.basename(path)}"
            print(msg)
        except Exception as e:
            print(f"Erreur chargement {path}: {e}")

    def jouer_mix(self, liste_chemins: list):
        """
        Reçoit une liste de chemins, récupère les données dans le 
        cache, applique les effets si besoin, et met le tout dans 
        la file d'attente.
        """
        if not liste_chemins:
            return

        for path in liste_chemins:
            if path in self.cache_samples:
                data = self.cache_samples[path]
                
                if self.intensite_filtre > 0:
                    filtre = LowPassFilterEffect(
                        intensite=self.intensite_filtre
                    )
                    data = filtre.appliquer(data)
                    
                if self.intensite_delay > 0:
                    delay = DelayEffect(
                        temps_ms=220, 
                        feedback=self.intensite_delay
                    )
                    data = delay.appliquer(data)
                    
                self.command_queue.put({'data': data, 'cursor': 0})
            else:
                msg = (
                    f"MoteurAudio: Impossible de jouer, "
                    f"le sample n'est pas en mémoire -> {path}"
                )
                print(msg)

    def _audio_callback(self, outdata, frames, time, status):
        """
        Fonction appelée automatiquement par sounddevice pour remplir
        le buffer de la carte son avec les données mixées.
        """
        if status:
            pass 
        
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
                mix_buffer[:n_frames] += (
                    data[cursor : cursor + n_frames]
                )
                
                sound['cursor'] += n_frames
                
                if sound['cursor'] < len(data):
                    sons_restants.append(sound)
        
        self.active_sounds = sons_restants
        mix_buffer *= self.volume_global
        np.clip(mix_buffer, -1.0, 1.0, out=mix_buffer)
        outdata[:, 0] = mix_buffer

    def set_volume(self, valeur: float):
        """
        Permet de changer le volume général de la sortie audio.
        """
        self.volume_global = max(0.0, min(1.0, valeur))

    def stop_stream(self):
        """
        Arrête proprement le flux sounddevice et ferme la connexion.
        """
        if self.stream:
            self.stream.stop()
            self.stream.close()