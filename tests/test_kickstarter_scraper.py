import asyncio
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.external_integrations import kickstarter
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


def test_scrape_kickstarter_project_rejects_invalid_urls_before_cache_or_network(monkeypatch):
    def unexpected_read_cache(*args, **kwargs):
        raise AssertionError("_read_cache should not be called for invalid URLs")

    async def unexpected_fetch_html(*args, **kwargs):
        raise AssertionError("_fetch_html should not be called for invalid URLs")

    monkeypatch.setattr(kickstarter, "_read_cache", unexpected_read_cache)
    monkeypatch.setattr(kickstarter, "_fetch_html", unexpected_fetch_html)

    result = asyncio.run(kickstarter.scrape_kickstarter_project("https://example.com/project"))

    assert result == {}
