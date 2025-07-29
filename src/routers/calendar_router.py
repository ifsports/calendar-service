from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..services.google_auth_service import GoogleAuthService
from .. import schemas
from ..dependencies import get_db
from typing import Optional

router = APIRouter(
    prefix="/api/v1/calendar",
    tags=["Calendar"]
)

auth_service = GoogleAuthService()


@router.get("/auth/login", response_model=schemas.AuthURLResponse)
def get_auth_url(user_email: str):
    """
    Endpoint para o frontend obter a URL de autorização do Google.
    O frontend deve redirecionar o usuário para esta URL.
    """
    try:
        url = auth_service.get_authorization_url(state=user_email)
        return {"authorization_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auth/callback")
def auth_callback(code: str, state: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Endpoint de callback. O Google redireciona o usuário para cá após o login.
    Este endpoint não deve ser chamado diretamente pelo frontend.
    O email do usuário precisa ser passado de alguma forma, o `state` é ideal para isso.
    """

    user_email = state

    if not user_email:
        raise HTTPException(status_code=400, detail="Email do usuário não encontrado no estado da requisição.")

    try:
        auth_service.fetch_tokens_and_save(code, user_email, db)
        return {"status": "success", "message": "Autenticação concluída com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar o token: {str(e)}")


@router.post("/events", response_model=schemas.StatusResponse)
def create_event(event_data: schemas.CalendarEventCreate, db: Session = Depends(get_db)):
    """
    Cria um evento na agenda do usuário. Requer que o usuário já tenha autenticado.
    """
    try:
        event_ids = auth_service.create_calendar_event(
            event_data.match_details,
            event_data.user_email,
            db
        )
        return {
            "status": "success",
            "message": f"Evento criado com sucesso com o ID: {event_ids}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))