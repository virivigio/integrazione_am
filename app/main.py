import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import api, web
from app.session_manager import session_manager
from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background cleanup task
    task = asyncio.create_task(_cleanup_loop())
    yield
    task.cancel()


async def _cleanup_loop():
    while True:
        await asyncio.sleep(15 * 60)  # every 15 minutes
        session_manager.cleanup_expired()


app = FastAPI(title="Orders AI Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router)
app.include_router(web.router)
