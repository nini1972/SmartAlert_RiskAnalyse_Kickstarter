"""API routes for analytics and dashboard data."""

from fastapi import APIRouter
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient

from config.settings import settings
from models.kickstarter import AnalyticsData
from services.analytics import AnalyticsService

router = APIRouter()

# Initialize services
analytics_service = AnalyticsService()

def get_database():
    try:
        from backend.server import db
    except ModuleNotFoundError:
        from server import db
    return db

@router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics."""
    db = get_database()
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

@router.get("/recommendations")
async def get_ai_recommendations():
    """Get AI-powered investment recommendations."""
    try:
        # Get recent projects for analysis
        db = get_database()
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
        
        # This would call the AI analysis service in a real implementation
        # For now, return placeholder recommendations
        return {
            "recommendations": [
                "Consider diversifying into underrepresented categories",
                "Review high-risk investments for potential rebalancing",
                "Look for projects with strong funding velocity",
                "Monitor projects approaching deadlines",
                "Evaluate creator track records for future investments"
            ],
            "generated_at": "2026-05-23T15:21:06Z"  # This would be dynamic
        }
    except Exception as e:
        return {"recommendations": ["Unable to generate recommendations at this time"], "error": str(e)}

@router.get("/analytics/advanced")
async def get_advanced_analytics():
    """Get advanced portfolio analytics with ROI predictions."""
    try:
        db = get_database()
        # Get all projects and investments
        projects = await db.projects.find({}).to_list(100)
        investments = await db.investments.find({}).to_list(100)
        
        # Convert to Pydantic models
        from models.kickstarter import KickstarterProject, Investment
        project_objects = [KickstarterProject(**p) for p in projects]
        investment_objects = [Investment(**i) for i in investments]
        
        # Calculate analytics
        analytics = await analytics_service.calculate_portfolio_analytics(project_objects, investment_objects)
        return analytics
    except Exception as e:
        # Return default analytics on error
        return AnalyticsData(
            roi_prediction=0.0,
            funding_velocity=0.0,
            market_sentiment=0.5,
            diversification_score=0.0,
            risk_adjusted_return=0.0,
            recommended_actions=["Analytics calculation failed"]
        )

@router.get("/analytics/funding-trends")
async def get_funding_trends():
    """Get funding trend data for charts."""
    try:
        db = get_database()
        projects = await db.projects.find({}).to_list(100)
        
        # Calculate funding velocities for trend analysis
        trend_data = []
        for project in projects:
            project_obj = KickstarterProject(**project)
            velocity = await analytics_service.calculate_funding_velocity(project_obj)
            
            trend_data.append({
                "name": project["name"][:20] + "..." if len(project["name"]) > 20 else project["name"],
                "velocity": velocity,
                "success_probability": project.get("ai_analysis", {}).get("success_probability", 0.5) * 100,
                "pledged_percentage": (project["pledged_amount"] / project["goal_amount"]) * 100,
                "risk_level": project["risk_level"],
                "category": project["category"]
            })
        
        return {"trends": trend_data}
    except Exception as e:
        return {"trends": [], "error": str(e)}
