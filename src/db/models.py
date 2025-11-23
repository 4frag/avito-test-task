from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ForeignKey


class Base(DeclarativeBase):
    pass


class Team(Base):
    __tablename__ = 'teams'

    name: Mapped[str] = mapped_column(primary_key=True, nullable=False)


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[str] = mapped_column(primary_key=True)
    username: Mapped[str] 
    is_active: Mapped[bool]

    team_name: Mapped[str] = mapped_column(ForeignKey('teams.name'))
