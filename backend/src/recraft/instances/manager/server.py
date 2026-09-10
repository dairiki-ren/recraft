# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import pathlib

import httpx
import pydantic

from .abc import environment, server


class VanillaVersion(pydantic.BaseModel):
    game_version: str


class VanillaServer(server.Server[VanillaVersion]):
    """Server class for vanilla Java installations"""
    mojang_api_mc_versions_endpoint = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"

    @property
    def cmdline(self) -> list[str]:
        return ["java", "-Xmx4G", "-Xms4G", "-jar", "server.jar", "nogui"]

    def __init__(self, environment_manager: environment.Environment):
        self.environment_manager = environment_manager

    @classmethod
    async def get_supported_versions(cls, httpx_async_client: httpx.AsyncClient, refresh: bool = False) -> list[VanillaVersion]:
        """Get a list of versions this server manager supports provisioning

        :return: A list of versions
        :rtype: list[VanillaVersion]
        """
        if cls._supported_versions is None or refresh == True:
            response = await httpx_async_client.get(cls.mojang_api_mc_versions_endpoint)
            cls._supported_versions = [VanillaVersion(
                game_version=version["id"]) for version in response.json()["versions"]]

        return cls._supported_versions

    async def provision(self, version: VanillaVersion, httpx_async_client: httpx.AsyncClient):
        """Provision a vanilla server

        :param version: Version to install
        :type version: VanillaVersion
        """

        response = await httpx_async_client.get(self.mojang_api_mc_versions_endpoint)

        version_manifest_url: str | None = None
        for response_version in response.json()["versions"]:
            if response_version["id"] == version.game_version:
                version_manifest_url = response_version["url"]
                break

        assert version_manifest_url is not None

        response = await httpx_async_client.get(version_manifest_url)
        mc_server_jar_url: str = response.json()["downloads"]["server"]["url"]

        response = await httpx_async_client.get(mc_server_jar_url)

        await self.environment_manager.write_file(await response.aread(), pathlib.Path("server.jar"))
        await self.environment_manager.write_file(b"eula=true", pathlib.Path("eula.txt"))

        server_properties = """
management-server-allowed-origins=
management-server-enabled=true
management-server-host=0.0.0.0
management-server-port=25575
management-server-secret=1XXqMX1G6hACCstlCdz2u6sPyBVtrbqNZXXSvPbM
management-server-tls-enabled=false
management-server-tls-keystore=
management-server-tls-keystore-password="""

        await self.environment_manager.write_file(server_properties.encode(), pathlib.Path("server.properties"))
