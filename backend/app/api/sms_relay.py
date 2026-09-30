import hashlib
import secrets
from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from pydantic import BaseModel

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.sms_relay_device import SmsRelayDevice
from app.models.sms_message import SmsMessage


router = APIRouter(
    prefix="/sms-relay",
    tags=["SMS Relay"]
)


# =========================================================
# BEARER SECURITY
# =========================================================

security = HTTPBearer()

# =========================================================
# SMS DELIVERY REPORT MODEL
# =========================================================

class SmsReport(BaseModel):

    sms_id: int

    status: str

    error_message: str | None = None


# =========================================================
# TOKEN HELPERS
# =========================================================

def hash_device_token(token: str) -> str:

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def generate_device_token() -> str:

    return secrets.token_urlsafe(32)


# =========================================================
# REGISTER DEVICE
# =========================================================

@router.post("/register")
def register_device(
    device_name: str,
    phone_number: str,
    db: Session = Depends(get_db)
):

    token = generate_device_token()

    token_hash = hash_device_token(token)

    device = SmsRelayDevice(
        device_name=device_name,
        phone_number=phone_number,
        device_token_hash=token_hash,
        is_active=True
    )

    db.add(device)
    db.commit()
    db.refresh(device)

    return {
        "message": "SMS relay device registered successfully",
        "device_id": device.id,
        "device_name": device.device_name,
        "device_token": token
    }


# =========================================================
# AUTHENTICATE DEVICE
# =========================================================

def get_relay_device(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    token_hash = hash_device_token(token)

    device = (
        db.query(SmsRelayDevice)
        .filter(
            SmsRelayDevice.device_token_hash == token_hash,
            SmsRelayDevice.is_active == True
        )
        .first()
    )

    if device is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid or inactive device token"
        )

    device.last_seen = datetime.utcnow()

    db.commit()

    return device


# =========================================================
# DEVICE STATUS
# =========================================================

@router.get("/status")
def relay_status(
    device: SmsRelayDevice = Depends(get_relay_device)
):

    return {
        "status": "connected",
        "device_id": device.id,
        "device_name": device.device_name,
        "phone_number": device.phone_number,
        "last_seen": device.last_seen
    }

# =========================================================
# DEACTIVATE DEVICE
# =========================================================

@router.post("/deactivate/{device_id}")
def deactivate_device(
    device_id: int,
    device: SmsRelayDevice = Depends(get_relay_device),
    db: Session = Depends(get_db)
):

    if device.id != device_id:

        raise HTTPException(
            status_code=403,
            detail="You can only deactivate your own device"
        )

    device.is_active = False

    db.commit()

    return {
        "message": "SMS relay device deactivated successfully",
        "device_id": device.id
    }
    
# =========================================================
# POLL FOR PENDING SMS
# =========================================================

@router.get("/poll")
def poll_sms(
    device: SmsRelayDevice = Depends(get_relay_device),
    db: Session = Depends(get_db)
):

    sms = (
        db.query(SmsMessage)
        .filter(
            SmsMessage.status == "pending",
            (
                SmsMessage.device_id == device.id
            ) | (
                SmsMessage.device_id.is_(None)
            )
        )
        .order_by(
            SmsMessage.created_at.asc()
        )
        .first()
    )

    if sms is None:

        return {
            "message_available": False
        }

    sms.status = "processing"
    sms.device_id = device.id
    sms.attempts += 1

    db.commit()
    db.refresh(sms)

    return {
        "message_available": True,
        "sms_id": sms.id,
        "phone_number": sms.phone_number,
        "message": sms.message
    }
    
# =========================================================
# CREATE TEST SMS
# =========================================================

@router.post("/test-sms")
def create_test_sms(
    phone_number: str,
    message: str,
    device: SmsRelayDevice = Depends(get_relay_device),
    db: Session = Depends(get_db)
):

    sms = SmsMessage(
        device_id=device.id,
        phone_number=phone_number,
        message=message,
        status="pending",
        attempts=0
    )

    db.add(sms)
    db.commit()
    db.refresh(sms)

    return {
        "message": "Test SMS added to queue",
        "sms_id": sms.id,
        "status": sms.status
    }
    
# =========================================================
# REPORT SMS DELIVERY
# =========================================================

@router.post("/report")
def report_sms(
    report: SmsReport,
    device: SmsRelayDevice = Depends(get_relay_device),
    db: Session = Depends(get_db)
):

    sms = (
        db.query(SmsMessage)
        .filter(
            SmsMessage.id == report.sms_id
        )
        .first()
    )

    if sms is None:

        raise HTTPException(
            status_code=404,
            detail="SMS message not found"
        )

    if sms.device_id != device.id:

        raise HTTPException(
            status_code=403,
            detail="SMS does not belong to this device"
        )

    if report.status not in ["sent", "failed"]:

        raise HTTPException(
            status_code=400,
            detail="Status must be 'sent' or 'failed'"
        )

    sms.status = report.status

    if report.status == "sent":

        sms.sent_at = datetime.utcnow()

        sms.error_message = None

    else:

        sms.error_message = report.error_message

    db.commit()

    return {
        "message": "SMS delivery report recorded",
        "sms_id": sms.id,
        "status": sms.status
    }