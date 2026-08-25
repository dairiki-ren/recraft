# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import asyncio
import logging
import pathlib

import httpx

from .abc import environment

logger = logging.getLogger(__name__)


class DockerEnvironmentManager(environment.EnvironmentManager):
    def __init__(self,
                 identifier: str,
                 container_image: str,
                 host_volume_path: str | pathlib.Path,
                 httpx_async_client: httpx.AsyncClient,
                 operations_timeout: float = 45.0,
                 docker_uri: str = "http://docker",
                 ports: list[int] | None = None,
                 container_volume_path: str | pathlib.Path = pathlib.Path(
                     "/app"),
                 ) -> None:
        """Initialize a Docker environment manager

        :param identifier: See :meth:`EnvironmentManager.__init__`
        :type identifier: str
        :param container_name: Override the container name
        :type container_name: str
        :param container_image: _description_
        :type container_image: str
        :param host_volume_path: _description_
        :type host_volume_path: str | pathlib.Path
        :param ports: _description_
        :type ports: list[int]
        :param httpx_async_client: A :class:`httpx.AsyncClient` preconfigured
            with a valid transport that can access the Docker socket (e.g. via
            UNIX domain socket)
        :type httpx_async_client: httpx.AsyncClient
        :param container_volume_path: _description_, defaults to pathlib.Path( "/app")
        :type container_volume_path: str | pathlib.Path, optional
        :param docker_uri: _description_, defaults to "http://docker"
        :type docker_uri: _type_, optional
        """
        self.identifier = identifier
        self._container_name = identifier
        self.container_image = container_image
        self.host_volume_path = host_volume_path
        self.ports = ports
        self.httpx_async_client = httpx_async_client
        self.operations_timeout = operations_timeout
        self.container_volume_path = container_volume_path
        self.docker_uri = docker_uri
        self._container_id: str | None = None
        self._start_stop_lock = asyncio.Lock()

    async def _get_container_id(self):
        try:
            if self._container_id is None:
                response = await self.httpx_async_client.get(
                    f"{self.docker_uri}/containers/json",
                    params={
                        "all": True,
                        "filters": str({"name": self._container_name})},
                )
                # Find exact name match as Docker engine returns fuzzy matches
                # by default
                for container in response.json():
                    if container["Name"] == self._container_name:
                        self._container_id = container["Id"]
                        break
        except KeyError:
            # Container does not exist
            pass

        return self._container_id

    async def start(self, cmdline: list[str]):
        container_id = await self._get_container_id()
        async with self._start_stop_lock:
            if container_id is None:
                # Container not created yet
                response = await self.httpx_async_client.post(
                    f"{self.docker_uri}/containers/create",
                    json={"Name": self._container_name,
                          "Image": self.container_image,
                          "Mounts": [
                              {
                                  "Type": "bind",
                                  "Source": self.host_volume_path,
                                  "Destination": self.container_volume_path
                              }
                          ],
                          "Cmd": cmdline},
                )
                self._container_id = container_id = response.json()["Id"]

            response = await self.httpx_async_client.post(
                f"{self.docker_uri}/containers/{container_id}/start"
            )

    async def stop(self):
        container_id = await self._get_container_id()
        if container_id is None:
            return
        async with self._start_stop_lock:
            await self.httpx_async_client.post(
                f"{self.docker_uri}/containers/{container_id}/stop",
                json={"t": self.operations_timeout}
            )
            await self.httpx_async_client.post(
                f"{self.docker_uri}/containers/{container_id}/remove"
            )
