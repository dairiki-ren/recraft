# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import typing

import fastapi
import httpx
import sqlmodel
import sqlmodel.ext.asyncio.session

import recraft.database
import recraft.instances.manager.instance

from . import config


class State(typing.TypedDict):
    httpx_async_client: httpx.AsyncClient
    instance_managers: dict[int,
                            recraft.instances.manager.instance.DockerInstanceManager]
    configuration: config.Configuration


def get_httpx_async_client(request: fastapi.Request):
    return request.state["httpx_async_client"]


def get_instance_managers(request: fastapi.Request):
    return request.state["instance_managers"]


def get_configuration(request: fastapi.Request):
    return request.state["configuration"]


async def get_db_session():
    async with sqlmodel.ext.asyncio.session.AsyncSession(recraft.database.async_engine) as session:
        yield session


HttpxAsyncClientDep = typing.Annotated[
    httpx.AsyncClient, fastapi.Depends(get_httpx_async_client)
]
InstanceManagersDep = typing.Annotated[
    list[recraft.instances.manager.instance.DockerInstanceManager],
    fastapi.Depends(get_instance_managers)
]
ConfigurationDep = typing.Annotated[
    config.Configuration,
    fastapi.Depends(get_configuration)
]
DBSessionDep = typing.Annotated[
    sqlmodel.ext.asyncio.session.AsyncSession,
    fastapi.Depends(get_db_session)
]
