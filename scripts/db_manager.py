# scripts/db_manager.py
"""Database management utilities"""

import sys
sys.path.append('.')

from alembic.config import Config
from alembic import command
from database import engine, test_database_connection
from app.models import BaseModel

def create_migration(message: str):
    """Create new migration"""
    alembic_cfg = Config("alembic.ini")
    command.revision(alembic_cfg, autogenerate=True, message=message)
    print(f"Created migration: {message}")

def upgrade_database():
    """Upgrade database to latest migration"""
    if not test_database_connection():
        print("Database connection failed")
        return False
    
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("Database upgraded to latest version")
    return True

def downgrade_database(revision: str = "-1"):
    """Downgrade database to specific revision"""
    alembic_cfg = Config("alembic.ini")
    command.downgrade(alembic_cfg, revision)
    print(f"Database downgraded to: {revision}")

def show_history():
    """Show migration history"""
    alembic_cfg = Config("alembic.ini")
    command.history(alembic_cfg, verbose=True)

def current_version():
    """Show current database version"""
    alembic_cfg = Config("alembic.ini")
    command.current(alembic_cfg, verbose=True)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Management')
    parser.add_argument('action', choices=['upgrade', 'downgrade', 'history', 'current', 'create'])
    parser.add_argument('--message', '-m', help='Migration message for create action')
    parser.add_argument('--revision', '-r', help='Revision for downgrade', default='-1')
    
    args = parser.parse_args()
    
    if args.action == 'upgrade':
        upgrade_database()
    elif args.action == 'downgrade':
        downgrade_database(args.revision)
    elif args.action == 'history':
        show_history()
    elif args.action == 'current':
        current_version()
    elif args.action == 'create':
        if not args.message:
            print("Please provide migration message with --message")
            sys.exit(1)
        create_migration(args.message)