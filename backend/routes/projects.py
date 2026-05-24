"""API routes for project management."""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient

from config.settings import settings
from models.kickstarter import (
    KickstarterProject,
    ProjectCreate
)
from services.analytics import AnalyticsService
from services.ai_analysis import AIAnalysisService
from utils.datenormalizer import get_utc_now

router = APIRouter()

# Initialize services
analytics_service = AnalyticsService()
ai_analysis_service = AIAnalysisService()

# These would be injected in a real application
# For now, we'll access the database directly from the main app
def get_database():
    # This is a placeholder - in reality, we'd get this from the app state
    from backend.server import db
    return db

@router.post("/", response_model=KickstarterProject, status_code=status.HTTP_201_CREATED)
async def create_project(project_data: ProjectCreate):
    """Create a new Kickstarter project with AI analysis."""
    db = get_database()
    project = KickstarterProject(**project_data.dict())
    
    # Perform AI analysis
    ai_analysis = await ai_analysis_service.analyze_project_with_ai(project)
    project.ai_analysis = ai_analysis.dict()
    project.risk_level = ai_analysis.risk_level
    
    # Insert into database
    result = await db.projects.insert_one(project.dict())
    return project

@router.get("/", response_model=List[KickstarterProject])
async def get_projects(
    category: Optional[str] = None, 
    risk_level: Optional[str] = None,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page")
):
    """Get a list of projects with optional filtering and pagination."""
    db = get_database()
    query = {}
    if category:
        query['category'] = category
    if risk_level:
        query['risk_level'] = risk_level
    
    skip = (page - 1) * page_size
    projects = await db.projects.find(query).skip(skip).limit(page_size).to_list(page_size)
    return [KickstarterProject(**project) for project in projects]

@router.get("/{project_id}", response_model=KickstarterProject)
async def get_project(project_id: str):
    """Get a specific project by ID."""
    db = get_database()
    project = await db.projects.find_one({'id': project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return KickstarterProject(**project)

@router.put("/{project_id}", response_model=KickstarterProject)
async def update_project(project_id: str, project_data: ProjectCreate):
    """Update an existing project."""
    db = get_database()
    existing_project = await db.projects.find_one({'id': project_id})
    if not existing_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update project
    updated_project = KickstarterProject(**project_data.dict())
    updated_project.id = project_id
    updated_project.updated_at = get_utc_now()
    
    # Re-analyze with AI
    ai_analysis = await ai_analysis_service.analyze_project_with_ai(updated_project)
    updated_project.ai_analysis = ai_analysis.dict()
    updated_project.risk_level = ai_analysis.risk_level
    
    await db.projects.replace_one({'id': project_id}, updated_project.dict())
    return updated_project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str):
    """Delete a project and its associated investments."""
    db = get_database()
    result = await db.projects.delete_one({'id': project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Also delete related investments
    await db.investments.delete_many({'project_id': project_id})
    return None
