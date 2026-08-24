from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.core.security import decode_access_token


# ============================================================
# OAUTH2 CONFIGURATION
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# ============================================================
# GET CURRENT USER
# ============================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get the currently logged-in user
    using the JWT access token.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    # --------------------------------------------------------
    # DECODE TOKEN
    # --------------------------------------------------------

    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    # --------------------------------------------------------
    # GET PHONE NUMBER FROM JWT
    # --------------------------------------------------------

    phone_number = payload.get("sub")

    if phone_number is None:
        raise credentials_exception

    # --------------------------------------------------------
    # FIND USER
    # --------------------------------------------------------

    user = db.query(User).filter(
        User.phone_number == str(phone_number)
    ).first()

    if user is None:
        raise credentials_exception

    return user