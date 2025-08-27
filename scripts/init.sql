-- Initialize database with basic setup
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes that will be needed
-- These will be created by Alembic migrations, but good to have as backup

-- Performance optimization
ALTER DATABASE taskdb SET timezone TO 'UTC';