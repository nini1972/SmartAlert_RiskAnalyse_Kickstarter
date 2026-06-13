import asyncio
import hashlib
import json
import logging
import os
import re
import tempfile
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests
from pydantic import BaseModel, Field, ValidationError


DEFAULT_TIMEOUT_SECONDS = 15
DEFAULT_MAX_RETRIES = 3
DEFAULT_CACHE_TTL_SECONDS = 600
MAX_BACKOFF_SECONDS = 8
CACHE_DIR = os.path.join(tempfile.gettempdir(), "kickstarter_scrape_cache")
KICKSTARTER_URL_PATTERN = re.compile(r"^https?://(?:www\.)?kickstarter\.com/")
KICKSTARTER_GRAPHQL_URL = "https://www.kickstarter.com/graph"
KICKSTARTER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)
KICKSTARTER_PROJECT_QUERY = """
query KickstarterProject($slug: String!) {
  project(slug: $slug) {
    id
    slug
    name
    description
    goal { amount currency }
    pledged { amount currency }
    backersCount
    state
    currency
    launchedAt
    deadlineAt
    url
    category { name slug }
    creator { name slug }
  }
}
"""


class KickstarterScrapedProject(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    creator: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=10, max_length=2000)
    category: str = Field(min_length=1, max_length=50)
    url: str = Field(pattern=KICKSTARTER_URL_PATTERN.pattern)
    goal_amount: float = Field(gt=0)
    pledged_amount: float = Field(default=0, ge=0)
    backers_count: int = Field(default=0, ge=0)
    deadline: datetime
    launched_date: datetime
    status: str = Field(pattern=r"^(live|successful|failed|cancelled)$")
    scraped: bool = True


def _safe_text(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    cleaned = re.sub(r"\s+", " ", str(value)).strip()
    return cleaned if cleaned else fallback


def _truncate_text(value: str, max_length: int) -> str:
    return value[:max_length] if len(value) > max_length else value


def _is_valid_kickstarter_url(url: str) -> bool:
    return bool(KICKSTARTER_URL_PATTERN.match(url))


def is_valid_kickstarter_project_url(url: str) -> bool:
    return _is_valid_kickstarter_url(url) and _extract_slug(url) is not None


def _extract_slug(url: str) -> Optional[str]:
    parsed = urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) >= 3 and parts[0] == "projects":
        return "/".join(parts[1:3])
    return None


def _extract_creator(value: Any) -> Optional[str]:
    if isinstance(value, dict):
        return value.get("name") or value.get("creator_name")
    if isinstance(value, str):
        return value
    return None


def _extract_category(value: Any) -> str:
    if isinstance(value, dict):
        return _safe_text(value.get("name"), "General")
    return _safe_text(value, "General")


def _money_amount(value: Any) -> float:
    if isinstance(value, dict):
        value = value.get("amount")
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _datetime_from_timestamp(value: Any) -> datetime:
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc).replace(tzinfo=None)
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    return datetime.utcnow()


def _normalize_status(value: Any) -> str:
    status = _safe_text(value, "live").lower()
    if status == "canceled":
        return "cancelled"
    if status in {"live", "successful", "failed", "cancelled"}:
        return status
    return "live"


