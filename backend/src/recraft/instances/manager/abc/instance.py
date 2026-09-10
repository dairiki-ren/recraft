# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import abc

from . import game


class Instance(abc.ABC):
    @abc.abstractmethod
    def __init__(self, identifier: str) -> None:
        pass

    @abc.abstractmethod
    async def start(self):
        pass

    @abc.abstractmethod
    async def stop(self):
        pass

    @abc.abstractmethod
    async def set_allowlist(self, allowlist: list[game.Player]):
        pass
