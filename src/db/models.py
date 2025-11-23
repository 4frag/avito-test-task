from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.types import PRStatus


class Base(DeclarativeBase):
    pass


class Team(Base):
    __tablename__ = 'teams'

    name: Mapped[str] = mapped_column(primary_key=True, nullable=False)


pr_reviewers = Table(
    'pr_reviewers',
    Base.metadata,
    Column('pr_id', String, ForeignKey('pull_requests.id'), primary_key=True),
    Column('user_id', String, ForeignKey('users.user_id'), primary_key=True)
)


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[str] = mapped_column(primary_key=True)
    username: Mapped[str]
    is_active: Mapped[bool]

    team_name: Mapped[str] = mapped_column(ForeignKey('teams.name'))

    pull_requests: Mapped[list['PullRequest']] = relationship(  # ← изменил название
        'PullRequest',
        back_populates='author',
        foreign_keys='PullRequest.author_id'
    )
    reviewed_prs: Mapped[list['PullRequest']] = relationship(
        'PullRequest',
        secondary=pr_reviewers,
        back_populates='assigned_reviewers'
    )


class PullRequest(Base):
    __tablename__ = 'pull_requests'

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    author_id: Mapped[str] = mapped_column(ForeignKey('users.user_id'))
    status: Mapped[PRStatus] = mapped_column(String(6), default=PRStatus.OPEN)
    assigned_reviewers: Mapped[list['User']] = relationship(
        'User',
        secondary=pr_reviewers,
        back_populates='reviewed_prs'
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    merged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None
    )

    author: Mapped['User'] = relationship('User', back_populates='pull_requests')
