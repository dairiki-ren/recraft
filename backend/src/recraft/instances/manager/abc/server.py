# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import abc
import typing

from . import environment

VersionType = typing.TypeVar("VersionType")


class ServerManager[VersionType](abc.ABC):
    """An abstraction class that streamlines provisioning and configuration of
    different server types
    """

    @abc.abstractmethod
    def __init__(self, environment_manager: environment.EnvironmentManager):
        """Initialize a server manager

        :param environment_manager: An environment manager
        :type environment_manager: environment.EnvironmentManager
        """

    @abc.abstractmethod
    @classmethod
    async def get_supported_versions(cls, refresh: bool = False, *args, **kwargs) -> list[VersionType]:
        """Get a list of versions this server manager supports provisioning

        :param refresh: Force a refresh of the version list (implementation
            detail vary), defaults to False
        :type refresh: bool, optional
        :return: A list of versions
        :rtype: list[Version]
        """

    @abc.abstractmethod
    async def provision(self, version: VersionType, *args, **kwargs):
        """Provisions a server instance

        :param version: Game version
        :type version: str
        """
