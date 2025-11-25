from fastapi import APIRouter, WebSocket

router = APIRouter()

@router.websocket("/ws/chat")
async def chat_socket(ws: WebSocket):
    await ws.accept()
    while True:
        msg = await ws.receive_text()
        await ws.send_text(msg)
