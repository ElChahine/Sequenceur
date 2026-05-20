# src/sequenceur/export.py
import numpy as np

class AudioExporter:
    """
    Service dédié au rendu mathématique hors ligne des compositions.
    """

    @staticmethod
    def exporter(pistes, bpm, volume_global, cache_samples, nb_boucles=4):
        """
        Calcule la sommation des échantillons pour créer le signal linéaire.
        """
        samples_par_pas = int((60 / bpm / 4) * 44100)
        duree_totale_samples = samples_par_pas * 64 * nb_boucles
        
        rendu_final = np.zeros(duree_totale_samples, dtype='float32')
        
        for piste in pistes:
            if piste.is_mute:
                continue
                
            sample_data = cache_samples.get(piste.sample_path)
            if sample_data is None:
                continue
                
            for b in range(nb_boucles):
                for step in range(64):
                    if piste.pattern[step]:
                        pos_start = (b * 64 * samples_par_pas) + (step * samples_par_pas)
                        pos_end = pos_start + len(sample_data)
                        
                        if pos_end > duree_totale_samples:
                            overlap = duree_totale_samples - pos_start
                            rendu_final[pos_start:] += sample_data[:overlap]
                        else:
                            rendu_final[pos_start:pos_end] += sample_data
                            
        rendu_final *= volume_global
        return np.clip(rendu_final, -1.0, 1.0)