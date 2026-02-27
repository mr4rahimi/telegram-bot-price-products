from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.admin_api.security import require_admin
from app.admin_api.schemas import ProductCreate, ProductOut, ProductUpdate
from app.core.db import get_db
from app.core.models import Product, Category

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
def list_products(
    category_id: int | None = Query(default=None),
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    stmt = select(Product).order_by(Product.id.desc())
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)

    items = db.execute(stmt).scalars().all()
    return items


@router.get("/{product_id}", response_model=ProductOut)
def get_product(
    product_id: int,
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    obj = db.get(Product, product_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Product not found")
    return obj


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    cat = db.get(Category, payload.category_id)
    if not cat:
        raise HTTPException(status_code=400, detail="Invalid category_id")

    obj = Product(
        category_id=payload.category_id,
        title=payload.title,
        image_ref=payload.image_ref,
        description=payload.description,
        features_json=payload.features_json,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    obj = db.get(Product, product_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Product not found")

    if payload.category_id is not None:
        cat = db.get(Category, payload.category_id)
        if not cat:
            raise HTTPException(status_code=400, detail="Invalid category_id")
        obj.category_id = payload.category_id

    if payload.title is not None:
        obj.title = payload.title

    # این‌ها اگر None هم باشند یعنی پاک کن
    if payload.image_ref is not None:
        obj.image_ref = payload.image_ref
    if payload.description is not None:
        obj.description = payload.description
    if payload.features_json is not None:
        obj.features_json = payload.features_json

    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    obj = db.get(Product, product_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(obj)
    db.commit()
    return None