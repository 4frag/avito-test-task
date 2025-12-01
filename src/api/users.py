from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.tags import APITags
from src.db.database import get_db_connection
from src.schemas.base import ErrorDetailSchema, ErrorResponseSchema
from src.schemas.users import UserGetReviewResponse, UserSchema, UserSetActiveRequestSchema
from src.services.users import UserService
from type_defs import ErrorCode

from .exceptions import NotFoundError


router = APIRouter(prefix='/users', tags=[APITags.USERS])


@router.post(
    '/setIsActive',
    summary='Установить флаг активности пользователя',
    response_model=UserSchema,
    responses={
        status.HTTP_404_NOT_FOUND: {
            'description': 'User not found',
            'model': ErrorResponseSchema
        }
    }
)
async def set_is_active(request: UserSetActiveRequestSchema, db: AsyncSession = Depends(get_db_connection)) -> UserSchema:
    user = await UserService(db).set_is_active(request)

    if user is None:
        raise NotFoundError(detail=ErrorDetailSchema(
            code=ErrorCode.NOT_FOUND,
            message='User not found'
        ))
    return UserSchema.model_validate(user)


@router.get(
    '/getReview',
    summary="Получить PR'ы, где пользователь назначен ревьювером",
)
async def get_review(user_id: str, db: AsyncSession = Depends(get_db_connection)) -> UserGetReviewResponse:
    return UserGetReviewResponse(
        user_id=user_id,
        pull_requests=await UserService(db).get_user_pull_requests_to_review(user_id)
    )
