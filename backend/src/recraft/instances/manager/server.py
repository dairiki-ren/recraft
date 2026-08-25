# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import httpx
import pydantic

from .abc import environment, server


class VanillaVersion(pydantic.BaseModel):
    game_version: str


class VanillaServerManager(server.ServerManager[VanillaVersion]):
    """Server manager for vanilla Java installations"""
    mojang_api_mc_versions_endpoint = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"

    def __init__(self, environment_manager: environment.EnvironmentManager):
        self.environment_manager = environment_manager

    @classmethod
    async def get_supported_versions(cls, refresh: bool = False, httpx_async_client: httpx.AsyncClient | None = None, *args, **kwargs) -> list[VanillaVersion]:
        """Get a list of versions this server manager supports provisioning

        :return: A list of versions
        :rtype: list[VanillaVersion]
        """
        if cls._supported_versions is None or refresh == True:
            external_httpx_async_client = True
            if httpx_async_client is None:
                external_httpx_async_client = False
                httpx_async_client = httpx.AsyncClient()
            response = await httpx_async_client.get(cls.mojang_api_mc_versions_endpoint)
            cls._supported_versions = [VanillaVersion(
                game_version=version["id"]) for version in response.json()["versions"]]
            if not external_httpx_async_client:
                await httpx_async_client.aclose()

        return cls._supported_versions
