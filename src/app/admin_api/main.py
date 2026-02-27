from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import ping_db
from app.admin_api.security import require_admin


def create_app() -> FastAPI:
    app = FastAPI(title="Telegram Bot Admin API", version="0.1.0")

    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.get("/api/me")
    def me(username: str = Depends(require_admin)):
        return {"username": username}

    @app.get("/api/db/ping")
    def db_ping(username: str = Depends(require_admin)):
        # if it fails, FastAPI returns 500 and you see stacktrace in logs
        ping_db()
        return {"db": "ok"}

    return app


app = create_app()