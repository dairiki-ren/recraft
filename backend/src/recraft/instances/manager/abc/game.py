# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import abc
import uuid

import pydantic


class Player(pydantic.BaseModel):
    """A simple player model for the game manager"""
    name: str
    id: uuid.UUID


class GameManager(abc.ABC):
    """An abstraction class that provides access to game-specific features such
    as player management or event handling
    """
    @abc.abstractmethod
    def __init__(self):
        """Initialize a game manager

        Required arguments may vary per implementation
        """

    @abc.abstractmethod
    async def __aenter__(self):
        await self.connect()

    @abc.abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()
        return exc_type, exc, tb

    @abc.abstractmethod
    async def connect(self):
        """Connect to the game

        Some implementations may require connecting to the game before being
        able to perform actions. You must always assume that this function needs
        to be called before performing any actions provided by the game manager.
        Alternatively, you can use the game manager as a context manager which
        automatically handles connection and disconnection.
        """

    @abc.abstractmethod
    async def disconnect(self):
        """Disconnect from the game

        Some implementations may require connecting to the game before being
        able to perform actions. You must always assume that this function needs
        to be called to cleanly shutdown outbound connections. Alternatively,
        you can use the game manager as a context manager which automatically
        handles connection and disconnection.
        """

    @abc.abstractmethod
    async def set_allowlist(self, allowlist: list[Player]):
        """Sets the allowlist

        Sets the player allowlist to :param:`allowlist` and applies it

        :param allowlist: _description_
        :type allowlist: list[Player]
        """
