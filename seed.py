from sqlalchemy.orm import Session
from database import SessionLocal
from app.models import Organization, User, Project, Task
from app.core.security import hash_password
from datetime import datetime, timedelta, timezone
import uuid

db: Session = SessionLocal()

def seed():
    # --- Organization ---
    org = db.query(Organization).filter_by(name="Default Organization").first()
    if not org:
        org = Organization(
            id=uuid.uuid4(),
            name="Default Organization",
            description="Seeded default organization"
        )
        db.add(org)
        db.commit()
        db.refresh(org)

    # --- Users ---
    users_data = [
        {
            "email": "admin@taskapp.com",
            "password": "Admin123@",
            "full_name": "Admin User",
            "gender": "male",
            "role": "admin",
        },
        {
            "email": "manager@taskapp.com",
            "password": "Manager123@",
            "full_name": "Manager User",
            "gender": "female",
            "role": "manager",
        },
        {
            "email": "member@taskapp.com",
            "password": "Member123@",
            "full_name": "Member User",
            "gender": "male",
            "role": "member",
        },
    ]

    user_objs = []
    for u in users_data:
        user = db.query(User).filter_by(email=u["email"]).first()
        if not user:
            user = User(
                id=uuid.uuid4(),
                email=u["email"],
                hash_password=hash_password(u["password"]),
                full_name=u["full_name"],
                gender=u["gender"],
                role=u["role"],
                organization_id=org.id,
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        user_objs.append(user)

    admin, manager, member = user_objs

    # --- Project ---
    project = db.query(Project).filter_by(name="Sample Project").first()
    if not project:
        project = Project(
            id=uuid.uuid4(),
            name="Sample Project",
            description="A sample seeded project",
            organization_id=org.id
        )
        project.members.extend(user_objs)  # add all users as members
        db.add(project)
        db.commit()
        db.refresh(project)

    # --- Tasks ---
    tasks_data = [
        {
            "title": "Setup project repo",
            "description": "Initialize git repo and setup CI/CD",
            "status": "todo",
            "priority": "high",
            "assignee_id": member.id,
            "due_date": datetime.now(timezone.utc) + timedelta(days=3),
            "created_by": manager.id
        },
        {
            "title": "Design database schema",
            "description": "ERD + migrations",
            "status": "in_progress",
            "priority": "medium",
            "assignee_id": admin.id,
            "due_date": datetime.now(timezone.utc) + timedelta(days=5),
            "created_by": manager.id
        },
        {
            "title": "Implement task API",
            "description": "CRUD + status transition",
            "status": "done",
            "priority": "low",
            "assignee_id": member.id,
            "due_date": datetime.now(timezone.utc) - timedelta(days=1),  # overdue
            "created_by": admin.id
        },
    ]

    for t in tasks_data:
        task = db.query(Task).filter_by(title=t["title"], project_id=project.id).first()
        if not task:
            task = Task(
                id=uuid.uuid4(),
                project_id=project.id,
                title=t["title"],
                description=t["description"],
                status=t["status"],
                priority=t["priority"],
                assignee_id=t["assignee_id"],
                due_date=t["due_date"],
                created_by=t["created_by"]
            )
            db.add(task)
            db.commit()

    print("Seeding completed.")


if __name__ == "__main__":
    seed()
