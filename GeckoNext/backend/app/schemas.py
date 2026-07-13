from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "annotator"          # ← добавили роль

class Token(BaseModel):
    access_token: str
    token_type: str

class UserMe(BaseModel):
    username: str
    role: str