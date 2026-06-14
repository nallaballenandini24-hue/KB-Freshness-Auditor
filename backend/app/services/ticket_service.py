"""Ticket service"""
import uuid
import logging
import csv
import io
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Ticket
from app.schemas.schemas import TicketCreate, TicketResponse
from app.repositories.ticket_repository import TicketRepository
from app.repositories.article_repository import ArticleRepository

logger = logging.getLogger(__name__)


class TicketService:
    """Service for managing tickets"""

    def __init__(self, session: AsyncSession):
        self.repository = TicketRepository(session)
        self.article_repo = ArticleRepository(session)
        self.session = session

    async def create_ticket(self, ticket_data: TicketCreate) -> TicketResponse:
        """Create new ticket"""
        ticket = Ticket(
            id=str(uuid.uuid4()),
            ticket_id=ticket_data.ticket_id,
            subject=ticket_data.subject,
            description=ticket_data.description,
            category=ticket_data.category,
            article_id=ticket_data.article_id,
            resolved=ticket_data.resolved,
            created_at=ticket_data.created_at,
            resolved_at=ticket_data.resolved_at,
        )

        try:
            created_ticket = await self.repository.create(ticket)
            await self.repository.commit()
            logger.info(f"Ticket created: {ticket.ticket_id}")
            return TicketResponse.model_validate(created_ticket)

        except Exception as e:
            await self.repository.rollback()
            logger.error(f"Error creating ticket: {e}")
            raise

    async def get_ticket(self, ticket_id: str) -> Optional[TicketResponse]:
        """Get ticket by ID"""
        ticket = await self.repository.get_by_id(ticket_id)
        return TicketResponse.model_validate(ticket) if ticket else None

    async def list_tickets(
        self, limit: int = 100, offset: int = 0
    ) -> List[TicketResponse]:
        """List tickets"""
        tickets = await self.repository.get_all(limit=limit, offset=offset)
        return [TicketResponse.model_validate(t) for t in tickets]

    async def get_tickets_by_article(self, article_id: str) -> List[TicketResponse]:
        """Get tickets by article"""
        tickets = await self.repository.get_by_article_id(article_id)
        return [TicketResponse.model_validate(t) for t in tickets]

    async def search_tickets(self, query: str, limit: int = 10) -> List[TicketResponse]:
        """Search tickets"""
        tickets = await self.repository.search_by_subject(query, limit=limit)
        return [TicketResponse.model_validate(t) for t in tickets]

    async def import_tickets_from_csv(self, file_content: bytes) -> Tuple[int, int]:
        """Import tickets from CSV file"""
        try:
            csv_str = file_content.decode("utf-8")
            reader = csv.DictReader(io.StringIO(csv_str))

            imported_count = 0
            skipped_count = 0

            for row in reader:
                try:
                    # Check if ticket already exists
                    existing = await self.repository.get_by_ticket_id(row["ticket_id"])
                    if existing:
                        skipped_count += 1
                        continue

                    ticket = Ticket(
                        id=str(uuid.uuid4()),
                        ticket_id=row["ticket_id"],
                        subject=row.get("subject", ""),
                        description=row.get("description"),
                        category=row.get("category"),
                        article_id=row.get("article_id"),
                        resolved=row.get("resolved", "false").lower() == "true",
                        created_at=datetime.fromisoformat(row["created_at"]),
                        resolved_at=(
                            datetime.fromisoformat(row["resolved_at"])
                            if row.get("resolved_at")
                            else None
                        ),
                    )

                    await self.repository.create(ticket)
                    imported_count += 1

                except Exception as e:
                    logger.warning(f"Error importing ticket: {e}")
                    skipped_count += 1

            await self.repository.commit()
            logger.info(f"Imported {imported_count} tickets, skipped {skipped_count}")
            return imported_count, skipped_count

        except Exception as e:
            await self.repository.rollback()
            logger.error(f"Error importing tickets: {e}")
            raise

    async def count_tickets_by_article(self, article_id: str) -> int:
        """Count tickets by article"""
        return await self.repository.count_by_article_id(article_id)

    async def count_total_tickets(self) -> int:
        """Count total tickets"""
        return await self.repository.count_all_tickets()
