
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Table,
    func,
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

photo_hashtags = Table(
    "photo_hashtags",
    Base.metadata,
    Column("photo_id", Integer, ForeignKey("photos.id"), primary_key=True),
    Column("hashtag_id", Integer, ForeignKey("hashtags.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())

    photos = relationship("Photo", back_populates="owner")


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    public_url = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

    owner = relationship("User", back_populates="photos")
    hashtags = relationship(
        "Hashtag", secondary=photo_hashtags, back_populates="photos"
    )


class Hashtag(Base):
    __tablename__ = "hashtags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    photos = relationship(
        "Photo", secondary=photo_hashtags, back_populates="hashtags"
    )
