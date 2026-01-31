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
        self.volume_global = 1.0
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
        Charge un fichier audio, convertit les données en float32 mono et les stocke en RAM.
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
        """
        Ajoute une liste de sons à la file d'attente pour lecture immédiate.
        Cette méthode est non-bloquante.
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
        Callback audio exécutée par sounddevice dans un thread séparé.
        Réalise le mixage (addition) des échantillons actifs.
        """
        if status:
            pass # Gestionnaire d'erreurs de flux (Xrun)
        
        # 1. Initialisation du buffer de sortie à zéro (Silence)
        outdata.fill(0)
        
        # 2. Récupération des nouveaux sons depuis la file d'attente
        try:
            while True:
                new_sound = self.command_queue.get_nowait()
                self.active_sounds.append(new_sound)
        except queue.Empty:
            pass

        # 3. Traitement et mixage des sons actifs
        sons_restants = []
        mix_buffer = np.zeros(frames, dtype='float32')
        
        for sound in self.active_sounds:
            data = sound['data']
            cursor = sound['cursor']
            
            # Calcul du nombre d'échantillons disponibles pour ce bloc
            n_frames = min(frames, len(data) - cursor)
            
            if n_frames > 0:
                # Mixage additif
                mix_buffer[:n_frames] += data[cursor : cursor + n_frames]
                
                # Mise à jour du curseur de lecture
                sound['cursor'] += n_frames
                
                # Conservation du son s'il n'est pas terminé
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
        """Définit le volume global (0.0 à 1.0)."""
        self.volume_global = max(0.0, min(1.0, valeur))

    def stop_stream(self):
        """Arrête proprement le flux audio."""
        if self.stream:
            self.stream.stop()
            self.stream.close()