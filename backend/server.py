from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from .database import connect_to_mongo, close_mongo_connection
from .models import UserRole, Gender, FavorCategory, TaskStatus, IssueStatus, QuestionType

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import database functions
from .database import connect_to_mongo, close_mongo_connection

# Import routers
from .routers.auth_router import router as auth_router
from .routers.voter_router import router as voter_router
from .routers.survey_router import router as survey_router
from .routers.task_router import router as task_router
from .routers.dashboard_router import router as dashboard_router
from .routers.import_router import router as import_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Political Voter Management Platform API...")
    await connect_to_mongo()
    logger.info("Database connected and indexes created")
    yield
    # Shutdown
    logger.info("Shutting down...")
    await close_mongo_connection()
    logger.info("Database connection closed")

# Create the main app
app = FastAPI(
    title="Political Voter Management Platform",
    description="Complete political voter management system with mobile and web support",
    version="1.0.0",
    lifespan=lifespan
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Health check endpoint
@api_router.get("/")
async def root():
    return {
        "message": "Political Voter Management Platform API",
        "version": "1.0.0",
        "status": "operational"
    }

@api_router.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include routers
api_router.include_router(auth_router)
api_router.include_router(voter_router)
api_router.include_router(survey_router)
api_router.include_router(task_router)
api_router.include_router(dashboard_router)
api_router.include_router(import_router)

# Include the api_router in the main app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
