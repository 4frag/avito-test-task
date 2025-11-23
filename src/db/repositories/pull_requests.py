from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.db.models import PullRequest

from .base import BaseRepository


class PullRequestRepository(BaseRepository[PullRequest]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(PullRequest, db)

    async def get_by_id_with_reviewers_and_author(self, pr_id: str) -> PullRequest | None:
        result = await self.db.execute(
            select(PullRequest)
            .options(
                selectinload(PullRequest.assigned_reviewers),
                joinedload(PullRequest.author)
            )
            .where(PullRequest.id == pr_id)
        )
        return result.scalar_one_or_none()
