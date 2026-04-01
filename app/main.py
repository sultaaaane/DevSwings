from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import create_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    yield


app = FastAPI(title="DevPulse", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def get_health():
    return {"status": "ok"}
