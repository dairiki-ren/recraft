# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import typing

import fastapi
import httpx
import sqlmodel
import sqlmodel.ext.asyncio.session

import recraft.database


class State(typing.TypedDict):
    httpx_async_client: httpx.AsyncClient
    httpx_async_client_docker: httpx.AsyncClient


def get_httpx_async_client(request: fastapi.Request):
    return request.state["httpx_async_client"]


def get_httpx_async_client_docker(request: fastapi.Request):
    return request.state["httpx_async_client_docker"]


async def get_db_session():
    async with sqlmodel.ext.asyncio.session.AsyncSession(recraft.database.async_engine) as session:
        yield session


HttpxAsyncClientDep = typing.Annotated[
    httpx.AsyncClient, fastapi.Depends(get_httpx_async_client)
]
HttpxAsyncClientDockerDep = typing.Annotated[
    httpx.AsyncClient, fastapi.Depends(get_httpx_async_client_docker)
]
DBSessionDep = typing.Annotated[sqlmodel.ext.asyncio.session.AsyncSession,
                                fastapi.Depends(get_db_session)]
