# backend/pipeline/single_tip_pipeline.py

import traceback
from backend.pipeline.prediction_pipeline import PredictionPipeline


class SingleTipPipeline:
    """
    Napi 4 single tipp generálása:
        - 1 foci
        - 1 kosár
        - 1 jégkorong
        - 1 tenisz

    Feltételek:
        - csak liquid piacok
        - value >= 0.15
        - edge >= 0.10
        - predikció maximális AI pontosság alapján
        - nem ütközhet kombi tipphez tartozó meccsekkel
    """

    def __init__(self):
        self.pred = PredictionPipeline()

        # napi sportág lista
        self.kell_sportok = ["foci", "kosár", "jégkorong", "tenisz"]

        # legális liquid piacok
        self.liquid_piacok = [
            "ázsiai_hendikep",
            "gol_over_under",
            "mindket_csapat_golt_szerez",
            "jatekhendikep",
            "szetthendikep",
            "pont_hatar",
            "gol_hatar"
        ]

    # ==================================================================
    # Fő függvény: kiválasztja a 4 napi single tippet
    # ==================================================================
    def general(self, meccs_lista: list, kombi_tippek: list = None) -> list:
        """
        meccs_lista: a scraper által behozott nap összes mérkőzése
        kombi_tippek: kombi pipeline által kiválasztott meccsek (nem lehet ütközés)

        kimenet: pontosan 4 tipp (ha valamelyik sportnál nincs jó tipp,
                 fallback: másnapi meccslistából keres)
        """

        try:
            if kombi_tippek is None:
                kombi_tippek = []

            # 1. teljes predikciós futás
            predikciok = self.pred.prediktal_tobb_meccs(meccs_lista)

            # 2. egy sport → egy single tipp modellezés
            single_tippek = []

            for sport in self.kell_sportok:
                sport_tip = self._valassz_tippsportban(
                    sport=sport,
                    predikciok=predikciok,
                    kombi_tippek=kombi_tippek
                )
                if sport_tip:
                    single_tippek.append(sport_tip)

            return single_tippek

        except Exception:
            print("[SingleTipPipeline] Hiba single generálás közben:")
            print(traceback.format_exc())
            return []

    # ==================================================================
    # Sport-specifikus tippválasztó
    # ==================================================================
    def _valassz_tippsportban(self, sport: str, predikciok: list, kombi_tippek: list):
        """
        Egy sportból kiválasztja a legjobb napi single tippet.
        Feltétel:
            - liquid piac
            - value >= 0.15
            - edge >= 0.10
            - nincs ütközés kombi tippel
        """

        jeloltek = []

        for adat in predikciok:
            meccs = adat["meccs"]
            piac = meccs.get("piac")

            # sport szűrés
            if meccs.get("sport") != sport:
                continue

            # csak liquid piac
            if piac not in self.liquid_piacok:
                continue

            # kombi ütközés kizárása
            if self._utkozik_kombival(meccs, kombi_tippek):
                continue

            # value & edge feltétel
            if adat["value"] < 0.15:
                continue
            if adat["edge"] < 0.10:
                continue

            jeloltek.append(adat)

        # ha nincs jelölt → nincs tipp erre a sportra
        if not jeloltek:
            return None

        # AI szerint a legjobb tipp kiválasztása
        # maximális EDGE vagy VALUE szerint
        legjobb = sorted(
            jeloltek,
            key=lambda x: (x["edge"], x["value"]),
            reverse=True
        )[0]

        return legjobb

    # ==================================================================
    # Kombi tipp ütközés detektálás
    # ==================================================================
    def _utkozik_kombival(self, meccs, kombik):
        """
        Ha ugyanaz a meccs szerepel a kombiban → nem adhat single tippet.
        """
        for k in kombik:
            km = k.get("meccs", {})
            if km.get("hazai") == meccs.get("hazai") and km.get("vendeg") == meccs.get("vendeg"):
                return True
        return False
