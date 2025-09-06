from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Integer, String, Boolean, Text, Double, ForeignKey, TIMESTAMP, JSON
from .db import Base

class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(32), default="rakumachi")
    source_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    url: Mapped[str | None] = mapped_column(Text, unique=True, nullable=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    prefecture: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(Text, nullable=True)
    ward: Mapped[str | None] = mapped_column(Text, nullable=True)
    station_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    station_walk_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_yen: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    area_m2: Mapped[float | None] = mapped_column(Double, nullable=True)
    land_area_m2: Mapped[float | None] = mapped_column(Double, nullable=True)
    floor_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    built_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    age_years: Mapped[float | None] = mapped_column(Double, nullable=True)
    structure: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True))
    first_seen_at: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True))
    last_seen_at: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    raw: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    valuations: Mapped[list["Valuation"]] = relationship("Valuation", back_populates="listing")

class Valuation(Base):
    __tablename__ = "valuations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("listings.id", ondelete="CASCADE"))
    model_version: Mapped[str] = mapped_column(Text)
    scored_at: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True))
    y_true: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    y_pred: Mapped[float | None] = mapped_column(Double, nullable=True)
    residual: Mapped[float | None] = mapped_column(Double, nullable=True)
    residual_pct: Mapped[float | None] = mapped_column(Double, nullable=True)

    listing: Mapped[Listing] = relationship("Listing", back_populates="valuations")
