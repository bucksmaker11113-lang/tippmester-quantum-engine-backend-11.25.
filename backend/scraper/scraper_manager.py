# backend/scraper/scraper_manager.py

import traceback
import asyncio
import concurrent.futures

from backend.scraper.oddsportal_scraper import OddsPortalScraper
from backend.scraper.flashscore_scraper import FlashScoreScraper
from backend.scraper.sofascore_scraper import SofaScoreScraper
from backend.scraper.betexplorer_scraper import BetExplorerScraper
from backend.scraper.bet365_scraper import Bet365Scraper
from backend.scraper.pinnacle_scraper import PinnacleScraper
from backend.scraper.williamhill_scraper import WilliamHillScraper
from backend.scraper.betfair_scraper import BetfairScraper
from backend.scraper.onexbet_scraper import OneXBetScraper

from backend.tippmix.tippmixpro_scraper import TippmixProScraper


class ScraperManager:
    """
    A rendszer központi scraper menedzsere:

        - párhuzamos scraping 10 portálról
        - odds normalizálás
        - piac és vonal egységesítés
        - magyar kulcsok generálása
        - Betfair (volume + matched money)
        - TippmixPro külön ágon (NEM keveredik)
    """

    def __init__(self):
        # külső odds források (value, edge, liquidity alap)
        self.scraperek = {
            "oddsportal": OddsPortalScraper(),
            "flashscore": FlashScoreScraper(),
            "sofascore": SofaScoreScraper(),
            "betexplorer": BetExplorerScraper(),
            "bet365": Bet365Scraper(),
            "pinnacle": PinnacleScraper(),
            "williamhill": WilliamHillScraper(),
            "betfair": BetfairScraper(),        # volume + matched money
            "onexbet": OneXBetScraper(),
        }

        # TippmixPro külön blokk (nem keverjük a többivel!)
        self.tippmix_scraper = TippmixProScraper()

    # ==================================================================
    # NAPI MECCSLISTA GYŰJTÉSE (párhuzamos scraping)
    # ==================================================================
    def gyujt_napi_meccsek(self) -> list:
        """
        Összegyűjti a 10 odds-forrás napi kínálatát.
        Minden scraper párhuzamosan fut.
        """

        eredmeny = []

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futurek = {
                    executor.submit(scraper.lekerdez): nev
                    for nev, scraper in self.scraperek.items()
                }

                for future in concurrent.futures.as_completed(futurek):
                    scraper_nev = futurek[future]
                    try:
                        adatok = future.result()
                        if adatok:
                            eredmeny.extend(adatok)
                    except Exception:
                        print(f"[ScraperManager] Hiba a(z) {scraper_nev} scraperben:")
                        print(traceback.format_exc())

        except Exception:
            print("[ScraperManager] Általános scraping hiba:")
            print(traceback.format_exc())

        # normalizált lista visszaadása
        return self._normalizal_meccslista(eredmeny)

    # ==================================================================
    # TIPPMIXPRO VALIDÁCIÓS ÁG
    # ==================================================================
    def gyujt_tippmix_adatok(self):
        """
        TippmixPro scraping — külön ág (nem vesz részt a Fusion Engine fúzióban).
        Csak ellenőrzésre használjuk (megjátszható-e a tipp?).
        """
        try:
            return self.tippmix_scraper.lekerdez()
        except Exception:
            print("[ScraperManager] TippmixPro scraping hiba:")
            print(traceback.format_exc())
            return []

    # ==================================================================
    # PIAC ÉS VONAL NORMÁLIZÁLÁS (MAGYAR kulcsok – kulcsfontosságú!)
    # ==================================================================
    def _normalizal_meccslista(self, lista: list) -> list:
        """
        Minden scraper más kulcsneveket használ → egységesítjük:
            sport
            hazai
            vendeg
            piac
            ertek
            odds
        """

        normalizalt = []

        for m in lista:
            try:
                norm = {
                    "sport": self._norm_sport(m),
                    "hazai": m.get("home") or m.get("hazai") or m.get("team1"),
                    "vendeg": m.get("away") or m.get("vendeg") or m.get("team2"),
                    "piac": self._norm_piac(m),
                    "ertek": m.get("line_value") or m.get("ertek"),
                    "odds": m.get("odds"),
                    "forras": m.get("forras"),
                    "volume": m.get("volume"),                # Betfair
                    "matched": m.get("matched_money"),         # Betfair
                }
                normalizalt.append(norm)

            except Exception:
                print("[ScraperManager] Normalizálási hiba:")
                print(traceback.format_exc())

        return normalizalt

    # ==================================================================
    # SPORT NORMALIZÁLÁS
    # ==================================================================
    def _norm_sport(self, m):
        sport = (m.get("sport") or "").lower()

        if "foot" in sport or "soc" in sport or "foc" in sport:
            return "foci"
        if "basket" in sport or "kos" in sport:
            return "kosár"
        if "hock" in sport or "ice" in sport or "jég" in sport:
            return "jégkorong"
        if "ten" in sport:
            return "tenisz"

        return "ismeretlen"

    # ==================================================================
    # PIAC NORMALIZÁLÁS (MAGYAR)
    # ==================================================================
    def _norm_piac(self, m):
        piac_raw = (m.get("market") or m.get("piac") or "").lower()

        if "asian" in piac_raw or "handicap" in piac_raw or "ah" in piac_raw:
            return "ázsiai_hendikep"
        if "over" in piac_raw or "under" in piac_raw:
            return "gol_over_under"
        if "btts" in piac_raw or "both" in piac_raw:
            return "mindket_csapat_golt_szerez"
        if "game handicap" in piac_raw:
            return "jatekhendikep"
        if "set handicap" in piac_raw:
            return "szetthendikep"
        if "spread" in piac_raw:
            return "pont_hatar"
        if "goal line" in piac_raw or "goal limit" in piac_raw:
            return "gol_hatar"

        return "ismeretlen"
