from datetime import datetime, timedelta
from uuid import UUID
import uuid

from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlmodel import Session, select
from redis import Redis

from app.config import settings
from app.users.model import User
from app.auth.schemas import RegisterRequest, LoginRequest, TokenResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Token config ---
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = 30
ALGORITHM = "HS256"


# --- Password helpers ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# --- Token helpers ---
def create_access_token(user_id: UUID) -> str:
    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: UUID) -> str:
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": str(uuid.uuid4()),  # unique ID per token, needed for blocklist
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


# --- Auth functions ---
def register(data: RegisterRequest, db: Session) -> User:
    # check if email already exists
    existing = db.exec(select(User).where(User.email == data.email)).first()
    if existing:
        raise ValueError("Email already registered")

    user = User(email=data.email, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login(data: LoginRequest, db: Session) -> TokenResponse:
    user = db.exec(select(User).where(User.email == data.email)).first()

    if not user or not user.password_hash:
        raise ValueError("Invalid credentials")

    if not verify_password(data.password, user.password_hash):
        raise ValueError("Invalid credentials")

    if not user.is_active:
        raise ValueError("Account is inactive")

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


def refresh(refresh_token: str, db: Session, redis: Redis) -> TokenResponse:
    payload = decode_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise ValueError("Invalid refresh token")

    # check if token is blocklisted
    jti = payload.get("jti")
    if redis.get(f"blocklist:{jti}"):
        raise ValueError("Token has been revoked")

    user_id = payload.get("sub")
    user = db.get(User, UUID(user_id))

    if not user or not user.is_active:
        raise ValueError("User not found or inactive")

    # blocklist the old refresh token so it can't be reused
    exp = payload.get("exp")
    ttl = exp - int(datetime.utcnow().timestamp())
    if ttl > 0:
        redis.setex(f"blocklist:{jti}", ttl, "1")

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


def logout(access_token: str, redis: Redis) -> None:
    payload = decode_token(access_token)

    if not payload:
        return  # already invalid, nothing to do

    jti = payload.get("jti", payload.get("sub"))  # access tokens use sub as fallback
    exp = payload.get("exp")
    ttl = exp - int(datetime.utcnow().timestamp())

    if ttl > 0:
        redis.setex(f"blocklist:{jti}", ttl, "1")
