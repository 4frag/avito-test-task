from src.db.models import PullRequest

from .base import BaseRepository


class PullRequestRepository(BaseRepository[PullRequest]):
    model = PullRequest
