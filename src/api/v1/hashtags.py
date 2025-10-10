from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.db import models

router = APIRouter()


@router.post("/")
def create_hashtag(name: str, db: Session = Depends(get_db)):
    existing_hashtag = db.query(models.Hashtag).filter(models.Hashtag.name == name).first()
    if existing_hashtag:
        raise HTTPException(status_code=409, detail="Hashtag already exists")
    db_hashtag = models.Hashtag(name=name)
    db.add(db_hashtag)
    db.commit()
    db.refresh(db_hashtag)
    return db_hashtag


@router.get("/")
def get_hashtags(db: Session = Depends(get_db)):
    return db.query(models.Hashtag).all()


@router.get("/search")
def search_hashtags(q: str, db: Session = Depends(get_db)):
    return db.query(models.Hashtag).filter(models.Hashtag.name.ilike(f"%{q}%")).all()