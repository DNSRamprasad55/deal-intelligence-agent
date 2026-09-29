from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.api.router import api_router
from app.db.database import engine, Base
import app.models  # Ensure models are imported for metadata reflection


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.APP_ENV}]")
    
    # Auto-create tables if running in SQLite / dev mode without manual alembic execution
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.error(f"Error initializing database tables: {str(e)}")
        
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
