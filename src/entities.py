from dataclasses import dataclass

from src.db.models import Team, User


@dataclass
class UserWithTeamDTO:
    user: User
    team: Team


@dataclass
class TeamWithMembers:
    team: Team
    members: list[User]
