from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine
from app.models import Base
from app.routers import auth, users, records, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    


app = FastAPI(
    title="Finance Dashboard API",
    description="Role-based finance data management system",
    version="1.0.0",
    lifespan=lifespan
)

# routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(records.router)
app.include_router(dashboard.router)


@app.get("/", tags=["health"])
def root():
    return {"message": "Finance Dashboard API is running"}