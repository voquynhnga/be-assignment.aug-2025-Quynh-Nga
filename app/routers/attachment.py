# app/routers/task_attachments.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import os
import shutil
import uuid
from pathlib import Path

from app.models import TaskAttachment, Task, User
from app.schemas import TaskAttachmentOut
from database import get_db
from app.dependencies import get_current_user, require_project_access
from config import settings

router = APIRouter(
    prefix="/tasks/{task_id}/attachments",
    tags=["Task Attachments"]
)

# Upload directory configuration
UPLOAD_DIR = Path("uploads/task_attachments")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Allowed file types
ALLOWED_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.txt', '.csv', '.jpg', '.jpeg', '.png', '.gif', '.bmp',
    '.zip', '.rar', '.7z', '.mp4', '.avi', '.mov', '.mp3', '.wav'
}

def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    # Check file size
    if hasattr(file.file, 'seek') and hasattr(file.file, 'tell'):
        file.file.seek(0, 2)  # Go to end
        file_size = file.file.tell()
        file.file.seek(0)  # Go back to start
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
            )
    
    # Check file extension
    if file.filename:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )

# Upload file attachment
@router.post("/", response_model=TaskAttachmentOut, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    task_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    require_project_access(task.project_id, db, current_user)
    # Check if user has access to the project
    # project = task.project
    # if current_user.role not in ["admin", "manager"]:
    #     member_ids = [m.id for m in project.members]
    #     if current_user.id not in member_ids:
    #         raise HTTPException(status_code=403, detail="Not authorized to upload to this task")
    
    # Validate file
    validate_file(file)
    
    # Generate unique filename
    file_uuid = str(uuid.uuid4())
    file_ext = Path(file.filename).suffix if file.filename else ""
    unique_filename = f"{file_uuid}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    try:
        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = file_path.stat().st_size
        
        # Create database record
        attachment = TaskAttachment(
            filename=unique_filename,
            original_filename=file.filename or "unknown",
            file_path=str(file_path),
            file_size=file_size,
            content_type=file.content_type or "application/octet-stream",
            task_id=task_id,
            upload_by=current_user.id
        )
        
        db.add(attachment)
        db.commit()
        db.refresh(attachment)
        
        return attachment
    
    except Exception as e:
        # Clean up file if database operation fails
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

# Get all attachments for a task
@router.get("/", response_model=List[TaskAttachmentOut])
def get_task_attachments(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if user has access to the project
    require_project_access(task.project_id, db, current_user)
    # project = task.project

    # if current_user.role not in ["admin", "manager"]:
    #     member_ids = [m.id for m in project.members]
    #     if current_user.id not in member_ids:
    #         raise HTTPException(status_code=403, detail="Not authorized to view attachments for this task")
    
    attachments = db.query(TaskAttachment).filter(
        TaskAttachment.task_id == task_id
    ).order_by(TaskAttachment.created_at.desc()).all()
    
    return attachments

# Get detail attachment 
@router.get("/{attachment_id}", response_model=TaskAttachmentOut)
def get_attachment(
    task_id: UUID,
    attachment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    require_project_access(task.project_id, db, current_user)
    

    # Check if attachment exists and belongs to the task
    attachment = db.query(TaskAttachment).filter(
        TaskAttachment.id == attachment_id,
        TaskAttachment.task_id == task_id
    ).first()
    
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    

    
    # Check if user has access to the project
    # task = attachment.task
    # # project = task.project
    # # if current_user.role not in ["admin", "manager"]:
    # #     member_ids = [m.id for m in project.members]
    # #     if current_user.id not in member_ids:
    # #         raise HTTPException(status_code=403, detail="Not authorized to view this attachment")
    
    return attachment

# Download file attachment
@router.get("/{attachment_id}/download")
def download_attachment(
    task_id: UUID,
    attachment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if attachment exists and belongs to the task
    attachment = db.query(TaskAttachment).filter(
        TaskAttachment.id == attachment_id,
        TaskAttachment.task_id == task_id
    ).first()
    
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    # Check if user has access to the project

    # task = attachment.task
    # project = task.project
    # if current_user.role not in ["admin", "manager"]:
    #     member_ids = [m.id for m in project.members]
    #     if current_user.id not in member_ids:
    #         raise HTTPException(status_code=403, detail="Not authorized to download this attachment")
    
    # Check if file exists on disk
    file_path = Path(attachment.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on server")
    
    return FileResponse(
        path=str(file_path),
        filename=attachment.original_filename,
        media_type=attachment.content_type
    )

# Delete attachment
@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attachment(
    task_id: UUID,
    attachment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if attachment exists and belongs to the task
    attachment = db.query(TaskAttachment).filter(
        TaskAttachment.id == attachment_id,
        TaskAttachment.task_id == task_id
    ).first()
    
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    # Check if user has access to the project
    task = db.query(Task).filter(Task.id == task_id).first()
    require_project_access(task.project_id, db, current_user)
    
    # Only the uploader or admin/manager can delete
    if attachment.upload_by != current_user.id and current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this attachment")
    
    # Delete file from disk
    file_path = Path(attachment.file_path)
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception:
            # Log error but don't fail the request
            pass
    
    # Delete database record
    db.delete(attachment)
    db.commit()
    
    return None

