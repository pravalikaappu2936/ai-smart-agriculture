from sqlalchemy import Column, Integer, String, DateTime

from app.database.database import Base


class PasswordReset(Base):

    __tablename__ = "password_resets"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    phone_number = Column(
        String,
        nullable=False,
        index=True
    )

    otp_hash = Column(
        String,
        nullable=False
    )

    expires_at = Column(
        DateTime,
        nullable=False
    )

    attempts = Column(
        Integer,
        default=0,
        nullable=False
    )

    reset_token_hash = Column(
        String,
        nullable=True
    )

    token_expires_at = Column(
        DateTime,
        nullable=True
    )