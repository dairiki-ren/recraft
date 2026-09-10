# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import asyncio

import mcsmp
import mcsmp.schemas

from .abc import game


class JsonRpcGame(game.Game):
    def __init__(self, host: str, port: int, secret: str, **kwargs):
        self.host = host
        self.port = port
        self.secret = secret
        self._mcsmp_client = mcsmp.Client(host, port, secret, **kwargs)
        self._loop_task: asyncio.Task | None = None

    async def __aenter__(self):
        await self.connect()

    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()
        return exc_type, exc, tb

    async def connect(self):
        await self._mcsmp_client.connect()

    async def disconnect(self):
        await self._mcsmp_client.close()

    async def set_allowlist(self, allowlist: list[game.Player]):
        await self._mcsmp_client.allow_list.set(
            [mcsmp.schemas.Player(name=player.name, id=str(player.id))
             for player in allowlist]
        )
