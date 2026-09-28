from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.user_schema import UserCreate

from app.services.auth_service import (
    register_user,
    login_user,
    create_password_reset_otp,
    verify_password_reset_otp,
    reset_password
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

    # OAuth2PasswordRequestForm uses
    # "username".
    #
    # In our project this contains
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


# ============================================================
# FORGOT PASSWORD
# ============================================================

@router.post("/forgot-password")
def forgot_password(
    phone_number: str,
    db: Session = Depends(get_db)
):

    otp = create_password_reset_otp(
        db,
        phone_number
    )

    if otp is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone number not registered"
        )

    # DEVELOPMENT / TESTING ONLY
    #
    # In production this OTP should be
    # sent through an SMS provider.
    return {
        "message": "OTP generated successfully",
        "otp": otp
    }


# ============================================================
# VERIFY PASSWORD RESET OTP
# ============================================================

@router.post("/verify-reset-otp")
def verify_reset_otp(
    phone_number: str,
    otp: str,
    db: Session = Depends(get_db)
):

    reset_token = verify_password_reset_otp(
        db,
        phone_number,
        otp
    )

    if reset_token is None:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

    return {
        "message": "OTP verified successfully",
        "reset_token": reset_token
    }


# ============================================================
# RESET PASSWORD
# ============================================================

@router.post("/reset-password")
def reset_user_password(
    phone_number: str,
    reset_token: str,
    new_password: str,
    db: Session = Depends(get_db)
):

    if len(new_password) < 6:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )

    if len(
        new_password.encode("utf-8")
    ) > 72:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password cannot be longer than 72 bytes"
        )

    success = reset_password(
        db,
        phone_number,
        reset_token,
        new_password
    )

    if not success:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset request"
        )

    return {
        "message": "Password reset successfully"
    }