# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import contextlib
import typing

import fastapi
import hishel
import hishel.httpx
import httpx
from sqlmodel.ext.asyncio.session import AsyncSession

import recraft.instances.lifespan
import recraft.instances.routes
import recraft.resources.routes

from . import config, database, deps, exceptions


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI) -> typing.AsyncGenerator[deps.State]:
    # Database
    await database.init_database()

    # Shared HTTPX clients
    cache_client_storage = hishel.AsyncSqliteStorage(
        database_path=config.configuration.data_path / "hishel_cache.sqlite3")
    cache_client = hishel.httpx.AsyncCacheClient(storage=cache_client_storage)

    httpx_async_client = cache_client
    httpx_docker_transport = httpx.AsyncHTTPTransport(
        uds=str(config.configuration.docker_socket_path))
    httpx_async_client_docker = httpx.AsyncClient(transport=httpx_docker_transport,
                                                  timeout=config.configuration.server_operations_timeout)

    # Instance managers
    instance_managers = {}
    async with AsyncSession(database.async_engine) as session:
        await recraft.instances.lifespan.init(session,
                                              instance_managers,
                                              config.configuration.shared_data_path,
                                              httpx_async_client,
                                              httpx_async_client_docker)

    yield deps.State(
        httpx_async_client=httpx_async_client,
        httpx_async_client_docker=httpx_async_client_docker,
        instance_managers=instance_managers,
        configuration=config.configuration
    )

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
