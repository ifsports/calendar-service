from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
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
    Get Google Authorization URL

    Gera a URL de autorização do Google para o fluxo OAuth2.
    Este é o primeiro passo para um usuário autorizar o acesso à sua agenda.
    O frontend deve chamar este endpoint, receber a URL e redirecionar o usuário para ela.

    **Exemplo de Resposta:**

    .. code-block:: json

       {
         "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=..."
       }

    """
    try:
        url = auth_service.get_authorization_url(state=user_email)
        return {"authorization_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auth/callback")
def auth_callback(code: str, state: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Handle Google Auth Callback

    Endpoint de callback para o fluxo OAuth2 do Google. **Não deve ser chamado diretamente.**
    O Google redireciona o usuário para cá após a autorização.
    O serviço troca o código de autorização (`code`) por tokens de acesso e de atualização,
    salva as credenciais associadas ao e-mail do usuário (`state`), e então redireciona
    o usuário de volta para o frontend com um status de sucesso ou falha.
    """
    user_email = state

    if not user_email:
        frontend_url = f"http://localhost:3000/jogos?error=missing_email"
        return RedirectResponse(url=frontend_url)

    try:
        auth_service.fetch_tokens_and_save(code, user_email, db)

        frontend_url = f"http://localhost:3000/api/v1/calendar/auth/callback?status=success&user_email={user_email}"
        return RedirectResponse(url=frontend_url)

    except Exception as e:
        print(f"Erro no callback: {str(e)}")
        frontend_url = f"http://localhost:3000/jogos?error=auth_failed&message={str(e)}"
        return RedirectResponse(url=frontend_url)


@router.post("/events", response_model=schemas.StatusResponse)
def create_event(event_data: schemas.CalendarEventCreate, db: Session = Depends(get_db)):
    """
    Create a Calendar Event

    Cria um novo evento na agenda Google do usuário.
    O usuário precisa ter completado o fluxo de autorização OAuth2 previamente,
    para que o sistema tenha as credenciais necessárias para agir em seu nome.

    **Exemplo de Corpo da Requisição (Payload):**

    .. code-block:: json

       {
         "user_email": "aluno.exemplo@academico.ifrn.edu.br",
         "match_details": {
           "summary": "Final de Futsal: Titãs vs. Gladiadores",
           "description": "Grande final dos Jogos Internos 2025.",
           "start_time": "2025-09-15T19:00:00-03:00",
           "end_time": "2025-09-15T20:30:00-03:00",
           "location": "Ginásio do IFRN - Campus Natal Central"
         }
       }


    **Exemplo de Resposta:**

    .. code-block:: json

       {
         "status": "success",
         "message": "Evento criado com sucesso com o ID: a1b2c3d4e5f6g7h8i9j0"
       }
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
