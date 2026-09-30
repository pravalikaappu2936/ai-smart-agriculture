from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

from sqlalchemy.sql import func

from app.database.database import Base


class SmsMessage(Base):

    __tablename__ = "sms_messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    device_id = Column(
        Integer,
        ForeignKey("sms_relay_devices.id"),
        nullable=True,
        index=True
    )

    phone_number = Column(
        String,
        nullable=False,
        index=True
    )

    message = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        nullable=False,
        default="pending",
        index=True
    )

    attempts = Column(
        Integer,
        nullable=False,
        default=0
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    sent_at = Column(
        DateTime,
        nullable=True
    )

    error_message = Column(
        String,
        nullable=True
    )