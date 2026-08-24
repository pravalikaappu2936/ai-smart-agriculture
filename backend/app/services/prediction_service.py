from sqlalchemy.orm import Session

from app.models.prediction import Prediction


def save_prediction(
    db: Session,
    user_id: int,
    module: str,
    input_data: str,
    prediction: str,
    confidence: float = 0.0,
):

    record = Prediction(
        user_id=user_id,
        module=module,
        input_data=input_data,
        prediction=prediction,
        confidence=confidence
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def get_predictions(
    db: Session,
    user_id: int
):

    return db.query(Prediction).filter(
        Prediction.user_id == user_id
    ).all()