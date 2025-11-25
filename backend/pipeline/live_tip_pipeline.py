# backend/pipeline/live_tip_pipeline.py

import datetime
import traceback
from backend.pipeline.prediction_pipeline import PredictionPipeline


class LiveTipPipeline:
    """
    LIVE tipp generáló modul.
    - csak 14:00 után fut
    - csak élő eseményekből válogat
    - csak liquid piacokat enged
    - value >= 0.10 és edge >= 0.08
    - sportágfüggetlen
    """

    def __init__(self):
        self.pred = PredictionPipeline()

        self.liquid_live_piacok = [
            "ázsiai_hendikep",
            "gol_over_under",
            "mindket_csapat_golt_szerez",
            "jatekhendikep",
            "szetthendikep",
            "pont_hatar",
            "gol_hatar",
        ]

        # minimum threshold élőben
        self.min_value = 0.10
        self.min_edge = 0.08

    # ==================================================================
    # Fő élő tipp generáló logika
    # ==================================================================
    def general(self, elojegy_lista: list, single_tippek=None, kombi_tippek=None):
        """
        elojegy_lista → scraper élő meccsadatok

        visszaad:
            [
              {
                "meccs": {...},
                "predikcio": {...},
                "value": 0.xx,
                "likviditas": 0.xx,
                "edge": 0.xx
              }
            ]
        """

        try:
            # 1) időkorlát
            if not self._ido_engedelyezett():
                return []

            if single_tippek is None:
                single_tippek = []
            if kombi_tippek is None:
                kombi_tippek = []

            # 2) predikciók futtatása
            predikciok = self.pred.prediktal_tobb_meccs(elojegy_lista)

            # 3) szűrés live kritériumok alapján
            jeloltek = self._szur_predikciok(
                predikciok,
                single_tippek,
                kombi_tippek
            )

            # 4) legjobb kiválasztása (1-3 élő tipp)
            rendezett = sorted(
                jeloltek,
                key=lambda x: (x["edge"], x["value"]),
                reverse=True
            )

            return rendezett[:3]  # max 3 élő tipp

        except Exception:
            print("[LiveTipPipeline] Hiba live tipp generálás közben:")
            print(traceback.format_exc())
            return []

    # ==================================================================
    # Szűrőfeltételek live tippekhez
    # ==================================================================
    def _szur_predikciok(self, predikciok, single_tippek, kombi_tippek):
        jeloltek = []

        for adat in predikciok:
            meccs = adat["meccs"]
            piac = meccs.get("piac")

            # csak liquid piac élőben
            if piac not in self.liquid_live_piacok:
                continue

            # ne ütközzön single/kombi tippel
            if self._utkozik(meccs, single_tippek):
                continue
            if self._utkozik(meccs, kombi_tippek):
                continue

            # min value / edge
            if adat["value"] < self.min_value:
                continue
            if adat["edge"] < self.min_edge:
                continue

            jeloltek.append(adat)

        return jeloltek

    # ==================================================================
    # Ütközés ellenőrzése (single + kombi)
    # ==================================================================
    def _utkozik(self, meccs, tipplist):
        for tip in tipplist:
            tm = tip.get("meccs", {})
            if tm.get("hazai") == meccs.get("hazai") and tm.get("vendeg") == meccs.get("vendeg"):
                return True
        return False

    # ==================================================================
    # Időkorlát ellenőrzése (14:00 után)
    # ==================================================================
    def _ido_engedelyezett(self):
        most = datetime.datetime.now().time()
        engedely = datetime.time(14, 0, 0)
        return most >= engedely
