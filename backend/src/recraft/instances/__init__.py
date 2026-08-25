# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import abc


class MinecraftServer(abc.ABC):
    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    def apply_allowlist(self, allowlist: int):
        pass
