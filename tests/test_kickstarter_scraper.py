from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.external_integrations.kickstarter import (
    KickstarterScrapedProject,
    extract_structured_data_from_html,
    extract_with_beautifulsoup_fallback,
)


FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_URL = "https://www.kickstarter.com/projects/demo/solar-backpack"


def test_extract_structured_data_from_html_uses_embedded_json():
    html = (FIXTURES_DIR / "kickstarter_structured_sample.html").read_text(encoding="utf-8")

    data = extract_structured_data_from_html(html, SAMPLE_URL)

    assert data["name"] == "Solar Backpack Charger"
    assert data["creator"] == "Jane Inventor"
    assert data["category"] == "Technology"
    assert data["url"] == SAMPLE_URL
    assert data["scraped"] is True


def test_extract_with_beautifulsoup_fallback_uses_html_selectors():
    html = (FIXTURES_DIR / "kickstarter_fallback_sample.html").read_text(encoding="utf-8")

    data = extract_with_beautifulsoup_fallback(html, SAMPLE_URL)

    assert data["name"] == "Fallback Project Heading"
    assert data["creator"] == "Fallback Creator"
    assert data["description"] == "Fallback extracted description from metadata."
    assert data["category"] == "Design"


def test_scraped_project_validation_rejects_non_kickstarter_urls():
    invalid_payload = {
        "name": "Project",
        "creator": "Creator",
        "description": "A valid enough description",
        "category": "Technology",
        "url": "https://example.com/project",
        "scraped": True,
    }

    with pytest.raises(ValidationError):
        KickstarterScrapedProject(**invalid_payload)
