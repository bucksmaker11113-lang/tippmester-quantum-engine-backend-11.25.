from fastapi import APIRouter
from services.tip_engine import generate_single_tips

router = APIRouter(prefix="/tips")

@router.get("/single")
def get_single():
    return generate_single_tips()
