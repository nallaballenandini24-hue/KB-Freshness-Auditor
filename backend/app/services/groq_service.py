"""Groq AI integration service"""
import logging
from typing import Optional, List
from groq import Groq

from app.core.config import settings

logger = logging.getLogger(__name__)


class GroqAIService:
    """Service for interacting with Groq AI API"""

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    async def generate_recommendations(
        self, article_content: str, article_title: str
    ) -> dict:
        """Generate AI recommendations for article"""
        try:
            prompt = f"""Analyze the following Knowledge Base article and provide recommendations:

Title: {article_title}

Content:
{article_content}

Please provide specific recommendations for:
1. Missing Information - What important details are missing?
2. Updated Steps - Are there outdated procedures that need updating?
3. Improvement Suggestions - How can this be written more clearly?
4. Draft Updated Article - Provide a revised version of the article

Format your response as JSON with these exact keys: missing_info, updated_steps, improvements, draft_article
"""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text

            # Parse response
            recommendations = {
                "missing_info": "",
                "updated_steps": "",
                "improvements": "",
                "draft_article": "",
            }

            # Extract recommendations from response
            lines = response_text.split("\n")
            current_section = None

            for line in lines:
                if "Missing Information" in line:
                    current_section = "missing_info"
                elif "Updated Steps" in line:
                    current_section = "updated_steps"
                elif "Improvement Suggestions" in line:
                    current_section = "improvements"
                elif "Draft Updated Article" in line:
                    current_section = "draft_article"
                elif current_section and line.strip():
                    recommendations[current_section] += line + "\n"

            logger.info(f"Generated recommendations for article: {article_title}")
            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            raise

    async def generate_summary(self, article_content: str) -> str:
        """Generate summary of article"""
        try:
            prompt = f"""Provide a brief 2-3 sentence summary of this KB article:

{article_content[:1000]}
"""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )

            return message.content[0].text

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise

    async def check_content_quality(self, article_content: str) -> dict:
        """Check content quality and provide feedback"""
        try:
            prompt = f"""Evaluate the quality of this KB article on these criteria:

{article_content[:1000]}

Provide scores (1-10) for:
- Clarity (how easy to understand)
- Completeness (covers all relevant topics)
- Accuracy (technically correct)
- Formatting (well-structured)

Also provide brief feedback on improvements needed.

Format as: clarity:X, completeness:X, accuracy:X, formatting:X, feedback:text
"""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text

            # Parse scores
            quality_metrics = {
                "clarity": 0,
                "completeness": 0,
                "accuracy": 0,
                "formatting": 0,
                "feedback": "",
            }

            parts = response_text.split(",")
            for part in parts:
                if ":" in part:
                    key, value = part.split(":")
                    key = key.strip().lower()
                    value = value.strip()
                    if key in quality_metrics:
                        try:
                            quality_metrics[key] = float(value)
                        except ValueError:
                            quality_metrics["feedback"] += f" {part}"

            return quality_metrics

        except Exception as e:
            logger.error(f"Error checking content quality: {e}")
            raise
