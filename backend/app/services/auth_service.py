from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.password_reset import PasswordReset

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)


# ========================================
# REGISTER USER
# ========================================

def register_user(
    db: Session,
    username: str,
    phone_number: str,
    password: str
):
    # Check whether username already exists
    existing_username = db.query(User).filter(
        User.username == username
    ).first()

    if existing_username:
        raise ValueError(
            "Username already registered"
        )

    # Check whether phone number already exists
    existing_phone = db.query(User).filter(
        User.phone_number == phone_number
    ).first()

    if existing_phone:
        raise ValueError(
            "Phone number already registered"
        )

    # Hash password before storing it
    hashed_password = hash_password(password)

    # Create user
    user = User(
        username=username,
        phone_number=phone_number,
        password=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# ========================================
# AUTHENTICATE USER
# ========================================

def authenticate_user(
    db: Session,
    phone_number: str,
    password: str
):
    # Find user using phone number
    user = db.query(User).filter(
        User.phone_number == phone_number
    ).first()

    if user is None:
        return None

    # Verify password
    password_valid = verify_password(
        password,
        user.password
    )

    if not password_valid:
        return None

    return user


# ========================================
# LOGIN USER
# ========================================

def login_user(
    db: Session,
    phone_number: str,
    password: str
):
    user = authenticate_user(
        db,
        phone_number,
        password
    )

    if user is None:
        return None

    # Create JWT token
    access_token = create_access_token(
        data={
            "sub": str(user.phone_number)
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ============================================================
# CREATE PASSWORD RESET OTP
# ============================================================

def create_password_reset_otp(
    db: Session,
    phone_number: str
):

    # Find user
    user = db.query(User).filter(
        User.phone_number == phone_number
    ).first()

    if user is None:
        return None

    # Generate six-digit OTP
    otp = f"{secrets.randbelow(1000000):06d}"

    # Hash OTP before storing
    otp_hash = hashlib.sha256(
        otp.encode("utf-8")
    ).hexdigest()

    # Delete previous reset requests
    db.query(PasswordReset).filter(
        PasswordReset.phone_number == phone_number
    ).delete(
        synchronize_session=False
    )

    # Create new reset record
    reset = PasswordReset(
        phone_number=phone_number,
        otp_hash=otp_hash,
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(minutes=10)
        ),
        attempts=0,
        reset_token_hash=None,
        token_expires_at=None
    )

    db.add(reset)
    db.commit()

    # DEVELOPMENT ONLY
    return otp


# ============================================================
# VERIFY PASSWORD RESET OTP
# ============================================================

def verify_password_reset_otp(
    db: Session,
    phone_number: str,
    otp: str
):

    reset = db.query(PasswordReset).filter(
        PasswordReset.phone_number == phone_number
    ).first()

    if reset is None:
        return None

    # Maximum OTP attempts
    if reset.attempts >= 5:
        return None

    # Increase attempt count
    reset.attempts += 1

    # Check OTP expiry
    now = datetime.now(timezone.utc)

    expires_at = reset.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    if now > expires_at:
        db.commit()
        return None

    # Hash supplied OTP
    otp_hash = hashlib.sha256(
        otp.encode("utf-8")
    ).hexdigest()

    # Compare OTP hashes
    if otp_hash != reset.otp_hash:
        db.commit()
        return None

    # Generate temporary reset token
    reset_token = secrets.token_urlsafe(32)

    reset_token_hash = hashlib.sha256(
        reset_token.encode("utf-8")
    ).hexdigest()

    reset.reset_token_hash = reset_token_hash

    reset.token_expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=10)
    )

    db.commit()

    return reset_token


# ============================================================
# RESET PASSWORD
# ============================================================

def reset_password(
    db: Session,
    phone_number: str,
    reset_token: str,
    new_password: str
):

    reset = db.query(PasswordReset).filter(
        PasswordReset.phone_number == phone_number
    ).first()

    if reset is None:
        return False

    if reset.reset_token_hash is None:
        return False

    # Check token expiry
    now = datetime.now(timezone.utc)

    token_expires_at = reset.token_expires_at

    if token_expires_at is None:
        return False

    if token_expires_at.tzinfo is None:
        token_expires_at = token_expires_at.replace(
            tzinfo=timezone.utc
        )

    if now > token_expires_at:
        return False

    # Hash supplied reset token
    token_hash = hashlib.sha256(
        reset_token.encode("utf-8")
    ).hexdigest()

    # Verify reset token
    if token_hash != reset.reset_token_hash:
        return False

    # Find user
    user = db.query(User).filter(
        User.phone_number == phone_number
    ).first()

    if user is None:
        return False

    # Hash new password using existing bcrypt system
    user.password = hash_password(
        new_password
    )

    # Delete reset record after successful reset
    db.delete(reset)

    db.commit()

    return True