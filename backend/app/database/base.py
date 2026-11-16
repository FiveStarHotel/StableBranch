from datetime import UTC, datetime
from typing import Any, ClassVar

from sqlalchemy import DateTime, TypeDecorator
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from backend.app.core.config import settings

engine = create_async_engine(
    url=settings.database_url,
    echo=settings.sqlalchemy_echo
)

SessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)

# MySQL хранит даты в наивном формате (без таймзон), мы используем время по Гринвичу (с таймзоной)
# Конструкция ниже позволяет ORM сохранять datetime в наивном формате в Гринвиче
# И отдавать наивный datetime в виде aware (с таймзоной)
class UTCDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime, dialect):
        if value is not None:
            if value.tzinfo is None:
                raise ValueError("Using naive datetime is prohibited! Use aware date time!")
            value = value.astimezone(UTC).replace(tzinfo=None)
        return value
    
    def process_result_value(self, value: datetime, dialect):
        if value is not None:
            value = value.replace(tzinfo=UTC)
        return value


class Base(DeclarativeBase):
    type_annotation_map: ClassVar[dict[Any, Any]] = {
        datetime: UTCDateTime
    }
