from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import json
import redis

from app.models import Project, User, Task, Notification
from app.schemas import NotificationOut
from database import get_db
from app.dependencies import get_current_user
from app.services.notification import create_notification


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)

redis_client = redis.Redis(host="localhost", port=6379, password="redis123", db=0, decode_responses=True)

CACHE_TTL = 60 # seconds

@router.get("/", response_model=List[NotificationOut])
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cache_key = f"user:{current_user.id}:notifications"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        return [NotificationOut(**notif) for notif in json.loads(cached_data)]

    notifs = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    redis_client.setex(cache_key, CACHE_TTL, json.dumps([n.as_dict() for n in notifs]))
    return notifs


@router.put("/{notif_id}/read", response_model=NotificationOut)
def mark_as_read(
    notif_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notif = (
        db.query(Notification)
        .filter(Notification.id == notif_id, Notification.user_id == current_user.id)
        .first()
    )
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.is_read = True
    db.commit()
    db.refresh(notif)

    cache_key = f"user:{current_user.id}:notifications"
    redis_client.delete(cache_key)

    return notif

