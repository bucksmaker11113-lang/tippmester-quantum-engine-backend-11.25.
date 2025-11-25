# backend/pipeline/kombi_tip_pipeline.py

import traceback
from backend.pipeline.prediction_pipeline import PredictionPipeline


class KombiTipPipeline:
    """
    Kombi tipp generáló modul:
        - 3 és 5 közötti tipp
        - csak liquid piacokból
        - csak magas value + edge értékek
        - nem lehet ütközés a napi single tippekkel
        - sportágfüggetlen (bármely sportból válogathat)
    """

    def __init__(self):
        self.pred = PredictionPipeline()

        # engedélyezett liquid piacok
        self.liquid_piacok = [
            "ázsiai_hendikep",
            "gol_over_under",
            "mindket_csapat_golt_szerez",
            "jatekhendikep",
            "szetthendikep",
            "pont_hatar",
            "gol_hatar",
        ]

        # minimum értékek
        self.min_value = 0.12
        self.min_edge = 0.08

        # cél elemszám
        self.min_tipp = 3
        self.max_tipp = 5

    # =====================================================================
    # Kombi tipp fő funkciója
    # =====================================================================
    def general(self, meccs_lista: list, single_tippek: list = None) -> list:
        """
        meccs_lista → scraper+master pipeline alapján
        single_tippek → aznapi single tippek (nem lehet ütközés)

        visszaad egy 3-5 tippből álló kombi listát
        """

        try:
            if single_tippek is None:
                single_tippek = []

            # 1. predikciók beszerzése
            predikciok = self.pred.prediktal_tobb_meccs(meccs_lista)

            # 2. jelöltek szűrése
            jeloltek = self._szuresek(
                predikciok=predikciok,
                single_tippek=single_tippek
            )

            # 3. ha kevés jelölt → nincs kombi tipp
            if len(jeloltek) < self.min_tipp:
                return []

            # 4. legjobb 3-5 kiválasztása: edge + value súlyozott sorrend
            rendezett = sorted(
                jeloltek,
                key=lambda x: (x["edge"], x["value"]),
                reverse=True
            )

            # ha több mint 5, csak az első 5 kell
            return rendezett[:self.max_tipp]

        except Exception:
            print("[KombiTipPipeline] Hiba kombi generálás közben:")
            print(traceback.format_exc())
            return []

    # =====================================================================
    # Jelöltek szűrése
    # =====================================================================
    def _szuresek(self, predikciok: list, single_tippek: list):
        jeloltek = []

        for adat in predikciok:
            meccs = adat["meccs"]
            piac = meccs.get("piac")

            # liquid csak
            if piac not in self.liquid_piacok:
                continue

            # ne legyen ütközés single tippel
            if self._utkozik_single(meccs, single_tippek):
                continue

            # minimum értékek
            if adat["value"] < self.min_value:
                continue
            if adat["edge"] < self.min_edge:
                continue

            jeloltek.append(adat)

        return jeloltek

    # =====================================================================
    # Ütközik-e a single tippel?
    # =====================================================================
    def _utkozik_single(self, meccs, single_tippek):
        for s in single_tippek:
            sm = s.get("meccs", {})
            if sm.get("hazai") == meccs.get("hazai") and sm.get("vendeg") == meccs.get("vendeg"):
                return True
        return False
