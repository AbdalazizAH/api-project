from pydantic import BaseModel


class VerificationRequest(BaseModel):
    username: str
    code: str
