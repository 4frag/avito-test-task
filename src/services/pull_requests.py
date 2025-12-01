from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import PullRequest, User
from src.db.repositories.pull_requests import PullRequestRepository
from src.db.repositories.users import UserRepository
from type_defs import PRStatus

from .exceptions import (
    AuthorCannotBeAReviewerError,
    CannotAssignMoreReviewersError,
    PRAlreadyExistsError,
    PRDoesNotExistError,
    PRNotModifiableError,
    ReviewerFromWrongTeamError,
    ReviewerNotAssignedError,
    UserDoesNotExistError,
    UserIsNotActiveError,
)


MAX_REVIEWERS_COUNT = 2


class PullRequestService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.pull_request_repo = PullRequestRepository(db)
        self.user_repo = UserRepository(db)

    async def auto_assign_reviewers(self, pr_id: str) -> PullRequest:
        pr = await self.pull_request_repo.get_where(
            PullRequest.id == pr_id,
            join_=[PullRequest.assigned_reviewers]
        )
        if not pr:
            raise PRDoesNotExistError(pr_id)

        if pr.status != PRStatus.OPEN:
            raise PRNotModifiableError

        author = await self.user_repo.get_where(User.user_id == pr.author_id)
        if not author:
            raise UserDoesNotExistError(pr.author_id)

        available_reviewers = await self.user_repo.list_where(
            User.team_name == author.team_name,
            User.is_active is True,
            User.user_id != author.user_id
        )

        reviewers_to_assign = available_reviewers[:2]
        pr.assigned_reviewers = reviewers_to_assign

        await self.db.commit()
        return pr

    async def create_pr_with_auto_reviewers(self, **pr_data: dict) -> PullRequest:
        try:
            pr = await self.pull_request_repo.create(**pr_data)
            return await self.auto_assign_reviewers(pr.id)
        except IntegrityError as e:
            error_msg = str(e.orig).lower()

            if 'duplicate key value violates unique constraint "pull_requests_pkey"' in error_msg:
                raise PRAlreadyExistsError(pr_data['id']) from e

            raise

    async def replace_reviewer(
        self,
        pr_id: str,
        old_reviewer_id: str,
        new_reviewer_id: str
    ) -> PullRequest:
        pr = await self.pull_request_repo.get_where(
            PullRequest.id == pr_id,
            join_=[PullRequest.assigned_reviewers]
        )
        if not pr:
            raise PRDoesNotExistError(pr_id)

        if pr.status != PRStatus.OPEN:
            raise PRNotModifiableError

        old_reviewer = await self.user_repo.get_by_id(old_reviewer_id)
        new_reviewer = await self.user_repo.get_by_id(new_reviewer_id)

        if not old_reviewer:
            raise UserDoesNotExistError(old_reviewer_id)
        if not new_reviewer:
            raise UserDoesNotExistError(new_reviewer_id)

        if not old_reviewer.is_active:
            raise UserIsNotActiveError(old_reviewer_id)
        if not new_reviewer.is_active:
            raise UserIsNotActiveError(new_reviewer_id)

        if old_reviewer not in pr.reviewers:
            raise ReviewerNotAssignedError(old_reviewer_id, pr_id)

        if new_reviewer_id == pr.author_id:
            raise AuthorCannotBeAReviewerError

        if pr.author.team_name != new_reviewer.team_name:
            raise ReviewerFromWrongTeamError

        pr.reviewers = [
            new_reviewer if reviewer.id == old_reviewer_id else reviewer
            for reviewer in pr.reviewers
        ]

        await self.db.commit()
        await self.db.refresh(pr)
        return pr

    async def set_reviewers(
        self,
        pr_id: str,
        reviewer_ids: list[str]
    ) -> PullRequest:
        if len(reviewer_ids) > MAX_REVIEWERS_COUNT:
            raise CannotAssignMoreReviewersError(MAX_REVIEWERS_COUNT)

        pr = await self.pull_request_repo.get_where(
            PullRequest.id == pr_id,
            join_=[PullRequest.author]
        )
        if not pr:
            raise PRDoesNotExistError(pr_id)

        if pr.status != PRStatus.OPEN:
            raise PRNotModifiableError

        reviewers = await self.user_repo.get_by_ids(reviewer_ids)
        reviewer_dict = {reviewer.id: reviewer for reviewer in reviewers}

        valid_reviewers = []
        for reviewer_id in reviewer_ids:
            reviewer = reviewer_dict.get(reviewer_id)
            if not reviewer:
                raise UserDoesNotExistError(reviewer_id)
            if not reviewer.is_active:
                raise UserIsNotActiveError(reviewer_id)
            if reviewer_id == pr.author_id:
                raise AuthorCannotBeAReviewerError
            valid_reviewers.append(reviewer)

        author = await self.user_repo.get_by_id(pr.author_id)
        for reviewer in valid_reviewers:
            if reviewer.team_name != author.team_name:
                ReviewerFromWrongTeamError(reviewer_id)

        pr.reviewers = valid_reviewers

        await self.db.commit()
        await self.db.refresh(pr)
        return pr

    async def merge_pr(self, pr_id: str) -> PullRequest:
        pr = await self.pull_request_repo.get_where(
            PullRequest.id == pr_id,
            join_=[PullRequest.assigned_reviewers]
        )
        if not pr:
            raise PRDoesNotExistError(pr_id)

        if pr.status == PRStatus.MERGED:
            return pr

        pr.status = PRStatus.MERGED
        pr.merged_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(pr)
        return pr
