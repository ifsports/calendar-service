import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from sqlalchemy.orm import Session
from .. import models, schemas
from typing import List
import json


CLIENT_SECRETS_FILE = 'config/google_credentials.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']
REDIRECT_URI = "http://35.215.219.1/api/v1/calendar/auth/callback"


class GoogleAuthService:

    def get_authorization_url(self, state: str = None):
        """
        Gera a URL para o usuário iniciar o fluxo de autorização do Google.
        """
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )

        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            prompt='consent',
            state=state
        )
        return authorization_url

    def fetch_tokens_and_save(self, code: str, user_email: str, db: Session):
        """
        Recebe o código de autorização, troca por tokens e salva no banco de dados.
        """
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        flow.fetch_token(code=code)

        creds_json = flow.credentials.to_json()

        db_user_creds = db.query(models.UserCredentials).filter(models.UserCredentials.user_email == user_email).first()

        if db_user_creds:
            db_user_creds.token_json = creds_json

        else:
            db_user_creds = models.UserCredentials(user_email=user_email, token_json=creds_json)
            db.add(db_user_creds)

        db.commit()
        db.refresh(db_user_creds)

    def _get_credentials_from_db(self, user_email: str, db: Session) -> Credentials:
        """
        Carrega as credenciais de um usuário específico do banco de dados.
        """
        db_user_creds = db.query(models.UserCredentials).filter(models.UserCredentials.user_email == user_email).first()
        if not db_user_creds:
            return None

        creds_info = json.loads(db_user_creds.token_json)
        creds = Credentials.from_authorized_user_info(info=creds_info, scopes=SCOPES)

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            db_user_creds.token_json = creds.to_json()
            db.commit()

        return creds

    def create_calendar_event(self, match_details: List[schemas.MatchDetails], user_email: str, db: Session):
        """
        Cria múltiplos eventos na agenda do usuário especificado.
        """
        creds = self._get_credentials_from_db(user_email, db)
        if not creds:
            raise Exception("Usuário não autenticado. Por favor, inicie o processo de login.")

        try:
            service = build('calendar', 'v3', credentials=creds)
            created_event_ids = []

            for match in match_details:
                event_body = {
                    'summary': match.summary,
                    'location': match.location,
                    'description': match.description,
                    'start': {
                        'dateTime': match.start_time.isoformat(),
                        'timeZone': 'America/Sao_Paulo',
                    },
                    'end': {
                        'dateTime': match.end_time.isoformat(),
                        'timeZone': 'America/Sao_Paulo',
                    },
                    'attendees': [
                        {'email': user_email},
                    ],
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'popup', 'minutes': 60},
                            {'method': 'popup', 'minutes': 15},
                        ],
                    },
                }

                event = service.events().insert(calendarId='primary', body=event_body).execute()
                print(f"Evento criado: {event.get('htmlLink')}")
                created_event_ids.append(event['id'])

            return created_event_ids

        except HttpError as error:
            print(f'Ocorreu um erro: {error}')
            raise Exception(f"Erro na API do Google: {error}")
