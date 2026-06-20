from pathlib import Path

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.db import ping_db
from app.admin_api.security import require_admin
from app.admin_api.routers.categories import router as categories_router
from app.admin_api.routers.products import router as products_router
from app.admin_api.routers.uploads import router as uploads_router

from fastapi.responses import FileResponse

UPLOAD_DIR = Path(__file__).resolve().parents[3] / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


FRONT_DIR = Path(__file__).resolve().parents[3] / "admin-panel" / "dist"

def create_app() -> FastAPI:
    app = FastAPI(title="Telegram Bot Admin API", version="0.3.0")

    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Serve uploaded images as static files
    app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.get("/api/me")
    def me(username: str = Depends(require_admin)):
        return {"username": username}

    @app.get("/api/db/ping")
    def db_ping(username: str = Depends(require_admin)):
        ping_db()
        return {"db": "ok"}

    app.include_router(categories_router)
    app.include_router(products_router)
    app.include_router(uploads_router)

    # فایل‌های static (js/css)
    app.mount("/assets", StaticFiles(directory=FRONT_DIR / "assets"), name="assets")

    # صفحه اصلی
    @app.get("/")
    def serve_admin():
        return FileResponse(FRONT_DIR / "index.html")

    # برای React Router
    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        return FileResponse(FRONT_DIR / "index.html")

    return app


app = create_app()