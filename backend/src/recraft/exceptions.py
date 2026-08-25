# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import re
import typing

import fastapi
import fastapi.responses
import pydantic


def upper_join(s: str, join_with: str):
    upper_name_parts = [part.upper()
                        for part in re.findall("[A-Z][^A-Z]*", s)]
    return join_with.join(upper_name_parts)


ParamsT = typing.TypeVar("ParamsT", bound=pydantic.BaseModel)


class ErrorResponse(pydantic.BaseModel):
    pass


class GenericErrorResponse[ParamsT: pydantic.BaseModel](ErrorResponse):
    message: str = pydantic.Field(..., description="Error message")
    error_code: str = pydantic.Field(..., description="Machine-readable code")
    params: ParamsT = pydantic.Field(...,
                                     description="Contextual error parameters")


class AppError(Exception):
    status_code = 500
    error_code = upper_join(__name__, "_")  # "AppError" becomes APP_ERROR
    message = "An error has occured"
    params_model: type[pydantic.BaseModel] | None = None

    @classmethod
    def get_response_model(cls) -> type[ErrorResponse]:
        if cls.params_model:
            return GenericErrorResponse[cls.params_model]

        # Fallback if no params are specified
        class StandardErrorResponse(ErrorResponse):
            message: str = cls.message
            error_code: str = cls.error_code

        return StandardErrorResponse

    @classmethod
    def openapi_response(cls) -> dict[str, typing.Any]:
        return {
            "model": cls.get_response_model(),
            "description": cls.message,
        }

    def __init__(self, params: pydantic.BaseModel | None = None, message: str | None = None):
        self.message = message or self.message
        self.params = params
        super().__init__(self.message)

# Some errors to inherit from


class NotFoundError(AppError):
    status_code = 404
    message = "The resource could not be found"


class LockedError(AppError):
    status_code = 409
    message = "The resource is currently locked"


class ExternalError(AppError):
    status_code = 503
    message = "An external error has occured"


class ExternalApiErrorParams(pydantic.BaseModel):
    status_code: int | None = None
    request_uri: str
    text: str | None = None


class ExternalApiError(AppError):
    message = "An error has occured with an external API"
    params_model = ExternalApiErrorParams


class ErrorContent(pydantic.BaseModel):
    error_code: str
    message: str
    params: dict[str, typing.Any] | None = None


def app_error_handler(request: fastapi.Request, exc: Exception):
    # The assert line below avoids type checking errors when registering the
    # exception handler, as FastAPI.add_exception_handler only accepts
    # Callable[["Request", Exception], "Response | Awaitable[Response]"] and
    # AppError doesn't match Exception
    assert isinstance(exc, AppError)
    error_content = ErrorContent.model_validate(exc, extra="ignore")
    return fastapi.responses.JSONResponse(
        status_code=exc.status_code,
        content=error_content.model_dump(exclude_unset=True)
    )


def default_error_handler(request: fastapi.Request, exc: Exception):
    assert isinstance(exc, fastapi.HTTPException)
    # Turns something like "Not Found" to "NOT_FOUND"
    # Refer to http.HTTPStatus(status_code).phrase which is used by
    # StarletteHTTPException as well
    error_code = upper_join("".join(exc.detail.split()), "_")
    error_content = ErrorContent(error_code=error_code, message=exc.detail)
    return fastapi.responses.JSONResponse(
        status_code=exc.status_code,
        content=error_content.model_dump(exclude_unset=True)
    )


def validation_error_handler(request: fastapi.Request, exc: Exception):
    assert isinstance(exc, fastapi.exceptions.RequestValidationError)
    error_code = "VALIDATION_ERROR"
    error_content = ErrorContent(
        error_code=error_code, message="Request data could not be validated", params={"errors": exc.errors()})
    return fastapi.responses.JSONResponse(
        status_code=422,
        content=error_content.model_dump(exclude_unset=True)
    )
