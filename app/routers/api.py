from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agent import run_agent
from app.session_manager import session_manager

router = APIRouter(prefix="/api")


class AskRequest(BaseModel):
    session_id: str | None = None
    message: str


class AskResponse(BaseModel):
    session_id: str
    response: str
    conversation: list


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    session_id, history = session_manager.get_or_create(req.session_id)
    try:
        reply = run_agent(history, req.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return AskResponse(
        session_id=session_id,
        response=reply,
        conversation=[m for m in history if isinstance(m.get("content"), str)],
    )


@router.get("/session/{session_id}")
def get_session(session_id: str):
    history = session_manager.get_history(session_id)
    if history is None:
        raise HTTPException(status_code=404, detail="Sessione non trovata")
    return {"session_id": session_id, "conversation": history}


@router.delete("/session/{session_id}")
def delete_session(session_id: str):
    deleted = session_manager.delete(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sessione non trovata")
    return {"deleted": True}
