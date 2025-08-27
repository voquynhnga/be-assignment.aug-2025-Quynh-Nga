# alembic/env.py
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import your models and config
import sys
sys.path.append('.')

from config import get_settings
from app.models import BaseModel

# Alembic Config object
config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for auto-generation
target_metadata = BaseModel.metadata

def get_url():
    """Get database URL from environment"""
    settings = get_settings()
    return settings.database_url

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    
    # Override database URL
    config.set_main_option("sqlalchemy.url", get_url())
    
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            # Include object name in migration
            include_object=include_object,
            # Render item for better diffs
            render_item=render_item,
        )

        with context.begin_transaction():
            context.run_migrations()

def include_object(object, name, type_, reflected, compare_to):
    """Filter objects to include in migration"""
    # Skip temporary tables
    if type_ == "table" and name.startswith("temp_"):
        return False
    return True

def render_item(type_, obj, autogen_context):
    """Render custom types for better migration files"""
    if type_ == "type" and hasattr(obj, "name"):
        # Custom enum rendering
        return f"sa.Enum(name='{obj.name}')"
    return False

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()