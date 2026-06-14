"""Startup script for local development"""
import asyncio
import logging
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.core.database import init_db, engine
from app.core.logging_config import logger


async def setup_development():
    """Initialize development environment"""
    try:
        logger.info("Initializing development database...")
        await init_db()
        logger.info("✓ Database initialized successfully")

        logger.info("Creating sample data...")
        from app.core.database import AsyncSessionLocal
        from app.models.models import Article
        import uuid
        from datetime import datetime

        async with AsyncSessionLocal() as session:
            # Check if sample data exists
            article_count = await session.query(Article).count()
            if article_count == 0:
                logger.info("Adding sample articles...")

                sample_articles = [
                    Article(
                        id=str(uuid.uuid4()),
                        title="Getting Started with Our Platform",
                        description="Learn the basics of using our service",
                        file_path="articles/sample-1.md",
                        file_name="sample-1.md",
                        content="# Getting Started\n\nWelcome to our platform...",
                        tags="onboarding, basics, tutorial",
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    ),
                    Article(
                        id=str(uuid.uuid4()),
                        title="Troubleshooting Common Issues",
                        description="Solutions to frequently encountered problems",
                        file_path="articles/sample-2.md",
                        file_name="sample-2.md",
                        content="# Troubleshooting\n\nCommon problems and solutions...",
                        tags="troubleshooting, help, support",
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    ),
                ]

                for article in sample_articles:
                    session.add(article)

                await session.commit()
                logger.info(f"✓ Added {len(sample_articles)} sample articles")
            else:
                logger.info(f"Database already contains {article_count} articles")

        logger.info("\n" + "=" * 50)
        logger.info("Development environment ready!")
        logger.info("=" * 50)
        logger.info("Start server with:")
        logger.info("  cd backend && python -m uvicorn app.main:app --reload")
        logger.info("\nAccess:")
        logger.info("  Dashboard: http://localhost:8000")
        logger.info("  API Docs:  http://localhost:8000/docs")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"Setup failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(setup_development())
