from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime
)

from sqlalchemy.sql import func

from app.database.database import Base


class SmsRelayDevice(Base):

    __tablename__ = "sms_relay_devices"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    device_name = Column(
        String,
        nullable=False
    )

    phone_number = Column(
        String,
        nullable=False
    )

    device_token_hash = Column(
        String,
        nullable=False,
        unique=True,
        index=True
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    last_seen = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )