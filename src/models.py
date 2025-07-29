from sqlalchemy import Column, String, Text, Integer
from src.database import Base


class UserCredentials(Base):
    __tablename__ = "user_credentials"

    user_email = Column(String, primary_key=True, index=True)
    token_json = Column(Text, nullable=False)

    def __repr__(self):
        return f"<UserCredentials(user_email='{self.user_email}')>"