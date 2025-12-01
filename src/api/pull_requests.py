from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db_connection
from src.schemas.base import ErrorDetailSchema
from src.schemas.pull_requests import MergePRRequest, PullRequest, PullRequestCreateRequestSchema
from src.services.exceptions import PRAlreadyExistsError, PRDoesNotExistError
from src.services.pull_requests import PullRequestService
from src.type_defs import ErrorCode

from .exceptions import NotFoundError
from .tags import APITags


router = APIRouter(prefix='/pullRequests', tags=[APITags.PULL_REQUESTS])


@router.post('/create', status_code=201)
async def create_pr(request: PullRequestCreateRequestSchema, db: AsyncSession = Depends(get_db_connection)) -> PullRequest:
    try:
        pr = await PullRequestService(db).create_pr_with_auto_reviewers(
            id=request.pull_request_id,
            name=request.pull_request_name,
            author_id=request.author_id
        )
        return PullRequest(
            pull_request_id=pr.id,
            pull_request_name=pr.name,
            author_id=pr.author_id,
            assigned_reviewers=[r.user_id for r in pr.assigned_reviewers],
            status=pr.status,
            created_at=pr.created_at,
            merged_at=pr.merged_at
        )
    except PRAlreadyExistsError as e:
        raise NotFoundError(
            detail=ErrorDetailSchema(
                code=ErrorCode.PR_EXISTS,
                message=str(e)
            )
        ) from e


@router.post(
    '/merge',
    responses={
        200: {
            'description': 'PR в состоянии MERGED',
            'content': {
                'application/json': {
                    'example': {
                        'pr': {
                            'pull_request_id': 'pr-1001',
                            'pull_request_name': 'Add search',
                            'author_id': 'u1',
                            'status': 'MERGED',
                            'assigned_reviewers': ['u2', 'u3'],
                            'mergedAt': '2025-10-24T12:34:56Z'
                        }
                    }
                }
            }
        },
        404: {
            'description': 'PR не найден',
            'content': {
                'application/json': {
                    'schema': {'$ref': '#/components/schemas/ErrorResponse'}
                }
            }
        }
    }
)
async def merge_pull_request(
        request: MergePRRequest,
        db: AsyncSession = Depends(get_db_connection),
        ) -> PullRequest:
    pr_service = PullRequestService(db)
    try:
        pr = await pr_service.merge_pr(request.pull_request_id)

        return PullRequest(
            pull_request_id=pr.id,
            pull_request_name=pr.name,
            author_id=pr.author_id,
            assigned_reviewers=[r.user_id for r in pr.assigned_reviewers],
            status=pr.status,
            created_at=pr.created_at,
            merged_at=pr.merged_at
        )
    except PRDoesNotExistError as e:
        raise NotFoundError(
            detail=ErrorDetailSchema(
                code=ErrorCode.NOT_FOUND,
                message=str(e)
            )
        ) from e
