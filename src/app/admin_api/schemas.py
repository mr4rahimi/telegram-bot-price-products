from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


# --------- Categories ---------

class CategoryCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class CategoryUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class CategoryOut(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


# --------- Products ---------

class ProductCreate(BaseModel):
    category_id: int
    title: str = Field(min_length=1, max_length=300)
    image_ref: Optional[str] = None
    description: Optional[str] = None
    features_json: Optional[dict[str, Any]] = None


class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    title: Optional[str] = Field(default=None, min_length=1, max_length=300)
    image_ref: Optional[str] = None
    description: Optional[str] = None
    features_json: Optional[dict[str, Any]] = None


class ProductOut(BaseModel):
    id: int
    category_id: int
    title: str
    image_ref: Optional[str]
    description: Optional[str]
    features_json: Optional[dict[str, Any]]

    class Config:
        from_attributes = True