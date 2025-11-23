from .base import BaseRepository
from src.db.models import Team


class TeamRepository(BaseRepository[Team]):
    def __init__(self, db):
        super().__init__(Team, db)