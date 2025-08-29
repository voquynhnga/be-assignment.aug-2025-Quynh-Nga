from fastapi import FastAPI
from app.routers import auth
from app.routers import org

app = FastAPI(
    title="TaskApp",
    description="Multi-organization task management backend",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI    
    )

app.include_router(auth.router)
app.include_router(org.router)

