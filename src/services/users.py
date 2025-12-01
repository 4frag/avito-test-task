from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import PullRequest, User
from src.db.repositories.pull_requests import PullRequestRepository
from src.db.repositories.teams import TeamRepository
from src.db.repositories.users import UserRepository
from src.schemas.users import UserSetActiveRequestSchema


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.team_repo = TeamRepository(db)
        self.pull_request_repo = PullRequestRepository(db)

    async def set_is_active(self, schema: UserSetActiveRequestSchema) -> User | None:
        result = await self.user_repo.update_one(User.user_id == schema.user_id, is_active=schema.is_active)
        await self.db.commit()
        return result

    async def get_user_pull_requests_to_review(self, user_id: str) -> list[PullRequest]:
        return await self.pull_request_repo.list_where(PullRequest.author_id == user_id)
