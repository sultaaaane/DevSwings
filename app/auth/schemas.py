from sqlmodel import SQLModel, Field


class RegisterRequest(SQLModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=255)


class LoginRequest(SQLModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=255)


class TokenResponse(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
