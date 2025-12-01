from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer

from type_defs import PRStatus


class PullRequestShortSchema(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PRStatus


class PullRequest(PullRequestShortSchema):
    model_config = ConfigDict(from_attributes=True)

    assigned_reviewers: list[str]
    created_at: datetime | None = None
    merged_at: datetime | None = None

    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime | None) -> str | None:
        return created_at.ctime() if created_at else None

    @field_serializer('merged_at')
    def serialize_merged_at(self, merged_at: datetime | None) -> str | None:
        return merged_at.ctime() if merged_at else None


class PullRequestCreateRequestSchema(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str


class MergePRRequest(BaseModel):
    pull_request_id: str
