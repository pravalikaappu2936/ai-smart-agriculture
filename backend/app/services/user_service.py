from sqlalchemy.orm import Session

from app.models.user import User


def get_all_users(db: Session):

    return db.query(User).all()


def get_user_by_id(
    db: Session,
    user_id: int
):

    return db.query(User).filter(
        User.id == user_id
    ).first()


def get_user_by_phone(
    db: Session,
    phone_number: str
):

    return db.query(User).filter(
        User.phone_number == phone_number
    ).first()


def register_user(
    db: Session,
    username: str,
    phone_number: str,
    password: str
):

    from app.core.security import hash_password

    hashed_password = hash_password(password)

    user = User(
        username=username,
        phone_number=phone_number,
        password=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

