from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.admin_api.security import require_admin
from app.admin_api.schemas import ProductCreate, ProductOut, ProductUpdate
from app.core.db import get_db
from app.db.models import Product, Category
from app.db.models import Offer, OfferPlatform

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
    return db.execute(stmt).scalars().all()


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
    if not db.get(Category, payload.category_id):
        raise HTTPException(status_code=400, detail="Invalid category_id")

    obj = Product(
        category_id=payload.category_id,
        title=payload.title,
        image_url=payload.image_url,
        basalam_url=payload.basalam_url,
        snappshop_url=payload.snappshop_url,
        website_url=payload.website_url,
        tapsishop_url=payload.tapsishop_url,
        mymonta_url=payload.mymonta_url,
        description=payload.description,
    )
    db.add(obj)
    db.flush()

    if payload.basalam_url:
        db.add(Offer(product_id=obj.id, platform=OfferPlatform.basalam, url=payload.basalam_url))
    if payload.snappshop_url:
        db.add(Offer(product_id=obj.id, platform=OfferPlatform.snappshop, url=payload.snappshop_url))
    if payload.website_url:
        db.add(Offer(product_id=obj.id, platform=OfferPlatform.direct, url=payload.website_url))
    if payload.tapsishop_url:
        db.add(Offer(product_id=obj.id, platform=OfferPlatform.tapsishop, url=payload.tapsishop_url))
    if payload.mymonta_url:
        db.add(Offer(product_id=obj.id, platform=OfferPlatform.mymonta, url=payload.mymonta_url))

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
        if not db.get(Category, payload.category_id):
            raise HTTPException(status_code=400, detail="Invalid category_id")
        obj.category_id = payload.category_id

    for field in ("title", "image_url", "basalam_url", "snappshop_url", "website_url",
                  "tapsishop_url", "mymonta_url", "description"):
        val = getattr(payload, field)
        if val is not None:
            setattr(obj, field, val)

    offers = db.execute(select(Offer).where(Offer.product_id == obj.id)).scalars().all()

    def sync(platform: OfferPlatform, url: str | None):
        existing = next((o for o in offers if o.platform == platform), None)
        if url:
            if existing:
                existing.url = url
            else:
                db.add(Offer(product_id=obj.id, platform=platform, url=url))
        else:
            if existing:
                db.delete(existing)

    sync(OfferPlatform.basalam, payload.basalam_url)
    sync(OfferPlatform.snappshop, payload.snappshop_url)
    sync(OfferPlatform.direct, payload.website_url)
    sync(OfferPlatform.tapsishop, payload.tapsishop_url)
    sync(OfferPlatform.mymonta, payload.mymonta_url)

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

    # حذف offer ها
    db.query(Offer).filter(Offer.product_id == product_id).delete()

    db.delete(obj)
    db.commit()