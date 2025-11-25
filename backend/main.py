# backend/main.py

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from backend.scraper.scraper_manager import ScraperManager
from backend.pipeline.single_tip_pipeline import SingleTipPipeline
from backend.pipeline.kombi_tip_pipeline import KombiTipPipeline
from backend.pipeline.live_tip_pipeline import LiveTipPipeline
from backend.pipeline.tippmixpro_filter import TippmixProFilter


app = FastAPI(
    title="Tippmester AI Backend",
    description="Professzionális sporttippeket generáló rendszer",
    version="1.0.0",
)

# CORS → FRONTEND kompatibilitás
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # frontendre majd finomítható
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# papline objektumok
scraper = ScraperManager()
single_pipeline = SingleTipPipeline()
kombi_pipeline = KombiTipPipeline()
live_pipeline = LiveTipPipeline()
tippmix_filter = TippmixProFilter()

# ======================================================================
# SINGLE TIPP ENDPOINT
# ======================================================================
@app.get("/api/single")
def get_single():
    """
    4 single tippet ad vissza.
    """
    meccsek = scraper.gyujt_napi_meccsek()
    tippmix = scraper.gyujt_tippmix_adatok()

    single_tippek = single_pipeline.general(meccsek)

    # TippmixPro validálás
    validalt = []
    for tip in single_tippek:
        tm = tippmix_filter.ellenoriz(tip, tippmix)
        tip["tippmix"] = tm
        validalt.append(tip)

    return {
        "tippek": validalt,
        "count": len(validalt)
    }

# ======================================================================
# KOMBI TIPP ENDPOINT
# ======================================================================
@app.get("/api/kombi")
def get_kombi():
    """
    3–5 kombi tippet ad vissza.
    """
    meccsek = scraper.gyujt_napi_meccsek()
    single_tippek = single_pipeline.general(meccsek)
    tippmix = scraper.gyujt_tippmix_adatok()

    kombi_tippek = kombi_pipeline.general(meccsek, single_tippek)

    # Tippmix validálás
    validalt = []
    for tip in kombi_tippek:
        tm = tippmix_filter.ellenoriz(tip, tippmix)
        tip["tippmix"] = tm
        validalt.append(tip)

    return {
        "single_tippek": single_tippek,
        "kombi_tippek": validalt,
        "count": len(validalt)
    }

# ======================================================================
# LIVE TIPP (HTTP) → csak a pillanatnyi 1-3 élő tipp
# ======================================================================
@app.get("/api/live")
def get_live():
    """
    Aktuális élő tippek listája (nem stream).
    """
    meccsek = scraper.gyujt_napi_meccsek()
    live_tippek = live_pipeline.general(meccsek)

    return {
        "live_tippek": live_tippek,
        "count": len(live_tippek)
    }

# ======================================================================
# WEBSOCKET → VALÓDI ÉLŐ STREAM!
# ======================================================================
@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    """
    Folyamatos élő tipp frissítés WebSocket-en keresztül.
    """
    await websocket.accept()

    while True:
        meccsek = scraper.gyujt_napi_meccsek()
        live_tippek = live_pipeline.general(meccsek)

        await websocket.send_json(live_tippek)

# ======================================================================
# TIPPMIX VALIDÁCIÓ KÜLÖN ENDPOINT
# ======================================================================
@app.post("/api/tippmix-validacio")
def post_tippmix_validacio(tip: dict):
    """
    Küldesz egy AI tippet → megmondja, hogy megjátszható-e TippmixPro-n.
    """
    tippmix = scraper.gyujt_tippmix_adatok()
    return tippmix_filter.ellenoriz(tip, tippmix)

# ======================================================================
# ODDS ÚJRATÖLTÉS ENDPOINT
# ======================================================================
@app.get("/api/refresh-odds")
def refresh_odds():
    """
    Manuális odds-frissítés (scraping újraindítása).
    """
    meccsek = scraper.gyujt_napi_meccsek()
    return {
        "frissitve": len(meccsek),
        "meccsek": meccsek
    }


# ======================================================================
# SERVER STARTER
# ======================================================================
if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
