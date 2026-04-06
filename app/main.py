from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import create_db
from app.auth.router import router as auth_router
from app.projects.router import router as project_router
from app.sessions.router import router as session_router
from app.commits.router import router as commit_router
from app.streaks.router import router as streak_router
import app.models


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    yield


app = FastAPI(title="DevPulse", version="0.1.0", lifespan=lifespan)

app.include_router(router=auth_router, prefix="/auth", tags=["auth"])
app.include_router(router=project_router, prefix="/projects", tags=["projects"])
app.include_router(router=session_router, prefix="/sessions", tags=["sessions"])
app.include_router(router=commit_router, prefix="/commits", tags=["commits"])
app.include_router(router=streak_router, prefix="/streaks", tags=["streaks"])


@app.get("/health")
def get_health():
    return {"status": "ok"}
