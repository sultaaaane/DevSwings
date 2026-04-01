from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from redis import Redis

from app.auth import service as auth_service
from app.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
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
