# app/routers/task_comments.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.models import TaskComment, Task, User
from app.schemas import TaskCommentOut, TaskCommentCreate
from database import get_db
from app.dependencies import get_current_user, require_project_access
from app.services.notification import create_notification

router = APIRouter(
    prefix="/tasks/{task_id}/comments",
    tags=["Task Comments"]
)

# Create a comment on a task
@router.post("/", response_model=TaskCommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(
    task_id: UUID,
    payload: TaskCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    require_project_access(task.project_id, db, current_user)
    
    # Create comment
    comment = TaskComment(
        content=payload.content,
        task_id=task_id,
        user_id=current_user.id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    # Send notification to task assignee (if not the same user)
    if task.assignee_id and task.assignee_id != current_user.id:
        create_notification(
            db, 
            task_id, 
            task.assignee_id, 
            f"New comment on task '{task.title}' by {current_user.full_name}"
        )
    
    # Also notify task creator if different from assignee and commenter
    if (task.created_by != current_user.id and 
        task.created_by != task.assignee_id):
        create_notification(
            db,
            task_id,
            task.created_by,
            f"New comment on task '{task.title}' by {current_user.name}"
        )
    
    return comment

# Get all comments for a task
@router.get("/", response_model=List[TaskCommentOut])
def get_task_comments(
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
    comments = db.query(TaskComment).filter(
        TaskComment.task_id == task_id
    ).order_by(TaskComment.created_at.asc()).all()
    
    return comments

# Update a comment
@router.put("/{comment_id}", response_model=TaskCommentOut)
def update_comment(
    task_id: UUID,
    comment_id: UUID,
    payload: TaskCommentCreate,  # Reuse the same schema
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(TaskComment).filter(
        TaskComment.id == comment_id,
        TaskComment.task_id == task_id
    ).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Only the comment author or admin/manager can update
    if comment.user_id != current_user.id and current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")
    
    comment.content = payload.content
    db.commit()
    db.refresh(comment)
    
    return comment

# Delete a comment
@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    task_id: UUID,
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(TaskComment).filter(
        TaskComment.id == comment_id,
        TaskComment.task_id == task_id
    ).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Only the comment author or admin/manager can delete
    if comment.user_id != current_user.id and current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    db.delete(comment)
    db.commit()
    
    return None