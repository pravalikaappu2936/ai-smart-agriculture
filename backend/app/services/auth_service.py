from sqlalchemy.orm import Session

from app.models.user import User

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
        raise ValueError("Username already registered")

    # Check whether phone number already exists
    existing_phone = db.query(User).filter(
        User.phone_number == phone_number
    ).first()

    if existing_phone:
        raise ValueError("Phone number already registered")

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

