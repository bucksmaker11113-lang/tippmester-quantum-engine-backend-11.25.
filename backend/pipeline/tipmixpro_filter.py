# backend/pipeline/tippmixpro_filter.py

import traceback


class TippmixProFilter:
    """
    A TippmixPro validációs modul.
    
    Feladata:
        - összevetni az AI tippet a TippmixPro kínálatával
        - megállapítani, hogy ugyanaz a piac elérhető-e
        - ellenőrizni a vonalat (pl. AH -1.5, Over 2.5)
        - eldönteni, hogy a tipp megjátszható-e
    
    Eredmény:
        {
          "megjatszhato": True/False,
          "tippmix_odds": float,
          "hiba": None vagy "nincs ilyen piac", ...
        }
    """

    def __init__(self):
        pass

    # ==================================================================
    # Fő validátor
    # ==================================================================
    def ellenoriz(self, ai_tipp: dict, tippmix_lista: list) -> dict:
        """
        ai_tipp:
            {
              "meccs": {...},
              "predikcio": {...},
              "value": ...,
              "edge": ...,
              "likviditas": ...
            }

        tippmix_lista:
            TippmixProScraper().lekerdez() eredménye
        
        """

        try:
            meccs = ai_tipp.get("meccs", {})
            sport = meccs.get("sport")
            hazai = meccs.get("hazai")
            vendeg = meccs.get("vendeg")
            piac = meccs.get("piac")
            ertek = meccs.get("ertek")

            # ==================================================================
            # 1) Keresünk azonos meccset
            # ==================================================================
            for tippmix in tippmix_lista:
                if (
                    tippmix.get("sport") == sport and
                    tippmix.get("hazai") == hazai and
                    tippmix.get("vendeg") == vendeg
                ):

                    # ==================================================================
                    # 2) Keresünk ugyanazt a piacot
                    # ==================================================================
                    if tippmix.get("piac") != piac:
                        continue

                    # ==================================================================
                    # 3) Keresünk ugyanazt a vonalat / értéket
                    # ==================================================================
                    tm_line = tippmix.get("ertek")
                    if not self._line_egyezes(ertek, tm_line):
                        continue

                    # ==================================================================
                    # 4) Tippmix odds
                    # ==================================================================
                    tm_odds = tippmix.get("odds")

                    return {
                        "megjatszhato": True,
                        "tippmix_odds": tm_odds,
                        "hiba": None
                    }

            # ha idáig eljut → nincs találat
            return {
                "megjatszhato": False,
                "tippmix_odds": None,
                "hiba": "piac vagy vonal nem található a TippmixPro-n"
            }

        except Exception:
            print("[TippmixProFilter] Hiba validálás közben:")
            print(traceback.format_exc())
            return {
                "megjatszhato": False,
                "tippmix_odds": None,
                "hiba": "technikai hiba"
            }

    # ==================================================================
    # Vonal (érték) egyeztetés
    # ==================================================================
    def _line_egyezes(self, ai_line, tm_line) -> bool:
        """
        Az AI és a TippmixPro vonalak összehasonlítása:

        pl.:
            -1.5 == -1.5
            2.5 == 2.5
            Over 2.5 → 2.5
        """

        try:
            # ha numerikus – könnyen összevethető
            if isinstance(ai_line, (int, float)) and isinstance(tm_line, (int, float)):
                return abs(float(ai_line) - float(tm_line)) < 0.001

            # string → float parse
            if isinstance(ai_line, str) and isinstance(tm_line, str):
                if ai_line.replace(",", ".") == tm_line.replace(",", "."):
                    return True

            # próbáljuk floatként
            try:
                if abs(float(ai_line) - float(tm_line)) < 0.001:
                    return True
            except:
                pass

            # ha semmi nem egyezik
            return False

        except:
            return False
