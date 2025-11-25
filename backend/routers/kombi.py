from fastapi import APIRouter
from services.tip_engine import generate_kombi_ticket

router = APIRouter(prefix="/tips")

@router.get("/kombi")
def get_kombi():
    return generate_kombi_ticket()
