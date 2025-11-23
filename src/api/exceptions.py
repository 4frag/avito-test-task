from typing import Any

from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    def __init__(
        self, detail: Any | None = None, headers: dict[str, Any] | None = None  # noqa: ANN401
    ) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)


class BadRequestError(HTTPException):
    def __init__(
        self, detail: Any | None = None, headers: dict[str, Any] | None = None  # noqa: ANN401
    ) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, headers)
