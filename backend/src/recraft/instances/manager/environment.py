# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only


from anyio.abc import Process

from .abc import environment


class ProcessEnvironmentManager(environment.Environment):
    def __init__(self, identifier: str, operations_timeout: float = 45) -> None:
        self.identifier = identifier
        self.operations_timeout = operations_timeout
        self.process: Process | None = None
