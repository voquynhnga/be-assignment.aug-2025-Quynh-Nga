from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.models import Project, User, Task, TaskStatus
from app.schemas import ProjectOut, ProjectCreate, TaskOut
from database import get_db
from app.dependencies import get_current_user
from sqlalchemy import func
from datetime import timezone, datetime
from sqlalchemy import exists
from app.models import project_members

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

# Create project
@router.post("/create", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to create project")

    # check duplicate name in org
    existing = (
        db.query(Project)
        .filter(Project.organization_id == current_user.organization_id, Project.name == payload.name)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Project name already exists in this organization")

    new_project = Project(
        name=payload.name,
        description=payload.description,
        organization_id=current_user.organization_id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    # add creator as member
    user = db.merge(current_user)   
    new_project.members.append(user)
    db.commit()
    return new_project


# Get all projects of the current user
@router.get("/")
def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project_ids = db.query(Project.id).filter(
        Project.organization_id == current_user.organization_id
    )

    if current_user.role == "member":
        project_ids = project_ids.join(Project.members).filter(User.id == current_user.id)

    return [pid for (pid,) in project_ids.all()]



# Get project detail
@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.organization_id == current_user.organization_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # member must be in project to view
    if current_user.role == "member" and current_user not in project.members:
        raise HTTPException(status_code=403, detail="Not authorized to view this project")

    return project


# Update project
@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: UUID,
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to update project")

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.organization_id == current_user.organization_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # check duplicate name (excluding itself)
    existing = (
        db.query(Project)
        .filter(Project.organization_id == current_user.organization_id,
                Project.name == payload.name,
                Project.id != project_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Project name already exists in this organization")

    project.name = payload.name
    project.description = payload.description
    db.commit()
    db.refresh(project)
    return project


# Delete project
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete project")

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.organization_id == current_user.organization_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Add member
@router.post("/{project_id}/members")
def add_member(
    project_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to add member")

    project = db.query(Project).filter_by(id=project_id, organization_id=current_user.organization_id).first()
    user = db.query(User).filter_by(id=user_id, organization_id=current_user.organization_id).first()

    if not project or not user:
        raise HTTPException(status_code=404, detail="Project or user not found")

    if user in project.members:
        raise HTTPException(status_code=400, detail="Already a member")

    project.members.append(user)
    db.commit()
    return {"message": "Member added successfully"}


# Remove member
@router.delete("/{project_id}/members/{user_id}")
def remove_member(
    project_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to remove member")

    project = db.query(Project).filter_by(id=project_id, organization_id=current_user.organization_id).first()
    user = db.query(User).filter_by(id=user_id, organization_id=current_user.organization_id).first()

    if not project or not user:
        raise HTTPException(status_code=404, detail="Project or user not found")

    if user not in project.members:
        raise HTTPException(status_code=400, detail="User not in project")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot remove yourself from the project")

    # manager can't remove admin/manager
    if current_user.role == "manager" and user.role in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Managers cannot remove admins/managers")

    project.members.remove(user)
    db.commit()
    return {"message": "Member removed successfully"}

#Count of tasks by status in a project
@router.get("/{project_id}/report/status")
def task_status_report(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    is_member = db.query(
        exists().where(
            (project_members.c.project_id == project_id) &
            (project_members.c.user_id == current_user.id)
        )
    ).scalar()

    if not is_member:
        raise HTTPException(status_code=403, detail="Not authorized")

    result = (
        db.query(Task.status, func.count(Task.id))
        .filter(Task.project_id == project_id)
        .group_by(Task.status)
        .all()
    )
    return {status: count for status, count in result}

#List of overdue tasks in a project
@router.get("/{project_id}/report/overdue", response_model=List[TaskOut])
def overdue_tasks(project_id: UUID, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    tasks = (
        db.query(Task)
        .filter(Task.project_id == project_id, Task.due_date < now, Task.status != 'done')
        .all()
    )
    return tasks

