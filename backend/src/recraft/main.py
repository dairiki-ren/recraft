# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import contextlib
import typing

import fastapi
import httpx

import recraft.instances.routes
import recraft.resources.routes

from . import config, database, deps, exceptions


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI) -> typing.AsyncGenerator[deps.State]:
    # Database
    await database.init_database()
    # Shared HTTPX clients
    httpx_async_client = httpx.AsyncClient(
        timeout=config.configuration.external_api_timeout)
    httpx_docker_transport = httpx.AsyncHTTPTransport(
        uds=str(config.configuration.docker_socket_path))
    httpx_async_client_docker = httpx.AsyncClient(transport=httpx_docker_transport,
                                                  timeout=config.configuration.server_operations_timeout)

    yield deps.State(httpx_async_client=httpx_async_client, httpx_async_client_docker=httpx_async_client_docker)

    await httpx_async_client.aclose()
    await httpx_async_client_docker.aclose()

app = fastapi.FastAPI(lifespan=lifespan)

app.add_exception_handler(exceptions.AppError, exceptions.app_error_handler)
app.add_exception_handler(fastapi.HTTPException,
                          exceptions.default_error_handler)
app.add_exception_handler(fastapi.exceptions.RequestValidationError,
                          exceptions.validation_error_handler)

app.include_router(recraft.instances.routes.router, prefix="/instances")
app.include_router(recraft.resources.routes.router, prefix="/resources")
