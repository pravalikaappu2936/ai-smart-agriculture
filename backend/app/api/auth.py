from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.user_schema import UserCreate

from app.services.auth_service import (
    register_user,
    login_user
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ========================================
# REGISTER
# ========================================

@router.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    try:

        new_user = register_user(
            db,
            user.username,
            user.phone_number,
            user.password
        )

        return {
            "message": "User registered successfully",
            "username": new_user.username,
            "phone_number": new_user.phone_number
        }

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ========================================
# LOGIN
# ========================================

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # OAuth2PasswordRequestForm uses the field
    # "username". In our project this contains
    # the user's phone number.

    phone_number = form_data.username

    result = login_user(
        db,
        phone_number,
        form_data.password
    )

    if result is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    return result

