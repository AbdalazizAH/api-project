# # backend/app/models/DasModelAdmin.py

from datetime import datetime
from backend.app.database import Base
from sqlalchemy.orm import relationship

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    registration_date = Column(DateTime, default=datetime.utcnow)
    is_email_verified = Column(Boolean, default=False)
    email_verification_code = Column(String)
    
    
    HeroTable = relationship("Hero", back_populates="user")

