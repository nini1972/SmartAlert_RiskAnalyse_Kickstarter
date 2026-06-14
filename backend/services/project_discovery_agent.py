"""CrewAI-based agentic system for discovering and evaluating Kickstarter projects."""

from typing import List, Dict, Any, Optional
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from external_integrations.kickstarter import (
    scrape_kickstarter_project,
    is_valid_kickstarter_project_url,
    extract_structured_data_from_html
)
from services.ai_analysis import AIAnalysisService
from models.kickstarter import KickstarterProject, AIAnalysisResult
from config.settings import settings
import asyncio
import logging
import json
import re
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Initialize services
ai_analysis_service = AIAnalysisService()

# Custom Tools for CrewAI
class KickstarterProjectScrapeTool(BaseTool):
    name: str = "Scrape Kickstarter Project"
    description: str = "Scrape a Kickstarter project URL to extract project data"
    
    def _run(self, url: str) -> str:
        """Scrape a Kickstarter project and return JSON string of the data."""
        try:
            # Run the async function in a synchronous context for CrewAI tool
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(scrape_kickstarter_project(url))
            loop.close()
            
            if not result:
                return json.dumps({"error": "Failed to scrape project"})
            
            return json.dumps(result)
        except Exception as e:
            logger.error(f"Error scraping Kickstarter project {url}: {e}")
            return json.dumps({"error": str(e)})

class KickstarterProjectAnalysisTool(BaseTool):
    name: str = "Analyze Project with AI"
    description: str = "Perform AI analysis on a Kickstarter project to get investment insights"
    
    def _run(self, project_json: str) -> str:
        """Analyze a project using AI and return JSON string of the analysis."""
        try:
            project_data = json.loads(project_json)
            if "error" in project_data:
                return project_json  # Pass through error
            
            # Create KickstarterProject object from scraped data
            project = KickstarterProject(**project_data)
            
            # Run AI analysis (this is async, so we need to handle it)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            analysis = loop.run_until_complete(ai_analysis_service.analyze_project_with_ai(project))
            loop.close()
            
            return json.dumps(analysis.dict())
        except Exception as e:
            logger.error(f"Error analyzing project: {e}")
            return json.dumps({"error": str(e)})

class KickstarterProjectDiscoveryTool(BaseTool):
    name: str = "Discover New Kickstarter Projects"
    description: str = "Discover new Kickstarter projects by browsing categories or recent launches"
    
    def _run(self, category: str = "", limit: int = 10) -> str:
        """Discover new Kickstarter projects and return JSON array of project data."""
        try:
            # This is a simplified discovery mechanism
            # In a real implementation, you might want to:
            # 1. Browse Kickstarter category pages
            # 2. Use Kickstarter's explore/discover endpoints
            # 3. Check recently launched projects
            # 4. Look at trending/popular projects
            
            # For now, we'll return a placeholder that demonstrates the concept
            # In practice, you would implement actual web scraping of Kickstarter browse pages
            
            # Example implementation placeholder:
            discovered_urls = self._discover_project_urls(category, limit)
            projects = []
            
            for url in discovered_urls:
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    scraped_data = loop.run_until_complete(scrape_kickstarter_project(url))
                    loop.close()
                    
                    if scraped_data and "error" not in scraped_data:
                        projects.append(scraped_data)
                except Exception as e:
                    logger.warning(f"Failed to scrape discovered URL {url}: {e}")
                    continue
            
            return json.dumps(projects)
        except Exception as e:
                logger.error(f"Error discovering projects: {e}")
                return json.dumps({"error": str(e)})
    
    def _discover_project_urls(self, category: str, limit: int) -> List[str]:
        """Discover project URLs from Kickstarter browse pages.
        This is a simplified implementation - in practice you'd want to:
        1. Scrape Kickstarter category pages (e.g., https://www.kickstarter.com/discover/technology)
        2. Extract project URLs from the page
        3. Filter for recently launched projects
        """
        # Placeholder implementation - returns some known good URLs for testing
        # In a real implementation, you would scrape actual Kickstarter browse pages
        test_urls = [
            "https://www.kickstarter.com/projects/esa/helvetiq-a-smart-way-to-protect-your-data",
            "https://www.kickstarter.com/projects/1591887223/penna-a-sustainable-inkless-metal-pen",
            "https://www.kickstarter.com/projects/raspberrypi/raspberry-pi-pico-w",
            "https://www.kickstarter.com/projects/stacksocial/the-ultimate-2024-web-developer-bundle",
            "https://www.kickstarter.com/projects/alamode/alamode-an-arduino-compatible-raspberry-pi"
        ]
        
        # Filter by category if specified (simplified)
        if category:
            # In a real implementation, you would filter by actual category data
            pass
            
        return test_urls[:limit]

