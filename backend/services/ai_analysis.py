"""Service for AI-powered project analysis."""

from typing import Any, Dict, Optional
import json
import logging
import re

from openai import OpenAI

from config.settings import settings
from models.kickstarter import AIAnalysisResult
from utils.datenormalizer import calculate_days_difference, get_utc_now


class AIAnalysisService:
    """Service for AI-powered project analysis."""

    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.logger = logging.getLogger(__name__)

    async def analyze_project_with_ai(self, project) -> AIAnalysisResult:
        """Analyze project using GPT for qualitative insights."""
        try:
            prompt = self._build_prompt(project)
            response = self.openai_client.chat.completions.create(
                model=getattr(settings, "OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {
                        "role": "system",
                        "content": "Return only valid JSON matching the requested schema. Do not include markdown."
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=800,
            )

            analysis_text = response.choices[0].message.content
            analysis_data = self._parse_analysis_json(analysis_text)
            return AIAnalysisResult(**analysis_data)
        except Exception as exc:
            self.logger.error("AI analysis failed for project %s: %s", project.id, exc)
            return self._fallback_analysis(project, str(exc))

    def _build_prompt(self, project) -> str:
        days_remaining = calculate_days_difference(project.deadline, get_utc_now())
        funding_ratio = (project.pledged_amount / project.goal_amount) if project.goal_amount else 0

        return f"""
Analyze this Kickstarter project for investment risk.

Project: {project.name}
Creator: {project.creator}
Description: {project.description}
Category: {project.category}
URL: {project.url}
Goal: {project.goal_amount:,.2f}
Pledged: {project.pledged_amount:,.2f}
Funding ratio: {funding_ratio:.2%}
Backers: {project.backers_count}
Status: {project.status}
Days remaining: {max(0, days_remaining)}

Return JSON with this exact schema:
{{
  "risk_level": "low|medium|high",
  "sentiment_score": 0.0,
  "success_probability": 0.0,
  "key_factors": ["factor1", "factor2", "factor3"],
  "recommendations": ["rec1", "rec2", "rec3"],
  "funding_velocity": 0.0,
  "creator_credibility": 0.0
}}

Consider description quality, creator signals, funding progress, time remaining, backer count, and category context.
""".strip()

    def _parse_analysis_json(self, analysis_text: Optional[str]) -> Dict[str, Any]:
        if not analysis_text:
            raise ValueError("Empty AI analysis response")

        json_match = re.search(r"\{.*\}", analysis_text, re.DOTALL)
        if not json_match:
            raise ValueError("AI response did not contain JSON")

        analysis_data = json.loads(json_match.group())
        required_fields = {
            "risk_level",
            "sentiment_score",
            "success_probability",
            "key_factors",
            "recommendations",
            "funding_velocity",
            "creator_credibility",
        }
        missing_fields = required_fields - set(analysis_data)
        if missing_fields:
            raise ValueError(f"AI response missing fields: {', '.join(sorted(missing_fields))}")
        return analysis_data

    def _fallback_analysis(self, project, error: Optional[str] = None) -> AIAnalysisResult:
        if error:
            self.logger.info("Using deterministic fallback analysis for project %s: %s", project.id, error)

        days_remaining = calculate_days_difference(project.deadline, get_utc_now())
        funding_ratio = (project.pledged_amount / project.goal_amount) if project.goal_amount else 0
        days_since_launch = calculate_days_difference(get_utc_now(), project.launched_date)
        raw_funding_velocity = (funding_ratio * 100 / days_since_launch) if days_since_launch > 0 else 0
        funding_velocity = min(raw_funding_velocity / 20.0, 1.0)

        if project.status == "successful":
            risk_level = "low"
            success_probability = 0.95
        elif project.status in {"failed", "cancelled"}:
            risk_level = "high"
            success_probability = 0.05
        elif days_remaining <= 0:
            risk_level = "high"
            success_probability = 0.2
        elif funding_ratio >= 1.0:
            risk_level = "low"
            success_probability = 0.85
        elif funding_ratio >= 0.6:
            risk_level = "medium"
            success_probability = 0.65
        elif funding_ratio >= 0.3:
            risk_level = "medium"
            success_probability = 0.45
        else:
            risk_level = "high"
            success_probability = 0.25

        description_quality = min(len(project.description) / 700, 1.0)
        backer_signal = min(project.backers_count / 100, 1.0)
        funding_signal = min(funding_ratio, 1.0)
        creator_credibility = round((description_quality * 0.35) + (backer_signal * 0.35) + (funding_signal * 0.30), 2)

        if project.status == "successful":
            creator_credibility = max(creator_credibility, 0.85)
        elif project.status in {"failed", "cancelled"}:
            creator_credibility = min(creator_credibility, 0.35)

        return AIAnalysisResult(
            risk_level=risk_level,
            sentiment_score=round(max(0.1, min(funding_ratio, 1.0)), 2),
            success_probability=round(success_probability, 2),
            key_factors=[
                f"Funding ratio is {funding_ratio:.0%} of goal.",
                f"Project status is {project.status}.",
                f"Raw funding velocity is {raw_funding_velocity:.2f}% of goal per day." if raw_funding_velocity else "Project has not been live long enough to calculate funding velocity.",
            ],
            recommendations=[
                "Review the project description, reward structure, and creator update history before investing." if risk_level != "low" else "Project shows strong funding signals; continue monitoring updates and delivery risk.",
                "Compare this project against similar campaigns in the same category.",
                "Re-check the campaign shortly before the deadline if it is still live.",
            ],
            funding_velocity=round(funding_velocity, 2),
            creator_credibility=creator_credibility,
        )
