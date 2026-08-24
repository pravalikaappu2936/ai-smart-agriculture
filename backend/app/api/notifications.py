from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.core.auth import (
    get_current_user
)

from app.models.user import User

from app.models.notification import (
    Notification
)

from app.schemas.notification_schema import (
    NotificationResponse
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# =========================================================
# GET ALL NOTIFICATIONS
# =========================================================

@router.get(
    "/",
    response_model=list[NotificationResponse]
)
def get_notifications(

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    )
):

    notifications = (

        db.query(
            Notification
        )

        .filter(
            Notification.user_id
            == current_user.id
        )

        .order_by(
            Notification.created_at.desc()
        )

        .all()
    )

    return notifications


# =========================================================
# GET UNREAD NOTIFICATIONS
# =========================================================

@router.get(
    "/unread",
    response_model=list[NotificationResponse]
)
def get_unread_notifications(

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    )
):

    notifications = (

        db.query(
            Notification
        )

        .filter(
            Notification.user_id
            == current_user.id,

            Notification.is_read == False
        )

        .order_by(
            Notification.created_at.desc()
        )

        .all()
    )

    return notifications


# =========================================================
# MARK ONE AS READ
# =========================================================

@router.put(
    "/{notification_id}/read"
)
def mark_notification_read(

    notification_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    )
):

    notification = (

        db.query(
            Notification
        )

        .filter(

            Notification.id
            == notification_id,

            Notification.user_id
            == current_user.id
        )

        .first()
    )

    if notification is None:

        raise HTTPException(
            status_code=404,
            detail="Notification not found."
        )

    notification.is_read = True

    db.commit()

    return {

        "status": "success",

        "message":
            "Notification marked as read."
    }


# =========================================================
# MARK ALL AS READ
# =========================================================

@router.put(
    "/read-all"
)
def mark_all_notifications_read(

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    )
):

    notifications = (

        db.query(
            Notification
        )

        .filter(

            Notification.user_id
            == current_user.id,

            Notification.is_read == False
        )

        .all()
    )

    for notification in notifications:

        notification.is_read = True

    db.commit()

    return {

        "status": "success",

        "message":
            "All notifications marked as read."
    }