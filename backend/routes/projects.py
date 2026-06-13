"""API routes for project management."""

from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from typing import DefaultDict, Deque, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request, status

from config.settings import settings
from models.kickstarter import (
    KickstarterProject,
    ProjectCreate,
    ProjectScrapeRequest
)
from services.analytics import AnalyticsService
from services.ai_analysis import AIAnalysisService
from external_integrations.kickstarter import (
    is_valid_kickstarter_project_url,
    scrape_kickstarter_project
)
from utils.datenormalizer import get_utc_now

router = APIRouter()

SCRAPE_RATE_LIMIT_REQUESTS = 10
SCRAPE_RATE_LIMIT_WINDOW_SECONDS = 60
_scrape_request_times: DefaultDict[str, Deque[datetime]] = defaultdict(deque)

# Initialize services
analytics_service = AnalyticsService()
ai_analysis_service = AIAnalysisService()

# These would be injected in a real application
# For now, we'll access the database directly from the main app
def get_database():
    try:
        from backend.server import db
    except ModuleNotFoundError:
        from server import db
    return db


def _get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _check_scrape_rate_limit(client_ip: str) -> None:
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(seconds=SCRAPE_RATE_LIMIT_WINDOW_SECONDS)
    request_times = _scrape_request_times[client_ip]

    while request_times and request_times[0] < window_start:
        request_times.popleft()

    if len(request_times) >= SCRAPE_RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Kickstarter scrape rate limit exceeded"
        )

    request_times.append(now)


def _serialize_scraped_project(scraped_project: dict) -> dict:
    serialized = dict(scraped_project)
    for field in ("deadline", "launched_date"):
        value = serialized.get(field)
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            serialized[field] = value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return serialized


@router.post("", response_model=KickstarterProject, status_code=status.HTTP_201_CREATED)
async def create_project_no_slash(project_data: ProjectCreate):
    return await create_project(project_data)

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

@router.get("", response_model=List[KickstarterProject])
async def get_projects_no_slash(
    category: Optional[str] = None, 
    risk_level: Optional[str] = None,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page")
):
    return await get_projects(category, risk_level, page, page_size)

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

@router.post("/scrape")
async def scrape_project(project_scrape_request: ProjectScrapeRequest, request: Request):
    """Fetch project data from Kickstarter for the add-project form."""
    if not is_valid_kickstarter_project_url(project_scrape_request.url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL must be a Kickstarter project URL"
        )

    _check_scrape_rate_limit(_get_client_ip(request))
    scraped_project = await scrape_kickstarter_project(
        project_scrape_request.url,
        timeout_seconds=settings.SCRAPE_TIMEOUT_SECONDS
    )
    if not scraped_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not scrape Kickstarter project data"
        )
    KickstarterProject(**scraped_project)
    return _serialize_scraped_project(scraped_project)

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
