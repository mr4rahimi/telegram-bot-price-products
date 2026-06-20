from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.admin_api.security import require_admin
from app.admin_api.schemas import CategoryCreate, CategoryOut, CategoryUpdate
from app.core.db import get_db
from app.db.models import Category

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    items = db.execute(select(Category).order_by(Category.id.desc())).scalars().all()
    return items


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    obj = Category(
    title=payload.title,
    sort_order=0,
    is_active=True,
)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    obj = db.get(Category, category_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Category not found")

    obj.title = payload.title
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    obj = db.get(Category, category_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # معمولاً به خاطر FK محصولات داخل دسته
        raise HTTPException(
            status_code=409,
            detail="Cannot delete category: it has products (or related records).",
        )
    return None