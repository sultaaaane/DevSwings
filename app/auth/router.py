from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session
from redis import Redis
import urllib.parse

from app.auth import service as auth_service
from app.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.config import settings
from app.core.database import get_session
from app.core.redis import get_redis

router = APIRouter()


@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_session)):
    try:
        user = auth_service.register(data, db)
        return {"message": "Account created successfully", "user_id": str(user.id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_session)):
    try:
        return auth_service.login(data, db)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    refresh_token: str,
    db: Session = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    try:
        return auth_service.refresh(refresh_token, db, redis)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout")
def logout(access_token: str, redis: Redis = Depends(get_redis)):
    auth_service.logout(access_token, redis)
    return {"message": "Logged out successfully"}


@router.get("/github/login")
def github_login():
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
        "scope": "read:user user:email",
        "response_type": "code",
    }
    url = f"https://github.com/login/oauth/authorize?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)


@router.get("/github/callback", response_model=TokenResponse)
async def github_callback(code: str, db: Session = Depends(get_session)):
    try:
        return await auth_service.github_auth_callback(code, db)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal Server Error during GitHub OAuth"
        )
