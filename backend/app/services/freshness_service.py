"""Freshness scoring service"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class FreshnessScoreCalculator:
    """Calculate freshness score for articles"""

    ARTICLE_AGE_WEIGHT = settings.ARTICLE_AGE_WEIGHT
    TICKET_COUNT_WEIGHT = settings.TICKET_COUNT_WEIGHT
    DAYS_SINCE_UPDATE_WEIGHT = settings.DAYS_SINCE_UPDATE_WEIGHT

    FRESH_THRESHOLD = settings.FRESH_THRESHOLD
    WARNING_THRESHOLD = settings.WARNING_THRESHOLD
    STALE_THRESHOLD = settings.STALE_THRESHOLD

    @staticmethod
    def calculate_score(
        article_age_days: int,
        ticket_count: int,
        days_since_last_update: int,
    ) -> float:
        """
        Calculate freshness score

        Score = (article_age_days * 0.5) + (ticket_count * 0.3) + (days_since_last_update * 0.2)
        """
        score = (
            (article_age_days * FreshnessScoreCalculator.ARTICLE_AGE_WEIGHT)
            + (ticket_count * FreshnessScoreCalculator.TICKET_COUNT_WEIGHT)
            + (days_since_last_update * FreshnessScoreCalculator.DAYS_SINCE_UPDATE_WEIGHT)
        )
        return round(score, 2)

    @staticmethod
    def get_status(score: float) -> str:
        """Determine status based on score"""
        if score < FreshnessScoreCalculator.FRESH_THRESHOLD:
            return "fresh"
        elif score < FreshnessScoreCalculator.WARNING_THRESHOLD:
            return "warning"
        else:
            return "stale"

    @staticmethod
    def calculate_article_age_days(created_at: datetime) -> int:
        """Calculate days since article creation"""
        return (datetime.utcnow() - created_at).days

    @staticmethod
    def calculate_days_since_update(updated_at: datetime) -> int:
        """Calculate days since last update"""
        return (datetime.utcnow() - updated_at).days
