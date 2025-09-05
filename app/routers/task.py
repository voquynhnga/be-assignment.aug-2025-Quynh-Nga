from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.models import Task, User, Project
from app.schemas import TaskOut, TaskCreate, TaskUpdate
from database import get_db
from app.dependencies import require_project_access, get_current_user
from app.services.notification import create_notification

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],

)

# Create a new task
@router.post("/create", response_model=TaskOut)
def create_task(
    project_id: UUID,
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_access),
):
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Not authorized to create task in this project")
    
    if payload.assignee_id:
        project = db.query(Project).filter(Project.id == project_id).first()
        member_ids = [m.id for m in project.members]
        if payload.assignee_id not in member_ids:
            raise HTTPException(status_code=400, detail="Assignee must be a member of this project")

    task = Task(
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        due_date=payload.due_date,
        project_id=project_id,
        assignee_id=payload.assignee_id,
        created_by=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Notification: if assigned
    if payload.assignee_id and payload.assignee_id != current_user.id:
        create_notification(db, task.id, payload.assignee_id, f"You have been assigned task '{task.title}'")

    return task


# List tasks in a project
@router.get("/project/{project_id}", response_model=List[UUID])
def list_tasks(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_project_access(project_id, db, current_user)
    task_ids = db.query(Task.id).filter(Task.project_id == project_id).all()
    return [tid for (tid,) in task_ids]


# Get task details
@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    
):
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    require_project_access(task.project_id, db, current_user)
    
    return task


# Update task
@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user), 
):
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    require_project_access(task.project_id, db, current_user)
    
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")

    if payload.status:
        valid_transitions = {
            "todo": ["in_progress"],
            "in_progress": ["done"],
            "done": []
        }
        if task.status not in valid_transitions:
            raise HTTPException(status_code=400, detail="Invalid current status")        
        if payload.status not in valid_transitions[task.status]:
            raise HTTPException(status_code=400, detail="Invalid status transition")
    
    if payload.assignee_id:
        project = db.query(Project).filter(Project.id == task.project_id).first()
        member_ids = [m.id for m in project.members]
        if payload.assignee_id not in member_ids:
            raise HTTPException(status_code=400, detail="Assignee must be a member of this project")

    old_assignee = task.assignee_id

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)


    db.commit()
    db.refresh(task)

    # Notifications
    if payload.status:
        create_notification(db, task.id, task.assignee_id, f"Task '{task.title}' moved to {task.status}")

    if payload.assignee_id and payload.assignee_id != old_assignee:
        create_notification(db, task.id, payload.assignee_id, f"You have been assigned task '{task.title}'")
        if old_assignee:
            create_notification(db, task.id, old_assignee, f"Your task '{task.title}' has been reassigned")  

    return task


# Delete task
@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user), 
):
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    require_project_access(task.project_id, db, current_user)

    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")
    if task.assignee_id and task.assignee_id != current_user.id:
        create_notification(db, task_id, task.assignee_id, f"Task '{task.title}' has been deleted")

    db.delete(task)
    db.commit()
    return None
