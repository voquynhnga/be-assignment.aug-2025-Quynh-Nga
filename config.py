from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://taskapp:taskapp123@localhost:5432/taskdb"
        
    # Application
    debug: bool = True
    log_level: str = "INFO"
    
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


def get_settings():
    return Settings()

settings = Settings()
