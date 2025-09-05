from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.models import Organization, User
from app.schemas import OrganizationOut, UserOut, UserCreateByAdmin, OrganizationUpdate
from database import get_db
from app.dependencies import get_current_user
from app.core.security import hash_password
from fastapi.responses import Response

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"]
)

# Update organization
@router.put("/update", response_model=OrganizationOut)
def update_organization(
    payload: OrganizationUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can update organization")

    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    org.name = payload.name
    org.description = payload.description
    db.commit()
    db.refresh(org)

    return org


# Get all users in organization (except current_user)
@router.get("/users", response_model=List[UserOut])
def get_users_in_organization(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    users = (
        db.query(User)
        .filter(
            User.organization_id == current_user.organization_id,
            User.id != current_user.id
        )
        .all()
    )
    return users


# Add user to organization (Admin only)
@router.post("/add-user", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def add_user_to_org(
    payload: UserCreateByAdmin,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can add user")

    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=payload.email,
        hash_password=hash_password(payload.password),
        full_name=payload.full_name,
        gender=payload.gender,
        role=payload.role,
        organization_id=current_user.organization_id,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# Delete user in organization (Admin only)
@router.delete("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_in_org(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can delete users")

    user = db.query(User).filter(
        User.id == user_id,
        User.organization_id == current_user.organization_id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found in your organization")

    db.delete(user)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
