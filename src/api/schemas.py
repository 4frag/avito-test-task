from datetime import datetime

from pydantic import BaseModel, field_serializer

from src.types import ErrorCode, PRStatus


# Error Schemas
class ErrorDetailSchema(BaseModel):
    code: ErrorCode
    message: str


class ErrorResponseSchema(BaseModel):
    error: ErrorDetailSchema

    class Config:
        json_schema_extra = {
            'example': {
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'resource not found'
                }
            }
        }


# Team Schemas
class TeamMemberSchema(BaseModel):
    user_id: str
    username: str
    is_active: bool


class TeamSchema(BaseModel):
    team_name: str
    members: list[TeamMemberSchema]


# User Schemas
class UserSchema(BaseModel):
    user_id: str
    username: str
    is_active: bool
    team_name: str

    class Config:
        populate_by_name = True


# Pull Request Schemas
class PullRequestShortSchema(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PRStatus


class PullRequest(PullRequestShortSchema):
    assigned_reviewers: list[str]
    created_at: datetime | None = None
    merged_at: datetime | None = None

    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime | None) -> str | None:
        return created_at.ctime() if created_at else None

    @field_serializer('merged_at')
    def serialize_merged_at(self, merged_at: datetime | None) -> str | None:
        return merged_at.ctime() if merged_at else None


# Requests schemas
class UserSetActiveRequestSchema(BaseModel):
    user_id: str
    is_active: bool

    class Config:
        json_schema_extra = {
            'example': {
                'user_id': 'u2',
                'is_active': False
            }
        }


class PullRequestCreateRequestSchema(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str


class MergePRRequest(BaseModel):
    pull_request_id: str
