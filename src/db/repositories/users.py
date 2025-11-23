from .base import BaseRepository
from src.db.models import User


class UserRepository(BaseRepository[User]):
    def __init__(self, db):
        super().__init__(User, db)