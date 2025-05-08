from datetime import datetime, timezone

from sqlalchemy import MetaData, String, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config import settings


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    metadata = MetaData(naming_convention=settings.db.naming_convention)


class Car(Base):
    __tablename__ = 'cars'

    url: Mapped[str] = mapped_column(String(1024), unique=True)
    title: Mapped[str] = mapped_column(String(512), index=True)
    price_usd: Mapped[int]
    odometer: Mapped[int]
    username: Mapped[str] = mapped_column(String(255))
    phone_number: Mapped[str] = mapped_column(String(100))
    image_url: Mapped[str] = mapped_column(String(1024))
    images_count: Mapped[int]
    car_number: Mapped[str | None] = mapped_column(String(20))
    car_vin: Mapped[str | None] = mapped_column(String(30), unique=True)
    datetime_found: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        server_default=func.now(),
    )
