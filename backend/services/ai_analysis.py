"""Service for AI-powered project analysis."""

from typing import List, Optional, Dict, Any
import logging
import json
import re

from openai import OpenAI

from config.settings import settings
from models.kickstarter import AIAnalysisResult
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
    
    async def analyze_project_with_ai(self, project) -> AIAnalysisResult:
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
