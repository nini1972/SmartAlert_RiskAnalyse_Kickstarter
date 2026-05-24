"""Service for generating project alerts."""

from typing import List
import logging

from config.settings import settings
from models.kickstarter import (
    KickstarterProject,
    AlertSettings,
    ProjectAlert
)
from utils.datenormalizer import (
    normalize_datetime,
    get_utc_now,
    calculate_days_difference
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
