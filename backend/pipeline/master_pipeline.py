# backend/pipeline/master_pipeline.py

import traceback
from backend.core.universal_fusion_engine import UniversalFusionEngine
from backend.core.value_evaluator import ValueEvaluator
from backend.core.liquidity_engine import LiquidityEngine
from backend.core.edge_evaluator import EdgeEvaluator


class MasterPipeline:
    """
    A rendszer felső szintű irányító pipeline-ja.
    Feladata:
    - több odds-forrásból bejövő mérkőzésadat normalizálása
    - Fusion Engine meghívása
    - value értékelés
    - likviditás becslés
    - edge számítás
    - teljes predikció visszaadása minden mérkőzéshez
    """

    def __init__(self):
        self.fusion = UniversalFusionEngine()
        self.value_calc = ValueEvaluator()
        self.liquidity_calc = LiquidityEngine()
        self.edge_calc = EdgeEvaluator()

    # ======================================================================
    #  FŐ FÜGGVÉNY: több meccs együttes feldolgozása
    # ======================================================================
    def feldolgoz(self, meccs_lista: list) -> list:
        """
        Bemenet:
            [
              {
                "sport": "foci",
                "hazai": "...",
                "vendeg": "...",
                "piac": "ázsiai_hendikep",
                "ertek": "-1.5",
                "odds": 1.92,
                ...
              },
              ...
            ]

        Kimenet:
            [
              {
                "meccs": {...},
                "predikcio": {...},
                "value": float,
                "likviditas": float,
                "edge": float
              },
              ...
            ]
        """

        eredmenyek = []

        for meccs in meccs_lista:
            try:
                # --------------------------------------
                # Fusion Engine meghívása
                # --------------------------------------
                raw_outputs = self.fusion.futtat_minden_engine(meccs)
                fusion_pred = self.fusion.fuzio(meccs["sport"], raw_outputs)

                # --------------------------------------
                # Value számítás
                # --------------------------------------
                value_ertek = self.value_calc.szamol(
                    predikcio=fusion_pred,
                    odds=meccs.get("odds")
                )

                # --------------------------------------
                # Likviditás becslés (piac alapú)
                # --------------------------------------
                likviditas = self.liquidity_calc.becsul(
                    sport=meccs["sport"],
                    piac=meccs["piac"]
                )

                # --------------------------------------
                # Edge számítás
                # --------------------------------------
                edge = self.edge_calc.szamol(
                    value=value_ertek,
                    likviditas=likviditas
                )

                # --------------------------------------
                # Végső output ebben a struktúrában:
                # --------------------------------------
                eredmenyek.append({
                    "meccs": meccs,
                    "predikcio": fusion_pred,
                    "value": round(value_ertek, 4),
                    "likviditas": round(likviditas, 4),
                    "edge": round(edge, 4)
                })

            except Exception:
                print("[MasterPipeline] HIBA egy meccs feldolgozásánál:")
                print(traceback.format_exc())

        return eredmenyek
