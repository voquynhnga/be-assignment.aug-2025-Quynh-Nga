from fastapi import FastAPI
from app.routers import auth
from app.routers import org
from app.routers import prj
# from fastapi.security import OAuth2PasswordBearer, HTTPBearer



# bearer_scheme = HTTPBearer()

app = FastAPI(
    title="TaskApp",
    description="Multi-organization task management backend",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI    
    )



app.include_router(auth.router)
app.include_router(org.router)
app.include_router(prj.router)

