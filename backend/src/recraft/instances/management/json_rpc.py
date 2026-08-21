# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import asyncio
import collections.abc
import json
import logging
import typing

import websockets.asyncio.client

logger = logging.getLogger(__name__)

EventType = dict[
    str,
    collections.abc.Callable[
        [dict[str, typing.Any]],
        typing.Coroutine[typing.Any, typing.Any, None]]
]


class JSONRPCClient:
    def __init__(self, uri: str, events: EventType | None = None) -> None:
        self.uri = uri
        if events is None:
            events = {}
        self.events = events
        self._task_group = asyncio.TaskGroup()
        self._websocket: websockets.ClientConnection | None = None

    async def connect(self):
        self._websocket = await websockets.asyncio.client.connect(self.uri)

    async def close(self):
        assert self._websocket is not None
        await self._websocket.close()

    async def __aenter__(self):
        await self.connect()

    async def __aexit__(self, exc_type, exc, tb):
        assert self._websocket is not None
        await self._websocket.close()

    async def loop(self):
        try:
            while True:
                assert self._websocket is not None
                message = await self._websocket.recv()
                content = json.loads(message)
                method = content.get("method")
                if not isinstance(method, str):
                    continue
                callback = self.events.get(method)
                if callback is not None:
                    self._task_group.create_task(callback(content))
        except asyncio.CancelledError:
            await self.close()
        except websockets.ConnectionClosedOK:
            pass
