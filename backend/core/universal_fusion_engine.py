# backend/core/universal_fusion_engine.py

import importlib
import traceback

class UniversalFusionEngine:
    def __init__(self):
        """
        A rendszer valamennyi engine-jét integráló központi modul.
        Minden engine-t dinamikusan tölt be a backend/engine könyvtárból.
        """

        # =====================================================
        #  ENGINE KATEGÓRIÁK (súlyok – elfogadott rendszered)
        # =====================================================
        self.weights = {
            "sharp": 0.30,
            "deep": 0.25,
            "statistical": 0.20,
            "ml": 0.10,
            "rating": 0.07,
            "rl": 0.05,
            "meta": 0.03
        }

        # =====================================================
        #  ENGINE LISTA – ZIP-ből beolvasva
        # =====================================================
        self.engines = {
            "sharp": [
                "sharp_money_ai_engine"
            ],
            "deep": [
                "quantum_synth_engine",
                "trend_engine",
                "score_pred_engine"
            ],
            "statistical": [
                "poisson_engine",
                "montecarlo_v3_engine"
            ],
            "ml": [
                "psychological_bias_engine",
                "oddsmaker_emulator_engine",
                "prop_engine"
            ],
            "rating": [
                # nincs dedikált rating engine a ZIP-ben
                # marad üres, vagy később bővíthető
            ],
            "rl": [
                "rl_stake_engine",
                "stake_rl_engne"
            ],
            "meta": [
                "weather_engine",
                "bias_engine"
            ]
        }

        # =====================================================
        #  DYNAMIKUS ENGINE BETÖLTŐ
        # =====================================================
        self.loaded_engines = {}
        self._load_all_engines()

    # ------------------------------------------------------------------
    def _load_all_engines(self):
        """
        Betölti az összes engine modult a backend/engine könyvtárból.
        """
        for category, engine_list in self.engines.items():
            for engine_name in engine_list:

                try:
                    module_path = f"backend.engine.{engine_name}"
                    module = importlib.import_module(module_path)

                    # ha van class a modulban
                    if hasattr(module, "Engine"):
                        engine_instance = module.Engine()
                    else:
                        # fallback: modul-level predict()
                        engine_instance = module

                    self.loaded_engines[engine_name] = {
                        "category": category,
                        "module": engine_instance
                    }

                except Exception as e:
                    print(f"[FusionEngine] Engine betöltési hiba: {engine_name}")
                    print(traceback.format_exc())
    # =====================================================================
    #  ENGINE FUTTATÁS – minden engine lefut, hibabiztos módban
    # =====================================================================
    def run_all_engines(self, match_data: dict) -> dict:
        """
        Futtatja valamennyi betöltött engine-t.
        match_data = normalizált meccsadatok (sport-specifikus)
        """
        raw_outputs = {}

        for engine_name, info in self.loaded_engines.items():
            module = info["module"]
            category = info["category"]

            try:
                if hasattr(module, "predict"):
                    result = module.predict(match_data)
                elif hasattr(module, "run"):
                    result = module.run(match_data)
                else:
                    # ha egyik sincs → skip
                    continue

                raw_outputs[engine_name] = {
                    "category": category,
                    "output": result
                }

            except Exception as e:
                print(f"[FusionEngine] HIBA engine futás közben: {engine_name}")
                print(traceback.format_exc())

        return raw_outputs

    # =====================================================================
    #  NORMALIZÁLÁS – különböző engine output -> közös skálára (0-1)
    # =====================================================================
    def _normalize_output(self, output):
        """
        Minden engine outputot 0–1 közé transzformál,
        illetve sport-specifikus szerkezetre igazít.
        """

        if output is None:
            return None

        # ha dict formátumot kapunk (leggyakoribb)
        if isinstance(output, dict):
            normalized = {}
            for key, value in output.items():
                try:
                    # numeric érték normalizálása
                    if isinstance(value, (int, float)):
                        # nagyon egyszerű skála – később fejleszthető
                        norm = max(0.0, min(1.0, float(value)))
                        normalized[key] = norm
                    else:
                        normalized[key] = value
                except:
                    continue
            return normalized

        # ha csak sima szám
        if isinstance(output, (int, float)):
            return {"value": max(0.0, min(1.0, float(output)))}

        # egyébként visszaadjuk eredetiben
        return output

    # =====================================================================
    #  SPORTÁG SPECIFIKUS – LIQUID PIAC OUTPUT KONVERZIÓ
    # =====================================================================
    def map_to_liquid_markets(self, sport: str, normalized_outputs: dict) -> dict:
        """
        Bemenet: összes engine normalizált outputja
        Kimenet: sport-specifikus liquid piac template 
        """

        # FUTBALL
        if sport == "football":
            return {
                "ah_home": self._avg_key(normalized_outputs, ["ah_home", "asian_home", "handicap_home"]),
                "ah_away": self._avg_key(normalized_outputs, ["ah_away", "asian_away", "handicap_away"]),
                "over_2_5": self._avg_key(normalized_outputs, ["over25", "o25", "over_2_5"]),
                "under_2_5": self._avg_key(normalized_outputs, ["under25", "u25", "under_2_5"]),
                "btts_yes": self._avg_key(normalized_outputs, ["btts_yes", "both_score", "btts"]),
                "btts_no": self._avg_key(normalized_outputs, ["btts_no", "no_both_score"]),
            }

        # TENISZ
        if sport == "tennis":
            return {
                "p1_win": self._avg_key(normalized_outputs, ["player1_win", "p1"]),
                "p2_win": self._avg_key(normalized_outputs, ["player2_win", "p2"]),
                "handicap_p1": self._avg_key(normalized_outputs, ["handicap_p1"]),
                "handicap_p2": self._avg_key(normalized_outputs, ["handicap_p2"]),
                "over_games": self._avg_key(normalized_outputs, ["over_games"]),
                "under_games": self._avg_key(normalized_outputs, ["under_games"]),
            }

        # KOSÁRLABDA
        if sport == "basketball":
            return {
                "spread_teamA": self._avg_key(normalized_outputs, ["spread_A", "spread_teamA"]),
                "spread_teamB": self._avg_key(normalized_outputs, ["spread_B", "spread_teamB"]),
                "over_total": self._avg_key(normalized_outputs, ["over_total", "o_total"]),
                "under_total": self._avg_key(normalized_outputs, ["under_total", "u_total"]),
            }

        # JÉGKORONG
        if sport == "hockey":
            return {
                "handicap_home": self._avg_key(normalized_outputs, ["handicap_home"]),
                "handicap_away": self._avg_key(normalized_outputs, ["handicap_away"]),
                "over_goals": self._avg_key(normalized_outputs, ["over_goals", "o_goals"]),
                "under_goals": self._avg_key(normalized_outputs, ["under_goals", "u_goals"]),
            }

        # fallback
        return normalized_outputs

    # =====================================================================
    # segédfüggvény: több kulcs átlagolása
    # =====================================================================
    def _avg_key(self, outputs, keys):
        vals = []
        for key in keys:
            for eng, data in outputs.items():
                out = data.get("output", {})
                if isinstance(out, dict) and key in out:
                    vals.append(out[key])
        if vals:
            return sum(vals) / len(vals)
        return None
    # =====================================================================
    #  FÚZIÓ – kategorizált engine outputok súlyozása
    # =====================================================================
    def fuse(self, sport: str, raw_outputs: dict) -> dict:
        """
        A teljes fúziós logika:
        - normalizálja az engine-ek outputját
        - kategóriánként súlyoz
        - sport-specifikus liquid piacokra konvertál
        - összeállítja a végső predikciót
        """

        # ------------------------------
        # 1. Normalizáljuk az összes outputot
        # ------------------------------
        normalized_by_engine = {}

        for eng, data in raw_outputs.items():
            category = data["category"]
            output = data["output"]

            normalized = self._normalize_output(output)
            normalized_by_engine[eng] = {
                "category": category,
                "output": normalized
            }

        # ------------------------------
        # 2. Kategóriák szerint csoportosítjuk
        # ------------------------------
        category_outputs = {
            "sharp": [],
            "deep": [],
            "statistical": [],
            "ml": [],
            "rating": [],
            "rl": [],
            "meta": []
        }

        for eng, data in normalized_by_engine.items():
            cat = data["category"]
            out = data["output"]
            if out is not None and cat in category_outputs:
                category_outputs[cat].append(out)

        # ------------------------------
        # 3. Kategóriák átlagolása
        # ------------------------------
        category_scores = {}

        for cat, out_list in category_outputs.items():
            if not out_list:
                category_scores[cat] = {}
                continue

            # egyes engine dict-eket átlagolunk kulcsonként
            agg = {}
            for out in out_list:
                if isinstance(out, dict):
                    for key, value in out.items():
                        agg.setdefault(key, []).append(value)

            averaged = {
                key: (sum(vals) / len(vals))
                for key, vals in agg.items()
            }

            category_scores[cat] = averaged

        # ------------------------------
        # 4. Sport-specifikus liquid piac mapping
        # ------------------------------
        mapped = self.map_to_liquid_markets(
            sport=sport,
            normalized_outputs=category_scores
        )

        # ------------------------------
        # 5. VÉGSŐ SÚLYOZOTT FÚZIÓ
        # ------------------------------
        final = {}

        for key in mapped.keys():
            total = 0.0

            for cat, score_dict in category_scores.items():
                if key in score_dict and score_dict[key] is not None:
                    total += score_dict[key] * self.weights[cat]

            final[key] = round(total, 4)

        # ------------------------------
        # 6. fallback: ha minden None, akkor None
        # ------------------------------
        if not any(final.values()):
            return {"prediction": None}

        return final


# =====================================================================
# KÉSZ A TELJES UNIVERSAL FUSION ENGINE
# =====================================================================
