# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import abc
import pathlib


class EnvironmentManager(abc.ABC):
    """An abstraction class that allows unified access to a server's process, networking
    and file management
    """
    @abc.abstractmethod
    def __init__(self, identifier: str, operations_timeout: float = 45.0) -> None:
        """Initialize an environment manager

        :param identifier: A token that uniquely identifies a server. How this
            token is used depends on the exact implementation of the
            EnvironmentManager. It is recommended to namespace this identifier
            per application instance.
        :type identifier: str
        :param operations_timeout: Timeout for graceful start/stop and status
            query operations
        :type operations_timeout: float
        """
    @abc.abstractmethod
    async def start(self, cmdline: list[str]) -> None:
        """Runs :param:`cmdline` to start the server process

        :param cmdline: cmdline to execute
        :type cmdline: list[str]
        """

    @abc.abstractmethod
    async def stop(self, *args, **kwargs) -> None:
        """Stop server process"""

    @abc.abstractmethod
    async def get_is_running(self) -> bool:
        """Get whether the server process is currently running"""

    @abc.abstractmethod
    async def forward_path(self, host_path: pathlib.Path, server_path: pathlib.Path, read_only: bool = True) -> None:
        """Make a host path available to the server environment

        :param host_path: The path on the host that should be exposed
        :type host_path: pathlib.Path
        :param server_path: Where the path should be made available in the server
            environment. This is should be interpreted as a relative path to the
            service directory.
        :type server_path: pathlib.Path
        :param read_only: Whether the file will be only used read-only by the
            server. The implementation may decide to pick different strategies
            for exposing the path, e.g. using a read-only symlink instead of a
            full copy; defaults to True
        :type read_only: bool, optional
        """
