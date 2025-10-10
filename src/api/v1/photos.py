from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.services import s3
from src.db import models

router = APIRouter()

from src.core.security import get_current_user

@router.post("/")
def upload_photo(file: UploadFile = File(...), hashtags: str = Form(None), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    public_url, s3_key = s3.s3_service.upload_file(file)
    
    db_photo = models.Photo(
        owner_id=current_user.id,
        public_url=public_url,
        s3_key=s3_key
    )
    db.add(db_photo)

    hashtag_objs = []
    if hashtags:
        hashtag_names = [h.strip() for h in hashtags.split(",")]
        for name in hashtag_names:
            hashtag_obj = db.query(models.Hashtag).filter(models.Hashtag.name == name).first()
            if not hashtag_obj:
                hashtag_obj = models.Hashtag(name=name)
                db.add(hashtag_obj)
            hashtag_objs.append(hashtag_obj)
    db.flush()

    for hashtag_obj in hashtag_objs:
        db_photo.hashtags.append(hashtag_obj)

    db.commit()
    db.refresh(db_photo)
    return db_photo


@router.get("/")
def get_photos(hashtag: str = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    query = db.query(models.Photo).filter(models.Photo.owner_id == current_user.id)
    if hashtag:
        query = query.join(models.Photo.hashtags).filter(models.Hashtag.name == hashtag)
    return query.all()


@router.get("/{photo_id}")
def get_photo(photo_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    photo = db.query(models.Photo).filter(models.Photo.id == photo_id, models.Photo.owner_id == current_user.id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo


@router.delete("/{photo_id}")
def delete_photo(photo_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    photo = db.query(models.Photo).filter(models.Photo.id == photo_id, models.Photo.owner_id == current_user.id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    # s3.s3_service.delete_file(photo.s3_key) # You would implement this in the S3 service

    db.delete(photo)
    db.commit()
    return {"detail": "Photo deleted"}