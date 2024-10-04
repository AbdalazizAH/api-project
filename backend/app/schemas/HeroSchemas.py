# backend/app/schemas/hero.py
from pydantic import BaseModel, Field

#! hero_model.py
class HeroModel(BaseModel):
    id: int = Field(..., gt=0, description="The ID of the uploaded image")
    image_url: str = Field(..., min_length=1, max_length=255, description="The URL of the uploaded image")
    active_img: bool = Field(default=False, description="Whether the image is active")

    class Config:
        from_attributes = True


class HeroInDB(BaseModel):
    id: int
    user_id: int
    active_img: bool
    image_url: str

    class Config:
        from_attributes = True
