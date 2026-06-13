"""API routes for investment management."""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient

from config.settings import settings
from models.kickstarter import (
    Investment,
    InvestmentCreate
)

router = APIRouter()

def get_database():
    try:
        from backend.server import db
    except ModuleNotFoundError:
        from server import db
    return db

@router.post("", response_model=Investment, status_code=status.HTTP_201_CREATED)
async def create_investment_no_slash(investment_data: InvestmentCreate):
    return await create_investment(investment_data)

@router.post("/", response_model=Investment, status_code=status.HTTP_201_CREATED)
async def create_investment(investment_data: InvestmentCreate):
    """Create a new investment."""
    db = get_database()
    # Verify project exists
    project = await db.projects.find_one({'id': investment_data.project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    investment = Investment(**investment_data.dict())
    await db.investments.insert_one(investment.dict())
    return investment

@router.get("", response_model=List[Investment])
async def get_investments_no_slash(project_id: Optional[str] = None):
    return await get_investments(project_id)

@router.get("/", response_model=List[Investment])
async def get_investments(project_id: Optional[str] = None):
    """Get investments, optionally filtered by project ID."""
    db = get_database()
    query = {}
    if project_id:
        query['project_id'] = project_id
    
    investments = await db.investments.find(query).to_list(100)
    return [Investment(**investment) for investment in investments]
