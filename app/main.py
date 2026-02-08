from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
from app.config import settings
from app.infrastructure.database.db import db
from app.api.v1.routers import cases as cases_router

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema de tracker de casos de soporte y requerimientos",
    version="1.0.0",
    debug=settings.DEBUG,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cases_router.router, prefix="/api/v1")


@app.on_event("startup")
async def startup():
    """Initialize database connection on startup"""
    logger.info("Starting application...")
    try:
        await db.connect()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(
            f"Failed to connect to database: {e}\n"
            "Please ensure PostgreSQL is running.\n"
            "You can start it with: make db-up or docker-compose up -d db"
        )
        # No raise - allow app to start but health checks will fail
        logger.warning("Application started without database connection")


@app.on_event("shutdown")
async def shutdown():
    """Close database connection on shutdown"""
    logger.info("Shutting down application...")
    await db.disconnect()
    logger.info("Database disconnected")


@app.get("/")
async def root():
    """Root endpoint - Hello World"""
    return {
        "message": "Hello World from Tracker API!",
        "app": settings.APP_NAME,
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/health/ready")
async def readiness():
    """Readiness check - verifies database connection"""
    try:
        await db.execute("SELECT 1")
        return {"status": "ready", "checks": {"database": "healthy"}}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "not_ready", "checks": {"database": "unhealthy", "error": str(e)}}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
