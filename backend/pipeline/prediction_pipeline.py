# backend/pipeline/prediction_pipeline.py

import traceback
from backend.pipeline.master_pipeline import MasterPipeline


class PredictionPipeline:
    """
    A predikciós réteg, amely a MasterPipeline-t használja.
    Képes:
    - több meccs adat feldolgozására
    - AI predikciók visszaadására
    - egységes struktúrába rendezett output generálására
    """

    def __init__(self):
        self.master = MasterPipeline()

    # ==================================================================
    #  Több mérkőzés predikciója
    # ==================================================================
    def prediktal_tobb_meccs(self, meccs_lista: list) -> list:
        """
        Bemenet: több meccsből álló list
        Kimenet: fusion + value + likviditás + edge
        """
        try:
            return self.master.feldolgoz(meccs_lista)
        except Exception:
            print("[PredictionPipeline] Hiba predikció közben:")
            print(traceback.format_exc())
            return []

    # ==================================================================
    #  Egy mérkőzés predikciója
    # ==================================================================
    def prediktal_egy_meccs(self, meccs: dict) -> dict:
        """
        Bemenet: egyetlen mérkőzés adatai
        Kimenet: predikciós dict
        """
        try:
            eredm = self.master.feldolgoz([meccs])
            if eredm:
                return eredm[0]
            return {}
        except Exception:
            print("[PredictionPipeline] Hiba egy meccs predikciójánál:")
            print(traceback.format_exc())
            return {}
