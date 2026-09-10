# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import pathlib

import httpx
import sqlmodel.ext.asyncio.session

from . import models
from .manager import instance


async def init(session: sqlmodel.ext.asyncio.session.AsyncSession,
               instance_managers: dict,
               shared_path: pathlib.Path,
               httpx_async_client: httpx.AsyncClient,
               httpx_async_client_docker: httpx.AsyncClient):
    results = (await session.exec(sqlmodel.select(models.Instance))).all()
    for result in results:
        instance_managers[result.id] = instance.DockerInstanceManager(
            f"recraft_{result.id}",
            shared_path,
            httpx_async_client,
            httpx_async_client_docker,
        )
