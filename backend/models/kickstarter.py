"""Database models for the Kickstarter Investment Tracker."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4

from pydantic import BaseModel, Field, validator


class KickstarterProject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=1, max_length=200)
    creator: str = Field(..., min_length=1, max_length=100)
    url: str = Field(..., pattern=r'^https?://')
    description: str = Field(..., min_length=10, max_length=2000)
    category: str = Field(..., min_length=1, max_length=50)
    goal_amount: float = Field(..., gt=0)
    pledged_amount: float = Field(default=0, ge=0)
    backers_count: int = Field(default=0, ge=0)
    deadline: datetime
    launched_date: datetime
    status: str = Field(..., pattern=r'^(live|successful|failed|cancelled)$')
    risk_level: str = Field(default='medium', pattern=r'^(low|medium|high)$')
    ai_analysis: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('deadline', 'launched_date')
    def validate_dates(cls, v):
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00')).replace(tzinfo=None)
            except ValueError:
                raise ValueError('Invalid datetime format')
        return v  # Assume already normalized by utility functions


class Investment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
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


class AlertSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str = "default_user"  # For future multi-user support
    notification_frequency: str = "instant"  # 'instant', 'daily', 'weekly'
    min_funding_velocity: float = 0.1  # Minimum funding speed threshold
    preferred_categories: List[str] = ["Technology"]
    max_risk_level: str = "medium"  # 'low', 'medium', 'high'
    min_success_probability: float = 0.6
    browser_notifications: bool = True
    email_notifications: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProjectAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    alert_type: str  # 'high_potential', 'funding_surge', 'deadline_approaching'
    message: str
    priority: str = "medium"  # 'low', 'medium', 'high'
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AnalyticsData(BaseModel):
    roi_prediction: float
    funding_velocity: float
    market_sentiment: float
    diversification_score: float
    risk_adjusted_return: float
    recommended_actions: List[str]