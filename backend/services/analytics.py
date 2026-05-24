"""Services for project analysis and alert generation."""

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import json
import re

from openai import OpenAI
from motor.motor_asyncio import AsyncIOMotorClient

from config.settings import settings
from models.kickstarter import (
    KickstarterProject,
    Investment,
    AIAnalysisResult,
    AlertSettings,
    ProjectAlert,
    AnalyticsData
)
from utils.datenormalizer import (
    normalize_datetime,
    get_utc_now,
    calculate_days_difference
)


class AIAnalysisService:
    """Service for AI-powered project analysis."""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.logger = logging.getLogger(__name__)
    
    async def analyze_project_with_ai(self, project: KickstarterProject) -> AIAnalysisResult:
        """Analyze project using GPT-4 for qualitative insights"""
        try:
            days_remaining = calculate_days_difference(project.deadline, get_utc_now())
            
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
            Days remaining: {max(0, days_remaining)}
            
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
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800
            )
            
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
            self.logger.error(f"AI analysis failed for project {project.id}: {e}")
            return AIAnalysisResult(
                risk_level="medium",
                sentiment_score=0.5,
                success_probability=0.5,
                key_factors=["Analysis failed"],
                recommendations=["Manual review required"],
                funding_velocity=0.5,
                creator_credibility=0.5
            )


class AlertService:
    """Service for generating project alerts."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def calculate_funding_velocity(self, project: KickstarterProject) -> float:
        """Calculate funding velocity as percentage of goal per day"""
        try:
            days_since_launch = calculate_days_difference(get_utc_now(), project.launched_date)
            
            if days_since_launch <= 0:
                return 0.0
            
            if project.goal_amount <= 0:
                return 0.0
                
            funding_percentage = (project.pledged_amount / project.goal_amount) * 100
            velocity = funding_percentage / days_since_launch
            return round(max(0.0, velocity), 2)
        except (AttributeError, TypeError, ZeroDivisionError) as e:
            self.logger.error(f"Error calculating funding velocity for project {project.id}: {e}")
            return 0.0
    
    async def generate_project_alerts(self, project: KickstarterProject, settings: AlertSettings) -> List[ProjectAlert]:
        """Generate alerts for promising projects based on user settings"""
        alerts = []
        
        try:
            # Check funding velocity
            velocity = await self.calculate_funding_velocity(project)
            if velocity >= settings.min_funding_velocity * 100:  # Convert to percentage
                alerts.append(ProjectAlert(
                    project_id=project.id,
                    alert_type="funding_surge",
                    message=f"🚀 {project.name} is funding at {velocity}% per day! This shows strong market interest.",
                    priority="high"
                ))
            
            # Check success probability
            if project.ai_analysis and project.ai_analysis.get('success_probability', 0) >= settings.min_success_probability:
                alerts.append(ProjectAlert(
                    project_id=project.id,
                    alert_type="high_potential",
                    message=f"⭐ {project.name} has {project.ai_analysis['success_probability']*100:.0f}% success probability - Consider investing!",
                    priority="medium"
                ))
            
            # Check deadline approaching
            days_remaining = calculate_days_difference(project.deadline, get_utc_now())
            
            if days_remaining <= 7 and days_remaining >= 0 and project.status == 'live':
                alerts.append(ProjectAlert(
                    project_id=project.id,
                    alert_type="deadline_approaching",
                    message=f"⏰ {project.name} ends in {days_remaining} days! Last chance to invest.",
                    priority="medium"
                ))
        except Exception as e:
            self.logger.error(f"Error generating alerts for project {project.id}: {e}")
        
        return alerts


class AnalyticsService:
    """Service for portfolio analytics calculations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def calculate_funding_velocity(self, project: KickstarterProject) -> float:
        """Calculate funding velocity as percentage of goal per day"""
        try:
            days_since_launch = calculate_days_difference(get_utc_now(), project.launched_date)
            
            if days_since_launch <= 0:
                return 0.0
            
            if project.goal_amount <= 0:
                return 0.0
                
            funding_percentage = (project.pledged_amount / project.goal_amount) * 100
            velocity = funding_percentage / days_since_launch
            return round(max(0.0, velocity), 2)
        except (AttributeError, TypeError, ZeroDivisionError) as e:
            self.logger.error(f"Error calculating funding velocity for project {project.id}: {e}")
            return 0.0
    
    async def calculate_portfolio_analytics(self, projects: List[KickstarterProject], investments: List[Investment]) -> AnalyticsData:
        """Generate advanced analytics for the investment portfolio"""
        if not projects or not investments:
            return AnalyticsData(
                roi_prediction=0.0,
                funding_velocity=0.0,
                market_sentiment=0.5,
                diversification_score=0.0,
                risk_adjusted_return=0.0,
                recommended_actions=["Add more projects to enable analytics"]
            )
        
        try:
            # Calculate average success probability
            success_probs = [p.ai_analysis.get('success_probability', 0.5) if p.ai_analysis else 0.5 for p in projects]
            avg_success_prob = sum(success_probs) / len(success_probs)
            
            # Calculate funding velocity average
            velocities = []
            for project in projects:
                velocity = await self.calculate_funding_velocity(project)
                velocities.append(velocity)
            avg_velocity = sum(velocities) / len(velocities) if velocities else 0.0
            
            # Calculate diversification score (based on categories)
            categories = [p.category for p in projects]
            unique_categories = len(set(categories))
            diversification_score = min(unique_categories / 5.0, 1.0)  # Max score for 5+ categories
            
            # Calculate risk distribution
            risk_levels = [p.risk_level for p in projects]
            high_risk_ratio = risk_levels.count('high') / len(risk_levels)
            medium_risk_ratio = risk_levels.count('medium') / len(risk_levels)
            low_risk_ratio = risk_levels.count('low') / len(risk_levels)
            
            # Risk-adjusted return prediction
            total_invested = sum(inv.amount for inv in investments)
            expected_returns = sum(inv.expected_return or inv.amount * 1.2 for inv in investments)
            roi_prediction = ((expected_returns - total_invested) / total_invested * 100) if total_invested > 0 else 0.0
            
            # Adjust for risk
            risk_adjustment = 1.0 - (high_risk_ratio * 0.3) + (low_risk_ratio * 0.1)
            risk_adjusted_return = roi_prediction * risk_adjustment
            
            # Generate recommendations
            recommendations = []
            if high_risk_ratio > 0.4:
                recommendations.append("Consider reducing high-risk investments to balance portfolio")
            if diversification_score < 0.6:
                recommendations.append("Diversify across more categories to reduce sector risk")
            if avg_velocity < 5.0:
                recommendations.append("Look for projects with faster funding momentum")
            if avg_success_prob < 0.6:
                recommendations.append("Focus on projects with higher AI-predicted success rates")
            
            return AnalyticsData(
                roi_prediction=round(roi_prediction, 2),
                funding_velocity=round(avg_velocity, 2),
                market_sentiment=round(avg_success_prob, 2),
                diversification_score=round(diversification_score, 2),
                risk_adjusted_return=round(risk_adjusted_return, 2),
                recommended_actions=recommendations or ["Portfolio looks well-balanced!"]
            )
        except Exception as e:
            self.logger.error(f"Failed to calculate analytics: {e}")
            return AnalyticsData(
                roi_prediction=0.0,
                funding_velocity=0.0,
                market_sentiment=0.5,
                diversification_score=0.0,
                risk_adjusted_return=0.0,
                recommended_actions=["Analytics calculation failed"]
            )
