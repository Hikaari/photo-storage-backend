
from sqlalchemy.orm import Session

from src.db import models

def get_user_by_external_id(db: Session, external_id: str):
    return db.query(models.User).filter(models.User.external_id == external_id).first()

def create_user(db: Session, external_id: str, username: str):
    db_user = models.User(external_id=external_id, username=username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
