from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.services.prediction_service import get_predictions

router = APIRouter(
    prefix="/prediction",
    tags=["Prediction History"]
)


@router.get("/")
def prediction_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_predictions(
        db,
        current_user.id
    )