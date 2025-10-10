
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse

from src.core.config import settings
from src.db.session import get_db
from src.services import users
from src.core.security import create_access_token, get_current_user
from src.db import models

router = APIRouter()

oauth = OAuth()
oauth.register(
    name='oidc',
    client_id=settings.oidc.client_id,
    client_secret=settings.oidc.client_secret,
    server_metadata_url=settings.oidc.server_metadata_url,
    client_kwargs={'scope': 'openid email profile'}
)


@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for('callback')
    return await oauth.oidc.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.oidc.authorize_access_token(request)
    user_info = await oauth.oidc.userinfo(token=token)

    user = users.get_user_by_external_id(db, user_info['sub'])
    if not user:
        user = users.create_user(db, user_info['sub'], user_info['email'])

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user