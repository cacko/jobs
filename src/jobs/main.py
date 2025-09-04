from fastapi import FastAPI
from .routers import api
from fastapi.middleware.cors import CORSMiddleware
from jobs.config import app_config
import asyncio
from fastapi.staticfiles import StaticFiles
from pathlib import Path

ASSETS_PATH = Path(__file__).parent.parent / "assets"


def create_app():
    app = FastAPI(
        title="jobs@cacko.net",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        redoc_url="/api/redoc",
    )

    origins = ["http://localhost:4200", "http://localhost:5173", "https://jobs.cacko.net"]

    assets_path = Path(app_config.api.assets)
    if not assets_path.exists():
        assets_path.mkdir(parents=True, exist_ok=True)

    app.mount(
        "/api/assets", StaticFiles(directory=assets_path.as_posix()), name="assets"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["x-pagination-page", "x-pagination-total", "x-pagination-next"],
    )

    app.include_router(api.router)
    return app
