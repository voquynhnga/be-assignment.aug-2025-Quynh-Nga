from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sqlalchemy.orm import Session
from typing import List

from app.models import Project, User
from app.schemas import ProjectOut, ProjectCreate
from database import get_db
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


# 👉 Create project
@router.post("/create", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # chỉ Admin/Manager được tạo
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to create project")

    new_project = Project(
        name=payload.name,
        description=payload.description,
        organization_id=current_user.organization_id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


# 👉 List all projects of user's organization
@router.get("/", response_model=List[ProjectOut])
def get_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    projects = db.query(Project).filter(Project.organization_id == current_user.organization_id).all()
    return projects


