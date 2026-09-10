# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import abc
import pathlib


class Environment(abc.ABC):
    """An abstraction class that allows unified access to an instance's process, networking
    and file management
    """

    @abc.abstractmethod
    def __init__(self, identifier: str) -> None:
        """Initialize an environment

        :param identifier: A token that uniquely identifies an instance. How
            this token is used depends on the exact implementation of the
            EnvironmentManager. It is recommended to namespace this identifier
            per application.
        :type identifier: str
        """

    @abc.abstractmethod
    async def start(self, cmdline: list[str]) -> None:
        """Runs :param:`cmdline` to start the server process

        :param cmdline: cmdline to execute
        :type cmdline: list[str]
        """

    @abc.abstractmethod
    async def stop(self) -> None:
        """Stop server process"""

    @abc.abstractmethod
    async def get_is_running(self) -> bool:
        """Get whether the server process is currently running"""

    @abc.abstractmethod
    async def write_file(self, content: bytes, server_path: pathlib.Path, overwrite: bool = False) -> None:
        """Write contents to a file

        :param content: Content to write into the file
        :type content: bytes
        :param server_path: Path to write to, relative to the service directory
        :type server_path: pathlib.Path
        :param overwrite: Overwrite file contents if file already exists,
            defaults to False
        :type overwrite: bool, optional
        """
