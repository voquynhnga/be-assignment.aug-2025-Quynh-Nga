from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://taskapp:taskapp123@localhost:5432/taskdb"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # JWT
    secret_key: str = "changeme"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Application
    debug: bool = True
    log_level: str = "INFO"
    
    # File Upload
    max_file_size: int = 5242880  # 5MB in bytes
    max_files_per_task: int = 3
    upload_dir: str = "uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


def get_settings():
    return Settings()

settings = Settings()
