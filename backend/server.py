"""Main application entry point for the Kickstarter Investment Tracker."""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import logging

from config.settings import settings
from routes import projects, investments, analytics, alerts

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the main app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="A Kickstarter investment and risk tracking application"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=settings.cors_origins_list,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(investments.router, prefix="/api/investments", tags=["investments"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "message": "Kickstarter Investment Tracker API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Starting Kickstarter Investment Tracker API")
    logger.info(f"Environment: {settings.PROJECT_NAME}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down Kickstarter Investment Tracker API")
    # Close database connection if needed
    # This would be handled by the database client in a real implementation
