# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import asyncio
import logging
import pathlib

import httpx

from recraft.instances.manager.abc.game import Player

from . import environment, game, server
from .abc import instance

logger = logging.getLogger("uvicorn.error")


class DockerInstanceManager(instance.Instance):
    # TODO: Extract Docker-related functionality to a dependency in the root directory
    def __init__(self, identifier: str, shared_path: pathlib.Path, httpx_async_client: httpx.AsyncClient, httpx_async_client_docker: httpx.AsyncClient) -> None:
        self.identifier = identifier
        self.httpx_async_client = httpx_async_client
        self.httpx_async_client_docker = httpx_async_client_docker
        self._environment_manager = environment.DockerEnvironment(
            identifier=identifier,
            container_image="eclipse-temurin:26-alpine",
            host_volume_path=shared_path / identifier,
            httpx_async_client=httpx_async_client,
            httpx_async_client_docker=httpx_async_client_docker
        )
        self._server_manager = server.VanillaServer(
            self._environment_manager)
        self._game_manager: game.JsonRpcGame | None = None

    async def start(self, allowlist: list[Player]):
        await self._environment_manager.start(self._server_manager.cmdline, ports=[25565, 25575])
        ip = await self._environment_manager.get_container_ip()
        assert ip is not None
        if self._game_manager is None:
            self._game_manager = game.JsonRpcGame(
                ip, 25575, "1XXqMX1G6hACCstlCdz2u6sPyBVtrbqNZXXSvPbM")
            for i in range(10):
                try:
                    await self._game_manager.connect()
                except (ConnectionRefusedError, RuntimeError):
                    logger.exception("Caught error")
                    await asyncio.sleep(1)
                else:
                    logger.info("Connected!")
                    break
            else:
                self._game_manager = None
                logger.info("Not connected")
                return
        await self._game_manager.set_allowlist(allowlist)

    async def stop(self):
        if self._game_manager is not None:
            await self._game_manager.disconnect()
            self._game_manager = None
        await self._environment_manager.stop()

    async def provision(self):
        await self._server_manager.provision(server.VanillaVersion(game_version="26.2"), self.httpx_async_client)

    async def set_allowlist(self, allowlist: list[Player]):
        assert self._game_manager is not None
        return await self._game_manager.set_allowlist(allowlist)
