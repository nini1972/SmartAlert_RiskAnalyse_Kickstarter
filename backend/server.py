from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta, timezone
import openai
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import requests
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# OpenAI client
openai.api_key = os.environ['OPENAI_API_KEY']
openai_client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class KickstarterProject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    creator: str
    url: str
    description: str
    category: str
    goal_amount: float
    pledged_amount: float
    backers_count: int
    deadline: datetime
    launched_date: datetime
    status: str  # 'live', 'successful', 'failed', 'cancelled'
    risk_level: str = 'medium'  # 'low', 'medium', 'high'
    ai_analysis: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Investment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    amount: float
    investment_date: datetime
    expected_return: Optional[float] = None
    notes: Optional[str] = None
    reward_tier: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectCreate(BaseModel):
    name: str
    creator: str
    url: str
    description: str
    category: str
    goal_amount: float
    pledged_amount: float = 0
    backers_count: int = 0
    deadline: datetime
    launched_date: datetime
    status: str = 'live'

class InvestmentCreate(BaseModel):
    project_id: str
    amount: float
    investment_date: datetime
    expected_return: Optional[float] = None
    notes: Optional[str] = None
    reward_tier: Optional[str] = None

class AIAnalysisResult(BaseModel):
    risk_level: str
    sentiment_score: float
    success_probability: float
    key_factors: List[str]
    recommendations: List[str]
    funding_velocity: float
    creator_credibility: float

# AI Analysis Functions
async def analyze_project_with_ai(project: KickstarterProject) -> AIAnalysisResult:
    """Analyze project using GPT-4 for qualitative insights"""
    try:
        prompt = f"""
        Analyze this Kickstarter project for investment risk:
        
        Project: {project.name}
        Creator: {project.creator}
        Description: {project.description}
        Category: {project.category}
        Goal: ${project.goal_amount:,.2f}
        Pledged: ${project.pledged_amount:,.2f}
        Backers: {project.backers_count}
        Status: {project.status}
        Days remaining: {(project.deadline.replace(tzinfo=None) - datetime.utcnow()).days if hasattr(project.deadline, 'replace') else 'N/A'}
        
        Provide analysis in this JSON format:
        {{
            "risk_level": "low|medium|high",
            "sentiment_score": 0.0-1.0,
            "success_probability": 0.0-1.0,
            "key_factors": ["factor1", "factor2", "factor3"],
            "recommendations": ["rec1", "rec2", "rec3"],
            "funding_velocity": 0.0-1.0,
            "creator_credibility": 0.0-1.0
        }}
        
        Consider: project description quality, creator experience, funding progress, time remaining, category trends.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800
        )
        
        import json
        analysis_text = response.choices[0].message.content
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
        if json_match:
            analysis_data = json.loads(json_match.group())
            return AIAnalysisResult(**analysis_data)
        else:
            # Fallback analysis
            return AIAnalysisResult(
                risk_level="medium",
                sentiment_score=0.5,
                success_probability=0.5,
                key_factors=["Analysis pending"],
                recommendations=["Manual review required"],
                funding_velocity=0.5,
                creator_credibility=0.5
            )
    except Exception as e:
        logging.error(f"AI analysis failed: {e}")
        return AIAnalysisResult(
            risk_level="medium",
            sentiment_score=0.5,
            success_probability=0.5,
            key_factors=["Analysis failed"],
            recommendations=["Manual review required"],
            funding_velocity=0.5,
            creator_credibility=0.5
        )

async def scrape_kickstarter_project(url: str) -> Dict[str, Any]:
    """Basic Kickstarter project data extraction"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract basic project data (simplified)
                    title = soup.find('h1', class_='type-28')
                    creator = soup.find('a', class_='grey-dark')
                    
                    return {
                        'name': title.text.strip() if title else 'Unknown Project',
                        'creator': creator.text.strip() if creator else 'Unknown Creator',
                        'description': 'Extracted from live project',
                        'category': 'Technology',
                        'scraped': True
                    }
    except Exception as e:
        logging.error(f"Scraping failed for {url}: {e}")
        return {}

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Kickstarter Investment Tracker API"}

@api_router.post("/projects", response_model=KickstarterProject)
async def create_project(project_data: ProjectCreate):
    project = KickstarterProject(**project_data.dict())
    
    # Perform AI analysis
    ai_analysis = await analyze_project_with_ai(project)
    project.ai_analysis = ai_analysis.dict()
    project.risk_level = ai_analysis.risk_level
    
    # Insert into database
    result = await db.projects.insert_one(project.dict())
    return project