def _load_json_candidates(html: str) -> list:
    candidates = []

    for match in re.finditer(
        r"<script[^>]*type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        block = match.group(1).strip()
        if block:
            candidates.append(block)

    assignment_patterns = [
        r"window\.__APOLLO_STATE__\s*=\s*(\{.*?\})\s*;",
        r"window\.ksr_track_properties\s*=\s*(\{.*?\})\s*;",
        r"window\.__NEXT_DATA__\s*=\s*(\{.*?\})\s*;",
    ]
    for pattern in assignment_patterns:
        for match in re.finditer(pattern, html, flags=re.DOTALL):
            candidates.append(match.group(1))

    parsed = []
    for candidate in candidates:
        try:
            parsed.append(json.loads(candidate))
        except json.JSONDecodeError:
            continue
    return parsed


def _find_first_key(data: Any, key: str) -> Optional[Any]:
    if isinstance(data, dict):
        if key in data and data[key] is not None:
            return data[key]
        for value in data.values():
            found = _find_first_key(value, key)
            if found is not None:
                return found
    elif isinstance(data, list):
        for item in data:
            found = _find_first_key(item, key)
            if found is not None:
                return found
    return None


def extract_structured_data_from_html(html: str, url: str) -> Dict[str, Any]:
    for payload in _load_json_candidates(html):
        name = _find_first_key(payload, "name")
        creator = _extract_creator(_find_first_key(payload, "creator"))
        description = _find_first_key(payload, "description") or _find_first_key(payload, "blurb")
        category_data = _find_first_key(payload, "category")
        category = category_data.get("name") if isinstance(category_data, dict) else category_data

        candidate = {
            "name": _safe_text(name, "Unknown Project"),
            "creator": _safe_text(creator, "Unknown Creator"),
            "description": _safe_text(description, "Extracted from Kickstarter"),
            "category": _safe_text(category, "General"),
            "url": url,
            "scraped": True,
        }
        try:
            return KickstarterScrapedProject(**candidate).model_dump()
        except ValidationError:
            continue
    return {}


def extract_with_beautifulsoup_fallback(html: str, url: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")

    name = None
    if soup.title:
        name = soup.title.text
    h1 = soup.select_one("h1")
    if h1 and h1.text.strip():
        name = h1.text.strip()
    meta_title = soup.select_one("meta[property='og:title']")
    if meta_title and meta_title.get("content"):
        name = meta_title["content"]

    creator = None
    creator_node = (
        soup.select_one("[data-test-id='creator-name']")
        or soup.select_one("a[rel='creator']")
        or soup.select_one("a[href*='/profile/']")
    )
    if creator_node:
        creator = creator_node.get_text(strip=True)

    description = None
    description_node = soup.select_one("meta[name='description']") or soup.select_one(
        "meta[property='og:description']"
    )
    if description_node and description_node.get("content"):
        description = description_node["content"]
    blurb_node = soup.select_one("[data-test-id='blurb']")
    if blurb_node and blurb_node.text.strip():
        description = blurb_node.get_text(strip=True)

    category = None
    category_node = soup.select_one("[data-test-id='category-name']") or soup.select_one(
        "a[href*='/discover/categories/']"
    )
    if category_node:
        category = category_node.get_text(strip=True)

    candidate = {
        "name": _safe_text(name, "Unknown Project"),
        "creator": _safe_text(creator, "Unknown Creator"),
        "description": _safe_text(description, "Extracted from Kickstarter"),
        "category": _safe_text(category, "General"),
        "url": url,
        "scraped": True,
    }
    try:
        return KickstarterScrapedProject(**candidate).model_dump()
    except ValidationError:
        return {}


def _cache_path_for_url(url: str) -> str:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, f"{digest}.json")


def _read_cache(url: str, cache_ttl_seconds: int) -> Dict[str, Any]:
    cache_path = _cache_path_for_url(url)
    if not os.path.exists(cache_path):
        return {}
    modified_at = datetime.fromtimestamp(os.path.getmtime(cache_path), timezone.utc)
    if datetime.now(timezone.utc) - modified_at > timedelta(seconds=cache_ttl_seconds):
        return {}
    try:
        with open(cache_path, "r", encoding="utf-8") as cache_file:
            payload = json.load(cache_file)
        return KickstarterScrapedProject(**payload).model_dump()
    except (OSError, json.JSONDecodeError, ValidationError):
        return {}


def _write_cache(url: str, data: Dict[str, Any]) -> None:
    cache_path = _cache_path_for_url(url)
    cache_data = {
        key: value.isoformat() if isinstance(value, datetime) else value
        for key, value in data.items()
    }
    try:
        with open(cache_path, "w", encoding="utf-8") as cache_file:
            json.dump(cache_data, cache_file)
    except OSError as exc:
        logging.warning("Failed to write Kickstarter cache for %s: %s", url, exc)


def _fetch_html_sync(session: Any, url: str, timeout_seconds: int) -> str:
    response = session.get(
        url,
        headers={"User-Agent": KICKSTARTER_USER_AGENT},
        timeout=timeout_seconds,
        impersonate="chrome131",
    )
    response.raise_for_status()
    return response.text


async def _fetch_html(session: Any, url: str, timeout_seconds: int) -> str:
    return await asyncio.to_thread(_fetch_html_sync, session, url, timeout_seconds)


def _extract_csrf_token(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, "lxml")
    csrf_tag = soup.find("meta", attrs={"name": "csrf-token"})
    if not csrf_tag:
        return None
    return csrf_tag.get("content")


def _fetch_project_graphql_data_sync(
    session: Any,
    url: str,
    slug: str,
    csrf_token: str,
    timeout_seconds: int,
) -> Dict[str, Any]:
    headers = {
        "Content-Type": "application/json",
        "User-Agent": KICKSTARTER_USER_AGENT,
        "X-CSRF-Token": csrf_token,
    }
    payload = {
        "operationName": "KickstarterProject",
        "variables": {"slug": slug},
        "query": KICKSTARTER_PROJECT_QUERY,
    }
    response = session.post(
        KICKSTARTER_GRAPHQL_URL,
        json=payload,
        headers=headers,
        timeout=timeout_seconds,
        impersonate="chrome131",
    )
    response.raise_for_status()
    data = response.json()

    errors = data.get("errors")
    if errors:
        messages = [error.get("message", "Unknown GraphQL error") for error in errors]
        raise RuntimeError("; ".join(messages))

    project = data.get("data", {}).get("project")
    if not project:
        raise RuntimeError("Kickstarter GraphQL response did not include project data")
    return project


async def _fetch_project_graphql_data(
    session: Any,
    url: str,
    slug: str,
    csrf_token: str,
    timeout_seconds: int,
) -> Dict[str, Any]:
    return await asyncio.to_thread(
        _fetch_project_graphql_data_sync,
        session,
        url,
        slug,
        csrf_token,
        timeout_seconds,
    )


def _normalize_graphql_project(project: Dict[str, Any], fallback_url: str) -> Dict[str, Any]:
    description = _truncate_text(_safe_text(project.get("description"), "Extracted from Kickstarter"), 2000)

    category = _extract_category(project.get("category"))
    creator = _extract_creator(project.get("creator"))

    candidate = {
        "name": _truncate_text(_safe_text(project.get("name"), "Unknown Project"), 200),
        "creator": _truncate_text(_safe_text(creator, "Unknown Creator"), 100),
        "description": description,
        "category": _truncate_text(category, 50),
        "url": _safe_text(project.get("url"), fallback_url),
        "goal_amount": _money_amount(project.get("goal")),
        "pledged_amount": _money_amount(project.get("pledged")),
        "backers_count": int(project.get("backersCount") or 0),
        "deadline": _datetime_from_timestamp(project.get("deadlineAt") or project.get("deadline")),
        "launched_date": _datetime_from_timestamp(project.get("launchedAt") or project.get("launched_at")),
        "status": _normalize_status(project.get("state") or project.get("status")),
        "scraped": True,
    }
    return KickstarterScrapedProject(**candidate).model_dump()


async def scrape_kickstarter_project(
    url: str,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    max_retries: int = DEFAULT_MAX_RETRIES,
    cache_ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS,
) -> Dict[str, Any]:
    if not _is_valid_kickstarter_url(url):
        logging.warning("Rejected non-Kickstarter URL for scraping: %s", url)
        return {}

    cached_data = _read_cache(url, cache_ttl_seconds)
    if cached_data:
        return cached_data

    slug = _extract_slug(url)
    if not slug:
        logging.warning("Could not extract Kickstarter project slug from URL: %s", url)
        return {}

    session = curl_requests.Session()
    try:
        for attempt in range(max_retries):
            try:
                html = await _fetch_html(session, url, timeout_seconds)
                csrf_token = _extract_csrf_token(html)

                if csrf_token:
                    try:
                        graphql_project = await _fetch_project_graphql_data(
                            session,
                            url,
                            slug,
                            csrf_token,
                            timeout_seconds,
                        )
                    except Exception as exc:
                        logging.warning("Kickstarter HTTP GraphQL fetch failed for %s: %s", url, exc)
                        graphql_project = None

                    if graphql_project:
                        normalized = _normalize_graphql_project(graphql_project, url)
                        if normalized:
                            _write_cache(url, normalized)
                            return normalized

                structured = extract_structured_data_from_html(html, url)
                if structured:
                    _write_cache(url, structured)
                    return structured

                fallback = extract_with_beautifulsoup_fallback(html, url)
                if fallback:
                    _write_cache(url, fallback)
                    return fallback
            except Exception as exc:
                backoff = min(2**attempt, MAX_BACKOFF_SECONDS)
                logging.warning(
                    "Kickstarter scrape attempt %s/%s failed for %s: %s",
                    attempt + 1,
                    max_retries,
                    url,
                    exc,
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(backoff)
    finally:
        session.close()

    logging.error("Kickstarter scrape failed after %s attempts for %s", max_retries, url)
    return {}