class ProjectEvaluationTool(BaseTool):
    name: str = "Evaluate Project for Investment"
    description: str = "Evaluate a Kickstarter project based on investment criteria (funding velocity, success probability, risk level, etc.)"
    
    def _run(self, project_json: str) -> str:
        """Evaluate a project and return JSON with score and recommendation."""
        try:
            data = json.loads(project_json)
            if "error" in data:
                return project_json  # Pass through error
            
            # Calculate investment score based on multiple factors
            score = self._calculate_investment_score(data)
            
            # Determine recommendation based on score
            if score >= 80:
                recommendation = "STRONG BUY"
            elif score >= 60:
                recommendation = "BUY"
            elif score >= 40:
                recommendation = "HOLD"
            elif score >= 20:
                recommendation = "WEAK HOLD"
            else:
                recommendation = "AVOID"
            
            result = {
                **data,
                "investment_score": score,
                "investment_recommendation": recommendation,
                "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return json.dumps(result)
        except Exception as e:
            logger.error(f"Error evaluating project: {e}")
            return json.dumps({"error": str(e)})
    
    def _calculate_investment_score(self, project_data: Dict[str, Any]) -> float:
        """Calculate investment score (0-100) based on various factors."""
        score = 0.0
        max_score = 100.0
        
        # Funding velocity (0-25 points)
        try:
            goal_amount = float(project_data.get("goal_amount", 0))
            pledged_amount = float(project_data.get("pledged_amount", 0))
            launched_date_str = project_data.get("launched_date")
            deadline_date_str = project_data.get("deadline")
            
            if goal_amount > 0 and launched_date_str and deadline_date_str:
                launched_date = datetime.fromisoformat(launched_date_str.replace('Z', '+00:00'))
                deadline_date = datetime.fromisoformat(deadline_date_str.replace('Z', '+00:00'))
                now = datetime.now(timezone.utc)
                
                days_elapsed = max((now - launched_date).total_seconds() / 86400, 1)  # at least 1 day
                days_total = max((deadline_date - launched_date).total_seconds() / 86400, 1)
                days_remaining = max((deadline_date - now).total_seconds() / 86400, 0)
                
                if days_elapsed > 0 and days_total > days_elapsed:
                    funding_ratio = pledged_amount / goal_amount
                    expected_final_ratio = funding_ratio * (days_total / days_elapsed)
                    # Score based on how much funding we expect vs goal (capped at 2.0x)
                    velocity_score = min(expected_final_ratio * 25, 25)  # 0-25 points
                    score += velocity_score
        except Exception as e:
            logger.debug(f"Could not calculate funding velocity: {e}")
        
        # AI success probability (0-25 points)
        try:
            # This would come from AI analysis, but for now we'll use a placeholder
            # In a real implementation, you'd get this from the AI analysis results
            success_probability = project_data.get("ai_analysis", {}).get("success_probability", 0.5)
            if isinstance(success_probability, (int, float)):
                score += success_probability * 25  # 0-25 points
        except Exception as e:
            logger.debug(f"Could not use success probability: {e}")
            # Default to middle score if no AI analysis
            score += 12.5
        
        # Risk level (0-20 points - lower risk is better)
        try:
            risk_level = project_data.get("risk_level", "medium").lower()
            risk_scores = {"low": 20, "medium": 10, "high": 0}
            score += risk_scores.get(risk_level, 10)
        except Exception as e:
            logger.debug(f"Could not process risk level: {e}")
            score += 10  # Default medium risk
        
        # Backer count momentum (0-15 points)
        try:
            backers_count = int(project_data.get("backers_count", 0))
            # Logarithmic scaling for backer count
            if backers_count > 0:
                backer_score = min(15 * (1 - (1 / (1 + backers_count / 100))), 15)
                score += backer_score
        except Exception as e:
            logger.debug(f"Could not calculate backer score: {e}")
        
        # Category popularity (0-10 points) - simplified
        try:
            # Some categories tend to perform better on Kickstarter
            preferred_categories = ["Technology", "Design", "Games"]
            category = project_data.get("category", "")
            if category in preferred_categories:
                score += 10
            else:
                score += 5  # Default for other categories
        except Exception as e:
            logger.debug(f"Could not calculate category score: {e}")
            score += 5
        
        # Progress so far (0-5 points)
        try:
            goal_amount = float(project_data.get("goal_amount", 0))
            pledged_amount = float(project_data.get("pledged_amount", 0))
            if goal_amount > 0:
                progress_ratio = min(pledged_amount / goal_amount, 1.0)
                score += progress_ratio * 5  # 0-5 points
        except Exception as e:
            logger.debug(f"Could not calculate progress score: {e}")
        
        return min(score, max_score)

# Agent Definitions
def create_project_discovery_agents() -> Dict[str, Agent]:
    """Create and return the agents for the project discovery workflow."""
    
    # Initialize tools
    scrape_tool = KickstarterProjectScrapeTool()
    analysis_tool = KickstarterProjectAnalysisTool()
    discovery_tool = KickstarterProjectDiscoveryTool()
    evaluation_tool = ProjectEvaluationTool()
    
    # Agent 1: Project Discovery Specialist
    discovery_agent = Agent(
        role="Kickstarter Project Discovery Specialist",
        goal="Find promising new Kickstarter projects in target categories",
        backstory="""You are an expert at finding emerging Kickstarter projects before they go viral.
        You know how to navigate Kickstarter's discovery systems, identify trending categories,
        and spot projects with early momentum that others might miss.""",
        tools=[discovery_tool, scrape_tool],
        verbose=True,
        allow_delegation=False
    )
    
    # Agent 2: Project Analysis Specialist
    analysis_agent = Agent(
        role="Project Analysis Specialist",
        goal="Perform deep analysis on Kickstarter projects to uncover investment insights",
        backstory="""You are a senior analyst with expertise in evaluating early-stage projects.
        You combine quantitative metrics with qualitative insights to assess a project's 
        true potential, looking beyond surface-level metrics to understand the team, 
        technology, and market opportunity.""",
        tools=[scrape_tool, analysis_tool],
        verbose=True,
        allow_delegation=False
    )
    
    # Agent 3: Investment Evaluation Specialist
    evaluation_agent = Agent(
        role="Investment Evaluation Specialist",
        goal="Evaluate Kickstarter projects against investment criteria to make recommendations",
        backstory="""You are a venture capital specialist who focuses on early-stage 
        Kickstarter projects. You understand what makes a project successful and can 
        quickly assess whether a project meets investment criteria based on funding 
        velocity, team strength, market potential, and risk factors.""",
        tools=[scrape_tool, analysis_tool, evaluation_tool],
        verbose=True,
        allow_delegation=False
    )
    
    # Agent 4: Project Curation Specialist (optional, for final decisions)
    curation_agent = Agent(
        role="Project Curation Specialist",
        goal="Make final decisions on which projects to add to the tracking system",
        backstory="""You are the final decision-maker for which Kickstarter projects 
        get added to our investment tracking system. You balance analytical rigor 
        with investment thesis, ensuring we only track projects that truly align 
        with our investment strategy and have genuine potential for success.""",
        tools=[evaluation_tool],
        verbose=True,
        allow_delegation=False
    )
    
    return {
        "discovery": discovery_agent,
        "analysis": analysis_agent,
        "evaluation": evaluation_agent,
        "curation": curation_agent
    }

# Task Definitions
def create_project_discovery_tasks(agents: Dict[str, Agent], category: str = "", limit: int = 10) -> List[Task]:
    """Create and return the tasks for the project discovery workflow."""
    
    # Task 1: Discover new projects
    discover_task = Task(
        description=f"""Discover {limit} new Kickstarter projects{f' in the {category} category' if category else ''}.
        Use the discovery tool to find project URLs, then scrape each project to get detailed information.
        Focus on recently launched projects that show early promise.""",
        agent=agents["discovery"],
        expected_output="JSON array containing scraped project data for {limit} Kickstarter projects"
    )
    
    # Task 2: Analyze discovered projects
    analyze_task = Task(
        description="""Perform AI analysis on each discovered project to get deeper insights.
        For each project, use the analysis tool to understand the team, technology, market potential,
        and risk factors that aren't apparent from surface-level metrics.""",
        agent=agents["analysis"],
        expected_output="JSON array containing project data with AI analysis results for each project",
        context=[discover_task]
    )
    
    # Task 3: Evaluate projects for investment
    evaluate_task = Task(
        description="""Evaluate each analyzed project against investment criteria including:
        - Funding velocity and momentum
        - AI-predicted success probability
        - Risk level assessment
        - Team credibility and execution capability
        - Market opportunity and timing
        Provide a score (0-100) and clear recommendation (STRONG BUY, BUY, HOLD, AVOID) for each project.""",
        agent=agents["evaluation"],
        expected_output="JSON array containing project data with investment scores and recommendations",
        context=[analyze_task]
    )
    
    # Task 4: Curate final selection (optional)
    curate_task = Task(
        description="""Review the evaluated projects and make final selections for our tracking system.
        Consider the investment scores, recommendations, and overall portfolio balance.
        Select only the most promising projects that align with our investment thesis and risk tolerance.
        Provide a curated list with justification for each selection.""",
        agent=agents["curation"],
        expected_output="JSON array containing the final selected projects with detailed justification",
        context=[evaluate_task]
    )
    
    # Return tasks - we can choose to run with or without the curation step
    return [discover_task, analyze_task, evaluate_task, curate_task]

# Crew Setup Function
def create_project_discovery_crew(category: str = "", limit: int = 10) -> Crew:
    """Create and return a CrewAI crew for project discovery and evaluation."""
    
    # Create agents
    agents = create_project_discovery_agents()
    
    # Create tasks
    tasks = create_project_discovery_tasks(agents, category, limit)
    
    # Create and return the crew
    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,  # Tasks run in order
        verbose=True,
        memory=True  # Enable memory for better context between tasks
    )
    
    return crew

