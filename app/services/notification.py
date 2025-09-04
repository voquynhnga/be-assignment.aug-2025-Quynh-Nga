from sqlalchemy.orm import Session
from uuid import UUID
from app.models import Notification
from datetime import  timedelta

def create_notification(db: Session, task_id: UUID, user_id: UUID, message: str):
    """Create and save a notification for a user."""
    notif = Notification(
        user_id=user_id,
        message=message,
        is_read=False,
        task_id=task_id,
        type='task_assigned',
        title="Task Assigned" 

    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif
