"""Temporal workflow for audit execution"""
import logging
from datetime import datetime
from typing import List

logger = logging.getLogger(__name__)


class AuditWorkflow:
    """
    Workflow for executing KB freshness audits

    Steps:
    1. Scan KB Articles
    2. Read Ticket Data
    3. Calculate Scores
    4. Generate Recommendations
    5. Save Results
    """

    @staticmethod
    async def execute_audit(job_id: str, session):
        """Execute audit workflow"""
        try:
            from app.repositories.article_repository import ArticleRepository
            from app.repositories.ticket_repository import TicketRepository
            from app.services.audit_service import AuditService
            from app.services.freshness_service import FreshnessScoreCalculator
            from app.services.groq_service import GroqAIService
            from app.services.recommendation_service import AIRecommendationService
            from app.schemas.schemas import AIRecommendationCreate

            # Step 1: Scan KB Articles
            logger.info(f"[{job_id}] Step 1: Scanning KB articles...")
            article_repo = ArticleRepository(session)
            articles = await article_repo.get_active_articles(limit=1000)
            logger.info(f"[{job_id}] Found {len(articles)} articles")

            # Step 2-3: Process each article
            audit_service = AuditService(session)
            recommendation_service = AIRecommendationService(session)
            ticket_repo = TicketRepository(session)
            groq_service = GroqAIService()

            logger.info(f"[{job_id}] Step 2-3: Calculating freshness scores...")
            processed_count = 0

            for article in articles:
                try:
                    # Get ticket count for article
                    ticket_count = await ticket_repo.count_by_article_id(article.id)

                    # Calculate age metrics
                    article_age_days = FreshnessScoreCalculator.calculate_article_age_days(
                        article.created_at
                    )
                    days_since_update = FreshnessScoreCalculator.calculate_days_since_update(
                        article.updated_at
                    )

                    # Calculate freshness score
                    score = FreshnessScoreCalculator.calculate_score(
                        article_age_days, ticket_count, days_since_update
                    )
                    status = FreshnessScoreCalculator.get_status(score)

                    # Create audit result
                    await audit_service.create_audit_result(
                        article_id=article.id,
                        freshness_score=score,
                        status=status,
                        article_age_days=article_age_days,
                        ticket_count=ticket_count,
                        days_since_last_update=days_since_update,
                    )

                    # Step 4: Generate AI recommendations for stale articles
                    if status == "stale":
                        logger.info(
                            f"[{job_id}] Generating recommendations for stale article: {article.id}"
                        )
                        try:
                            recommendations = await groq_service.generate_recommendations(
                                article.content, article.title
                            )

                            # Save recommendations
                            for rec_type, content in recommendations.items():
                                if content:
                                    rec_data = AIRecommendationCreate(
                                        recommendation_type=rec_type,
                                        original_content=article.content[:500],
                                        recommended_content=content,
                                        confidence_score=0.85,
                                    )
                                    await recommendation_service.create_recommendation(
                                        article.id, rec_data
                                    )

                        except Exception as e:
                            logger.warning(f"[{job_id}] Error generating recommendations: {e}")

                    processed_count += 1

                except Exception as e:
                    logger.error(f"[{job_id}] Error processing article {article.id}: {e}")

            # Step 5: Save results and update job
            logger.info(f"[{job_id}] Step 5: Completing audit job...")
            await audit_service.update_audit_job(
                job_id,
                status="completed",
                processed_articles=processed_count,
                completed_at=datetime.utcnow(),
            )

            logger.info(f"[{job_id}] Audit completed successfully")
            return {"status": "completed", "processed": processed_count}

        except Exception as e:
            logger.error(f"[{job_id}] Audit workflow failed: {e}")
            from app.services.audit_service import AuditService

            audit_service = AuditService(session)
            await audit_service.update_audit_job(
                job_id, status="failed", error_message=str(e)
            )
            raise
