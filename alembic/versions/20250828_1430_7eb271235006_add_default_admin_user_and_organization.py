"""Add default admin user and organization

Revision ID: 7eb271235006
Revises: 23332a6bd36d
Create Date: 2025-08-28 14:30:24.726731+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import os
from passlib.hash import bcrypt

# revision identifiers, used by Alembic.
revision: str = '7eb271235006'
down_revision: Union[str, Sequence[str], None] = '23332a6bd36d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None




# alembic/versions/xxx_add_default_admin_user_and_organization.py

def upgrade() -> None:
    # Create default organization and capture its id
    op.execute("""
        INSERT INTO organizations (name, description, created_at, updated_at) 
        VALUES ('Default Organization', 'Default organization for initial setup', NOW(), NOW());
    """)

    # Insert default admin user using organization_id
    op.execute("""
        INSERT INTO users (email, hash_password, full_name, gender, role, is_active, organization_id, created_at, updated_at)
        VALUES (
            'admin@taskapp.com', 
            '$2y$10$o6Eku87pwF73Gt1QG5C.huVcjIRoiWtlBPKno7Gmnsijw.IY5xpdq', 
            'System Administrator 1', 
            'male',
            'admin', 
            true, 
            (SELECT id FROM organizations WHERE name = 'Default Organization'),
            NOW(),
            NOW()
        );
    """)

def downgrade() -> None:
  op.execute("""
        DELETE FROM users 
        WHERE organization_id = (SELECT id FROM organizations WHERE name = 'Default Organization');
    """)
  op.execute("DELETE FROM organizations WHERE name = 'Default Organization';")
