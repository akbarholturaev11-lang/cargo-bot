from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from utils.constants import (
    DELIVERY_STATUS_NEW,
    STATUS_CHINA_RECEIVED,
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True)
    username: Mapped[str | None] = mapped_column(String(255))
    language: Mapped[str] = mapped_column(String(2))
    full_name: Mapped[str] = mapped_column(String(255))
    normalized_full_name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(32), unique=True)
    city: Mapped[str] = mapped_column(String(100))
    client_code: Mapped[str] = mapped_column(String(32), unique=True)
    status: Mapped[str] = mapped_column(String(32), default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    parcels: Mapped[list["Parcel"]] = relationship("Parcel", back_populates="user")
    delivery_requests: Mapped[list["DeliveryRequest"]] = relationship(
        "DeliveryRequest",
        back_populates="user",
    )


class Parcel(Base):
    __tablename__ = "parcels"

    id: Mapped[int] = mapped_column(primary_key=True)
    track_code: Mapped[str] = mapped_column(String(255))
    normalized_track_code: Mapped[str] = mapped_column(String(255), unique=True)
    client_code: Mapped[str] = mapped_column(String(32))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    destination_city: Mapped[str] = mapped_column(String(100))
    destination_warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouses.id"),
    )
    status_code: Mapped[str] = mapped_column(
        String(64),
        default=STATUS_CHINA_RECEIVED,
    )
    received_china_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    batch_date: Mapped[date | None] = mapped_column(Date)
    china_received_notified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    arrival_notified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    created_by_admin_id: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped["User"] = relationship("User", back_populates="parcels")
    destination_warehouse: Mapped["Warehouse | None"] = relationship(
        "Warehouse",
        back_populates="parcels",
    )
    delivery_requests: Mapped[list["DeliveryRequest"]] = relationship(
        "DeliveryRequest",
        back_populates="parcel",
    )


class Warehouse(Base):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(primary_key=True)
    city_key: Mapped[str] = mapped_column(String(64))
    city_name_tj: Mapped[str] = mapped_column(String(100))
    city_name_ru: Mapped[str] = mapped_column(String(100))
    address_caption: Mapped[str] = mapped_column(Text)
    image_file_id: Mapped[str | None] = mapped_column(String(255))
    media_type: Mapped[str] = mapped_column(String(16), default="photo", server_default="photo")
    media_file_id: Mapped[str | None] = mapped_column(String(255))
    tj_address_text: Mapped[str | None] = mapped_column(Text)
    tj_work_time: Mapped[str | None] = mapped_column(String(255))
    tj_phone: Mapped[str | None] = mapped_column(String(64))

    tj_pickup_caption: Mapped[str | None] = mapped_column(Text)
    tj_pickup_media_type: Mapped[str | None] = mapped_column(String(16))
    tj_pickup_media_file_id: Mapped[str | None] = mapped_column(String(255))

    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    parcels: Mapped[list["Parcel"]] = relationship(
        "Parcel",
        back_populates="destination_warehouse",
    )


class DeliveryRequest(Base):
    __tablename__ = "delivery_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    parcel_id: Mapped[int] = mapped_column(ForeignKey("parcels.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    track_code: Mapped[str] = mapped_column(String(255))
    destination_city: Mapped[str] = mapped_column(String(100))
    delivery_address: Mapped[str] = mapped_column(Text)
    delivery_phone: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default=DELIVERY_STATUS_NEW)
    handled_by_admin_id: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    parcel: Mapped["Parcel"] = relationship(
        "Parcel",
        back_populates="delivery_requests",
    )
    user: Mapped["User"] = relationship("User", back_populates="delivery_requests")


class Setting(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(255), unique=True)
    value: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
