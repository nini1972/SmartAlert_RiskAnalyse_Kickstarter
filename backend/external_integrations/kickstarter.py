import asyncio
import hashlib
import json
import logging
import os
import re
import tempfile
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import aiohttp
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, ValidationError


DEFAULT_TIMEOUT_SECONDS = 15
DEFAULT_MAX_RETRIES = 3
DEFAULT_CACHE_TTL_SECONDS = 600
MAX_BACKOFF_SECONDS = 8
CACHE_DIR = os.path.join(tempfile.gettempdir(), "kickstarter_scrape_cache")


class KickstarterScrapedProject(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    creator: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=2000)
    category: str = Field(min_length=1, max_length=50)
    url: str = Field(pattern=r"^https?://(?:www\.)?kickstarter\.com/")
    scraped: bool = True


def _safe_text(value: Optional[str], fallback: str) -> str:
    if not value:
        return fallback
    cleaned = str(value).strip()
    return cleaned if cleaned else fallback


def _extract_creator(value: Any) -> Optional[str]:
    if isinstance(value, dict):
        return value.get("name") or value.get("creator_name")
    if isinstance(value, str):
        return value
    return None


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


async def _extract_with_playwright(url: str, timeout_seconds: int) -> Dict[str, Any]:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logging.info("Playwright not installed; skipping browser extraction")
        return {}

    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=timeout_seconds * 1000)
            html = await page.content()
            await browser.close()
            structured = extract_structured_data_from_html(html, url)
            if structured:
                return structured
            return extract_with_beautifulsoup_fallback(html, url)
    except Exception as exc:
        logging.warning("Playwright extraction failed for %s: %s", url, exc)
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
    try:
        with open(cache_path, "w", encoding="utf-8") as cache_file:
            json.dump(data, cache_file)
    except OSError as exc:
        logging.warning("Failed to write Kickstarter cache for %s: %s", url, exc)


async def _fetch_html(url: str, timeout_seconds: int) -> str:
    timeout = aiohttp.ClientTimeout(total=timeout_seconds)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        )
    }
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.text()


async def scrape_kickstarter_project(
    url: str,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    max_retries: int = DEFAULT_MAX_RETRIES,
    cache_ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS,
) -> Dict[str, Any]:
    cached_data = _read_cache(url, cache_ttl_seconds)
    if cached_data:
        return cached_data

    for attempt in range(max_retries):
        try:
            html = await _fetch_html(url, timeout_seconds)

            structured = extract_structured_data_from_html(html, url)
            if structured:
                _write_cache(url, structured)
                return structured

            browser_data = await _extract_with_playwright(url, timeout_seconds)
            if browser_data:
                _write_cache(url, browser_data)
                return browser_data

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

    logging.error("Kickstarter scrape failed after %s attempts for %s", max_retries, url)
    return {}
