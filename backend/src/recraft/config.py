# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import pathlib

import pydantic
import pydantic_settings


class Configuration(pydantic_settings.BaseSettings):
    app_name: str = "Recraft"
    data_path: pathlib.Path = pathlib.Path("/data")
    external_api_timeout: float = 5.0
    # used for server start/stop e.g. via Docker API, which may take longer than
    # ordinary API requests
    server_operations_timeout: float = 45.0
    shared_data_path: pathlib.Path = pathlib.Path("/shared")
    sqlite_path: pathlib.Path = pydantic.Field(
        default_factory=lambda data: data["data_path"] / "db.sqlite3"
    )
    docker_socket_path: pathlib.Path = pathlib.Path("/var/run/docker.sock")


configuration = Configuration()
