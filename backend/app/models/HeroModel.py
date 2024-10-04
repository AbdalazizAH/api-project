# backend/app/models/Hero.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from ..database import Base
from sqlalchemy.orm import relationship


class Hero(Base):
    __tablename__ = "HeroTable"
    id = Column(Integer, primary_key=True, index=True)
    image = Column(String)
    active_img = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="HeroTable")
