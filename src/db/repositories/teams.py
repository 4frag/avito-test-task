from src.db.models import Team

from .base import BaseRepository


class TeamRepository(BaseRepository[Team]):
    model = Team
