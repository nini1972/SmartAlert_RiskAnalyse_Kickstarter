"""Utility functions for the Kickstarter Investment Tracker."""

from datetime import datetime, timezone
from typing import Optional


def normalize_datetime(dt: datetime) -> datetime:
    """Normalize datetime to UTC, handling timezone-aware and naive datetimes"""
    if dt.tzinfo is None:
        return dt
    return dt.replace(tzinfo=None)


def get_utc_now() -> datetime:
    """Get current UTC datetime"""
    return datetime.utcnow()


def calculate_days_difference(end_date: datetime, start_date: Optional[datetime] = None) -> int:
    """Calculate days between two dates, handling timezones properly"""
    if start_date is None:
        start_date = get_utc_now()
    
    end_normalized = normalize_datetime(end_date)
    start_normalized = normalize_datetime(start_date)
    
    return (end_normalized - start_normalized).days