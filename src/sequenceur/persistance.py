# src/sequenceur/persistance.py
import json

class ProjectPersistenceManager:
    """
    Classe pour sauvegarder et charger la configuration d'un projet.
    """

    @staticmethod
    def sauvegarder_projet(chemin_fichier, sequenceur_core):
        """
        Prend l'état actuel du séquenceur, met les variables importantes 
        dans un dictionnaire et écrit tout ça dans un fichier JSON.
        """
        moteur = sequenceur_core.moteur_audio
        donnees = {
            "bpm": sequenceur_core.bpm,
            "volume": moteur.volume_global,
            "intensite_delay": moteur.intensite_delay,
            "intensite_filtre": moteur.intensite_filtre,
            "pistes": []
        }
        for piste in sequenceur_core.pistes:
            donnees["pistes"].append({
                "nom": piste.nom,
                "sample_path": piste.sample_path,
                "is_mute": piste.is_mute,
                "pattern": piste.pattern.copy()
            })
            
        with open(chemin_fichier, 'w') as f:
            json.dump(donnees, f, indent=4)

    @staticmethod
    def charger_projet(chemin_fichier, sequenceur_core):
        """
        Ouvre un fichier JSON, récupère les données enregistrées et remet
        à jour les paramètres de notre séquenceur.
        """
        with open(chemin_fichier, 'r') as f:
            donnees = json.load(f)
            
        sequenceur_core.bpm = donnees.get("bpm", 120)
        
        moteur = sequenceur_core.moteur_audio
        moteur.set_volume(donnees.get("volume", 1.0))
        moteur.intensite_delay = donnees.get("intensite_delay", 0.0)
        moteur.intensite_filtre = donnees.get("intensite_filtre", 0.0)
        
        pistes_sauvegardees = donnees.get("pistes", [])
        for i, piste_data in enumerate(pistes_sauvegardees):
            if i < len(sequenceur_core.pistes):
                piste_actuelle = sequenceur_core.pistes[i]
                nouveau_chemin = piste_data.get(
                    "sample_path", piste_actuelle.sample_path
                )
                
                if nouveau_chemin != piste_actuelle.sample_path:
                    sequenceur_core.changer_sample_piste(
                        i, nouveau_chemin
                    )
                else:
                    piste_actuelle.nom = piste_data.get(
                        "nom", piste_actuelle.nom
                    )
                    
                piste_actuelle.is_mute = piste_data.get(
                    "is_mute", False
                )
                piste_actuelle.pattern = piste_data.get(
                    "pattern", [False] * 64
                )