import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class OfferPlatform(str, enum.Enum):
    basalam = "basalam"
    snappshop = "snappshop"
    direct = "direct"
    tapsishop = "tapsishop"
    mymonta = "mymonta"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sort_order: Mapped[int] = mapped_column(
    Integer,
    default=0,
    server_default="0",
    nullable=False
)
    is_active: Mapped[bool] = mapped_column(
    Boolean,
    default=True,
    server_default="true",
    nullable=False
)

    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(300), nullable=False)

    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    basalam_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    snappshop_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tapsishop_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    mymonta_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    category: Mapped["Category"] = relationship(back_populates="products")
    offers: Mapped[list["Offer"]] = relationship(back_populates="product")

class Offer(Base):
    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)

    platform: Mapped[OfferPlatform] = mapped_column(Enum(OfferPlatform), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)

    vendor_id: Mapped[str | None] = mapped_column(String(100), nullable=True)


    price_last: Mapped[int | None] = mapped_column(Integer, nullable=True) 
    price_updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    ttl_seconds: Mapped[int] = mapped_column(Integer, default=28800)

    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    product: Mapped["Product"] = relationship(back_populates="offers")
    #snappshop: Mapped["SnappshopOffer"] = relationship(back_populates="offer", uselist=False)