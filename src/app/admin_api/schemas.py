from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


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
    image_url: Optional[str] = None
    basalam_url: Optional[str] = None
    snappshop_url: Optional[str] = None
    website_url: Optional[str] = None
    tapsishop_url: Optional[str] = None
    mymonta_url: Optional[str] = None
    description: Optional[str] = None


class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    title: Optional[str] = Field(default=None, min_length=1, max_length=300)
    image_url: Optional[str] = None
    basalam_url: Optional[str] = None
    snappshop_url: Optional[str] = None
    website_url: Optional[str] = None
    tapsishop_url: Optional[str] = None
    mymonta_url: Optional[str] = None
    description: Optional[str] = None


class ProductOut(BaseModel):
    id: int
    category_id: int
    title: str
    image_url: Optional[str]
    basalam_url: Optional[str]
    snappshop_url: Optional[str]
    website_url: Optional[str]
    tapsishop_url: Optional[str]
    mymonta_url: Optional[str]
    description: Optional[str]

    class Config:
        from_attributes = True


# --------- Upload ---------

class UploadOut(BaseModel):
    url: str  # مثلاً /uploads/abc123.jpg