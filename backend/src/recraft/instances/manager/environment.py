# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import asyncio
import json
import os
import pathlib

import anyio
import httpx

from .abc import environment


class DockerEnvironment(environment.Environment):
    def __init__(self,
                 identifier: str,
                 container_image: str,
                 host_volume_path: pathlib.Path,
                 httpx_async_client: httpx.AsyncClient,
                 httpx_async_client_docker: httpx.AsyncClient,
                 operations_timeout: float = 45.0,
                 docker_uri: str = "http://docker",
                 container_volume_path: pathlib.Path = pathlib.Path(
                     "/app"),
                 ) -> None:
        """Initialize a Docker environment manager

        :param identifier: Used as container name
        :type identifier: str
        :param container_name: Override the container name
        :type container_name: str
        :param container_image: Container image to use
        :type container_image: str
        :param host_volume_path: Host volume path to mount into the container as
            the service directory
        :type host_volume_path: str | pathlib.Path
        :param httpx_async_client: A :class:`httpx.AsyncClient` for arbitrary
            HTTP tasks, such as downloading files
        :type httpx_async_client: httpx.AsyncClient
        :param httpx_async_client_docker: A :class:`httpx.AsyncClient` preconfigured
            with a valid transport that can access the Docker socket (e.g. via
            UNIX domain socket)
        :type httpx_async_client_docker: httpx.AsyncClient
        :param container_volume_path: Where to mount the service directory
            inside the container, defaults to pathlib.Path("/app")
        :type container_volume_path: str | pathlib.Path, optional
        :param docker_uri: URI of the Docker engine API, defaults to "http://docker"
        :type docker_uri: str, optional
        """
        self.identifier = identifier
        self._container_name = identifier
        self.container_image = container_image
        self.host_volume_path = host_volume_path
        self.httpx_async_client = httpx_async_client
        self.httpx_async_client_docker = httpx_async_client_docker
        self.operations_timeout = operations_timeout
        self.container_volume_path = container_volume_path
        self.docker_uri = docker_uri
        self._container_id: str | None = None
        self._container_ip: str | None = None
        self._start_stop_lock = asyncio.Lock()

    async def _get_container_id(self):
        try:
            if self._container_id is None:
                response = await self.httpx_async_client_docker.get(
                    f"{self.docker_uri}/containers/json",
                    params={
                        "all": True,
                        "filters": json.dumps({"name": [self._container_name]}, separators=(",", ":"))
                    },
                )
                # Find exact name match as Docker engine returns fuzzy matches
                # by default
                for container in response.json():
                    for name in container["Names"]:
                        if name == f"/{self._container_name}":
                            self._container_id = container["Id"]
                            break
        except KeyError:
            # Container does not exist
            pass

        return self._container_id

    def _make_docker_create_body(self, ports: list[int], cmd: list[str]):
        port_bindings = {
            f"{port}/tcp": [{"HostPort": str(port)}]
            for port in ports
        }
        port_bindings.update({
            f"{port}/udp": [{"HostPort": str(port)}]
            for port in ports
        })
        return {"Image": self.container_image,
                "HostConfig": {
                    "Binds": [
                        f"{self.host_volume_path}:{self.container_volume_path}"
                    ],
                    "PortBindings": port_bindings
                },
                "Cmd": cmd,
                "WorkingDir": str(self.container_volume_path),
                "User": f"{os.getuid()}:{os.getgid()}",
                "AttachStdin": True,
                "Tty": True
                }

    async def start(self, cmdline: list[str], ports: list[int] | None = None):
        container_id = await self._get_container_id()
        if ports is None:
            ports = []
        async with self._start_stop_lock:
            if container_id is None:
                # Container not created yet
                body = self._make_docker_create_body(ports, cmdline)
                response = await self.httpx_async_client_docker.post(
                    f"{self.docker_uri}/containers/create",
                    params={"name": self._container_name},
                    json=body
                )

                # TODO: Verify response
                self._container_id = container_id = response.json()["Id"]

            response = await self.httpx_async_client_docker.post(
                f"{self.docker_uri}/containers/{container_id}/start"
            )

    async def stop(self):
        container_id = await self._get_container_id()
        if container_id is None:
            return
        async with self._start_stop_lock:
            await self.httpx_async_client_docker.post(
                f"{self.docker_uri}/containers/{container_id}/stop",
                json={"t": self.operations_timeout}
            )
            response = await self.httpx_async_client_docker.delete(
                f"{self.docker_uri}/containers/{container_id}"
            )
            if response.status_code == 204:
                self._container_id = None
                self._container_ip = None

    async def get_container_ip(self) -> str | None:
        container_id = await self._get_container_id()
        if container_id is None:
            return
        if self._container_ip is None:
            response = await self.httpx_async_client_docker.get(
                f"{self.docker_uri}/containers/{container_id}/json"
            )
            response_json = response.json()

            # TODO: Support multiple networks
            self._container_ip = response_json["NetworkSettings"]["Networks"]["bridge"]["IPAddress"]

        return self._container_ip

    async def get_is_running(self) -> bool:
        # TODO: Proper running handling
        return True

    async def write_file(self, content: bytes, server_path: pathlib.Path, overwrite: bool = False) -> None:
        await anyio.Path(self.host_volume_path).mkdir(exist_ok=True)
        path = anyio.Path(self.host_volume_path / server_path)
        if await path.exists() and not overwrite:
            return

        async with await anyio.open_file(path, "wb") as file:
            await file.write(content)
