from datetime import datetime
from pydantic import BaseModel
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserInDB(BaseModel):
    id: int
    username: str
    email: EmailStr
    registration_date: datetime
    is_email_verified: bool
