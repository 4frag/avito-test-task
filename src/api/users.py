from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.tags import APITags
from src.db.database import get_db
from src.services.users import UserService
from .schemas import UserSetActiveRequestSchema, UserSchema, ErrorResponseSchema, ErrorDetailSchema, ErrorCode


router = APIRouter(prefix='/users', tags=[APITags.USERS])


@router.post(
    '/setIsActive',
    response_model=UserSchema,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found",
            "model": ErrorResponseSchema
        }
    }
)
async def set_is_active(request: UserSetActiveRequestSchema, db: AsyncSession = Depends(get_db)):    
    service = UserService(db)
    result = await service.update_user(user_id=request.user_id, is_active=request.is_active)

    if not result:
        response = ErrorResponseSchema(
            error=ErrorDetailSchema(
                code=ErrorCode.NOT_FOUND,
                message="User not found"
            )
        ).model_dump()
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=response
        )
    response = UserSchema.model_validate(result).model_dump()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response
    )
