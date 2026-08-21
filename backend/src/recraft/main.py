# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import contextlib
import typing

import fastapi
import fastapi.routing
import httpx

import recraft.instances.routes
import recraft.resources.routes

from . import config, database, deps, exceptions


class DocumentedRoute(fastapi.routing.APIRoute):
    def __init__(self, path: str, endpoint: typing.Callable, **kwargs):
        # Extract OpenAPI responses attached by the decorator
        gathered_responses = getattr(endpoint, "_openapi_responses", {})
        existing_responses = kwargs.get("responses") or {}

        # Merge decorator responses with any manually defined responses
        kwargs["responses"] = {**gathered_responses, **existing_responses}
        super().__init__(path, endpoint, **kwargs)


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI) -> typing.AsyncGenerator[deps.State]:
    # Database
    await database.init_database()
    # Shared requests session
    async with httpx.AsyncClient(timeout=config.configuration.external_api_timeout) as httpx_async_client:
        yield deps.State(httpx_async_client=httpx_async_client)

app = fastapi.FastAPI(lifespan=lifespan)
app.router.route_class = DocumentedRoute

app.add_exception_handler(exceptions.AppError, exceptions.app_error_handler)
app.add_exception_handler(fastapi.HTTPException,
                          exceptions.default_error_handler)
app.add_exception_handler(fastapi.exceptions.RequestValidationError,
                          exceptions.validation_error_handler)

app.include_router(recraft.instances.routes.router, prefix="/instances")
app.include_router(recraft.resources.routes.router, prefix="/resources")
