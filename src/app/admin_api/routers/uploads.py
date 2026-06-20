from __future__ import annotations

import uuid
import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles

from app.admin_api.security import require_admin
from app.admin_api.schemas import UploadOut

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

# پوشه آپلود — کنار src قرار می‌گیره
UPLOAD_DIR = Path(__file__).resolve().parents[4] / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE_MB = 5


@router.post("", response_model=UploadOut)
async def upload_image(
    file: UploadFile = File(...),
    _admin: str = Depends(require_admin),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, WEBP, GIF allowed")

    contents = await file.read()

    if len(contents) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large (max {MAX_SIZE_MB}MB)")

    ext = Path(file.filename or "img.jpg").suffix.lower() or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    dest = UPLOAD_DIR / filename

    dest.write_bytes(contents)

    return UploadOut(url=f"/uploads/{filename}")