# backend/app/routers/hero.py
from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends

from backend.app.database import get_db
from backend.app.models.DasModelAdmin import User
from backend.app.schemas.HeroSchemas import HeroInDB, HeroModel
from backend.app.utils.authenticate import get_current_user

prefix = "/hero"

router = APIRouter(prefix=prefix, tags=["Heroes"])
from sqlalchemy.orm import Session
from ..models import Hero
from ..utils.file_operations import upload_file, delete_file

from sqlalchemy.exc import SQLAlchemyError

# Configuration
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_MIME_TYPES = {
    "text/plain",
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/gif",
}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@router.post("/upload/", response_model=HeroInDB)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if not allowed_file(file.filename):
            raise HTTPException(status_code=400, detail="File type not allowed")

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")

        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(status_code=400, detail="Invalid file content")

        await file.seek(0)  # Reset file pointer
        public_url, _ = await upload_file(file, prefix.strip("/"))

        db_image = Hero(image=public_url, active_img=False, user_id=current_user.id)
        db.add(db_image)
        db.commit()
        db.refresh(db_image)

        return HeroInDB(
            user_id=current_user.id,
            id=db_image.id,
            image_url=db_image.image,
            active_img=db_image.active_img,
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")

@router.get("/", response_model=List[HeroModel])
async def get_images(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        images = db.query(Hero).filter(Hero.user_id == current_user.id).all()
        return [
            HeroModel(id=image.id, image_url=image.image, active_img=image.active_img)
            for image in images
        ]
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.get("/{image_id}", response_model=HeroModel)
async def get_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        image = (
            db.query(Hero)
            .filter(Hero.id == image_id, Hero.user_id == current_user.id)
            .first()
        )
        if image is None:
            raise HTTPException(status_code=404, detail="Image not found")
        return HeroModel(
            id=image.id, image_url=image.image, active_img=image.active_img
        )
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred")

@router.delete("/{image_id}", response_model=HeroModel)
async def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        db_image = (
            db.query(Hero)
            .filter(Hero.id == image_id, Hero.user_id == current_user.id)
            .first()
        )
        if not db_image:
            raise HTTPException(status_code=404, detail="Image not found")

        filename = db_image.image.split("/")[-1].split("?")[0]
        delete_file(prefix.strip("/"), filename)

        db.delete(db_image)
        db.commit()

        return HeroModel(
            id=db_image.id, image_url=db_image.image, active_img=db_image.active_img
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.put("/{image_id}", response_model=HeroModel)
async def update_image(
    image_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        db_image = (
            db.query(Hero)
            .filter(Hero.id == image_id, Hero.user_id == current_user.id)
            .first()
        )
        if not db_image:
            raise HTTPException(status_code=404, detail="Image not found")

        if not allowed_file(file.filename):
            raise HTTPException(status_code=400, detail="File type not allowed")

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")

        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(status_code=400, detail="Invalid file content")

        old_filename = db_image.image.split("/")[-1].split("?")[0]
        delete_file(prefix.strip("/"), old_filename)

        await file.seek(0)  # Reset file pointer
        public_url, _ = await upload_file(file, prefix.strip("/"))
        db_image.image = public_url
        db.commit()
        db.refresh(db_image)

        return HeroModel(
            id=db_image.id, image_url=db_image.image, active_img=db_image.active_img
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")

@router.put("/activate/{hero_id}", response_model=HeroModel)
async def activate_hero_image(
    hero_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        hero = (
            db.query(Hero)
            .filter(Hero.id == hero_id, Hero.user_id == current_user.id)
            .first()
        )
        if not hero:
            raise HTTPException(status_code=404, detail="Hero not found")

        db.query(Hero).filter(Hero.user_id == current_user.id).update(
            {Hero.active_img: False}
        )
        hero.active_img = True

        db.commit()
        db.refresh(hero)

        return HeroModel(id=hero.id, image_url=hero.image, active_img=hero.active_img)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.get("/isactive/", response_model=HeroModel)
async def get_active_hero(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        # Try to get the active hero image
        active_hero = (
            db.query(Hero)
            .filter(Hero.user_id == current_user.id, Hero.active_img == True)
            .first()
        )

        if active_hero is None:
            raise HTTPException(status_code=404, detail="No active images found")

        return HeroModel(
            id=active_hero.id,
            image_url=active_hero.image,
            active_img=active_hero.active_img,
        )

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred")