# Main execution function
def run_project_discovery(category: str = "", limit: int = 10) -> Dict[str, Any]:
    """Run the project discovery workflow and return results."""
    try:
        logger.info(f"Starting project discovery for category '{category}' with limit {limit}")
        
        # Create and run the crew
        crew = create_project_discovery_crew(category, limit)
        result = crew.kickoff()
        
        logger.info("Project discovery workflow completed successfully")
        
        # Try to parse the result as JSON if possible
        try:
            # The result might be a string or already parsed object
            if isinstance(result, str):
                # Try to parse as JSON
                parsed_result = json.loads(result)
                return {
                    "success": True,
                    "data": parsed_result,
                    "raw_result": result
                }
            else:
                return {
                    "success": True,
                    "data": result,
                    "raw_result": str(result)
                }
        except json.JSONDecodeError:
            # If not JSON, return as text
            return {
                "success": True,
                "data": result,
                "raw_result": str(result)
            }
            
    except Exception as e:
        logger.error(f"Error in project discovery workflow: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": None
        }

# Example usage function for testing
def example_usage():
    """Example of how to use the project discovery system."""
    print("Running Kickstarter project discovery and evaluation...")
    
    # Discover and evaluate technology projects
    result = run_project_discovery(category="Technology", limit=5)
    
    if result["success"]:
        print("Discovery completed successfully!")
        print(f"Results: {json.dumps(result['data'], indent=2)}")
    else:
        print(f"Discovery failed: {result['error']}")

if __name__ == "__main__":
    # Run example when script is executed directly
    example_usage()