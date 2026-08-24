from sqlalchemy.orm import Session

from app.models.user import User
from app.models.prediction import Prediction


def get_dashboard_statistics(db: Session):

    total_users = db.query(User).count()

    total_predictions = db.query(Prediction).count()

    return {
        "total_users": total_users,
        "total_predictions": total_predictions
    }