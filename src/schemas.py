from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from uuid import UUID

class MatchDetails(BaseModel):
    summary: str
    description: str
    start_time: datetime
    end_time: datetime
    location: Optional[str] = "Ginásio IFRN"

class CalendarEventCreate(BaseModel):
    user_email: EmailStr
    match_details: List[MatchDetails]

class AuthURLResponse(BaseModel):
    authorization_url: str

class StatusResponse(BaseModel):
    status: str
    message: str