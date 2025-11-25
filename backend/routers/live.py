from fastapi import APIRouter
from services.tip_engine import generate_live_tips

router = APIRouter(prefix="/tips")

@router.get("/live")
def get_live():
    return generate_live_tips()
