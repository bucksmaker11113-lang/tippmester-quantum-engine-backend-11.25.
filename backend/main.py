from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ROUTERS (mappából importáljuk)
from routers import tips, live, kombi, chat

app = FastAPI()

# --------------------------------------------------
# CORS (elengedhetetlen, különben a frontend nem éri el)
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # ha lesz domain, akkor majd cseréljük
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# ROUTER BEKÖTÉS
# --------------------------------------------------
app.include_router(tips.router)
app.include_router(live.router)
app.include_router(kombi.router)
app.include_router(chat.router)


# --------------------------------------------------
# SERVER STARTUP (opcionális)
# --------------------------------------------------
@app.get("/")
def root():
    return {"status": "backend running", "version": "1.0"}
