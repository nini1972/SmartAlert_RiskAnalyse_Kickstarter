"""API routes for alerts and notification settings."""

from fastapi import APIRouter, HTTPException, status
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient

from config.settings import settings
from models.kickstarter import (
    AlertSettings,
    ProjectAlert
)
from services.alerts import AlertService

router = APIRouter()

# Initialize services
alert_service = AlertService()

def get_database():
    # This is a placeholder - in reality, we'd get this from the app state
    from backend.server import db
    return db

@router.get("/", response_model=List[ProjectAlert])
async def get_smart_alerts():
    """Get smart alerts for promising projects."""
    try:
        db = get_database()
        # Get default alert settings (in a real app, this would be user-specific)
        default_settings = AlertSettings()
        
        # Get active projects
        projects = await db.projects.find({"status": "live"}).to_list(100)
        
        all_alerts = []
        for project in projects:
            from models.kickstarter import KickstarterProject
            project_obj = KickstarterProject(**project)
            alerts = await alert_service.generate_project_alerts(project_obj, default_settings)
            all_alerts.extend(alerts)
        
        # Sort by priority and creation time
        priority_order = {"high": 3, "medium": 2, "low": 1}
        all_alerts.sort(key=lambda x: (priority_order.get(x.priority, 0), x.created_at), reverse=True)
        
        return all_alerts[:10]  # Return top 10 alerts
    except Exception as e:
        # Log the error in a real implementation
        return []

@router.post("/settings", response_model=AlertSettings)
async def update_alert_settings(settings: AlertSettings):
    """Update user alert preferences."""
    try:
        db = get_database()
        # In a real app, this would be user-specific
        await db.alert_settings.replace_one(
            {"user_id": settings.user_id}, 
            settings.dict(), 
            upsert=True
        )
        return settings
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update settings: {e}")

@router.get("/settings", response_model=AlertSettings)
async def get_alert_settings():
    """Get current alert settings."""
    try:
        db = get_database()
        settings = await db.alert_settings.find_one({"user_id": "default_user"})
        if settings:
            return AlertSettings(**settings)
        else:
            # Return default settings
            return AlertSettings()
    except Exception as e:
        return AlertSettings()