@api_router.get("/projects", response_model=List[KickstarterProject])
async def get_projects(category: Optional[str] = None, risk_level: Optional[str] = None):
    query = {}
    if category:
        query['category'] = category
    if risk_level:
        query['risk_level'] = risk_level
    
    projects = await db.projects.find(query).to_list(100)
    return [KickstarterProject(**project) for project in projects]

@api_router.get("/projects/{project_id}", response_model=KickstarterProject)
async def get_project(project_id: str):
    project = await db.projects.find_one({'id': project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return KickstarterProject(**project)

@api_router.put("/projects/{project_id}", response_model=KickstarterProject)
async def update_project(project_id: str, project_data: ProjectCreate):
    existing_project = await db.projects.find_one({'id': project_id})
    if not existing_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update project
    updated_project = KickstarterProject(**project_data.dict())
    updated_project.id = project_id
    updated_project.updated_at = datetime.utcnow()
    
    # Re-analyze with AI
    ai_analysis = await analyze_project_with_ai(updated_project)
    updated_project.ai_analysis = ai_analysis.dict()
    updated_project.risk_level = ai_analysis.risk_level
    
    await db.projects.replace_one({'id': project_id}, updated_project.dict())
    return updated_project

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    result = await db.projects.delete_one({'id': project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Also delete related investments
    await db.investments.delete_many({'project_id': project_id})
    return {"message": "Project deleted successfully"}

@api_router.post("/investments", response_model=Investment)
async def create_investment(investment_data: InvestmentCreate):
    # Verify project exists
    project = await db.projects.find_one({'id': investment_data.project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    investment = Investment(**investment_data.dict())
    await db.investments.insert_one(investment.dict())
    return investment

@api_router.get("/investments", response_model=List[Investment])
async def get_investments(project_id: Optional[str] = None):
    query = {}
    if project_id:
        query['project_id'] = project_id
    
    investments = await db.investments.find(query).to_list(100)
    return [Investment(**investment) for investment in investments]

@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    # Calculate portfolio statistics
    total_projects = await db.projects.count_documents({})
    total_investments = await db.investments.count_documents({})
    
    # Investment amounts
    investments = await db.investments.find({}).to_list(1000)
    total_invested = sum(inv['amount'] for inv in investments)
    
    # Risk distribution
    risk_pipeline = [
        {"$group": {"_id": "$risk_level", "count": {"$sum": 1}}}
    ]
    risk_distribution = await db.projects.aggregate(risk_pipeline).to_list(10)
    
    # Category distribution
    category_pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}}
    ]
    category_distribution = await db.projects.aggregate(category_pipeline).to_list(10)
    
    # Success rate
    successful_projects = await db.projects.count_documents({'status': 'successful'})
    success_rate = (successful_projects / total_projects * 100) if total_projects > 0 else 0
    
    return {
        'total_projects': total_projects,
        'total_investments': total_investments,
        'total_invested': total_invested,
        'risk_distribution': risk_distribution,
        'category_distribution': category_distribution,
        'success_rate': success_rate,
        'avg_investment': total_invested / total_investments if total_investments > 0 else 0
    }

@api_router.post("/projects/scrape")
async def scrape_project_data(url: str):
    """Scrape basic project data from Kickstarter URL"""
    scraped_data = await scrape_kickstarter_project(url)
    if scraped_data:
        return {"message": "Project data scraped successfully", "data": scraped_data}
    else:
        raise HTTPException(status_code=400, detail="Failed to scrape project data")

@api_router.get("/recommendations")
async def get_ai_recommendations():
    """Get AI-powered investment recommendations"""
    try:
        # Get recent projects for analysis
        projects = await db.projects.find({}).limit(10).to_list(10)
        investments = await db.investments.find({}).to_list(100)
        
        # Create portfolio analysis prompt
        portfolio_summary = f"""
        Current Portfolio:
        - Total Projects: {len(projects)}
        - Total Investments: {len(investments)}
        - Total Invested: ${sum(inv['amount'] for inv in investments):,.2f}
        
        Recent Projects:
        {[f"- {p['name']} ({p['category']}, Risk: {p['risk_level']})" for p in projects[:5]]}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{
                "role": "user", 
                "content": f"""Based on this Kickstarter investment portfolio, provide 5 actionable recommendations for portfolio optimization and risk management:
                
                {portfolio_summary}
                
                Focus on: diversification, risk balance, emerging opportunities, and exit strategies.
                """
            }],
            temperature=0.7,
            max_tokens=600
        )
        
        recommendations = response.choices[0].message.content.split('\n')
        return {
            "recommendations": [rec.strip() for rec in recommendations if rec.strip()],
            "generated_at": datetime.utcnow()
        }
    except Exception as e:
        return {"recommendations": ["Unable to generate recommendations at this time"], "error": str(e)}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
