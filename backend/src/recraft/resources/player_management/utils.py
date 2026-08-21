# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import json
import uuid

import httpx
import pydantic

from . import exceptions, models

MINECRAFT_PROFILE_API_URL = (
    "https://api.minecraftservices.com/minecraft/profile/lookup/name/{player_name}"
)


def player_identity_changed(new_data: dict, db_player: models.Player):
    name = new_data.get("name", db_player.name)
    is_offline_player = new_data.get(
        "is_offline_player", db_player.is_offline_player)

    identity_changed = bool(
        ("name" in new_data and name != db_player.name) or
        ("is_offline_player" in new_data and is_offline_player !=
            db_player.is_offline_player)
    )

    return identity_changed


class MinecraftAPIPlayerProfile(pydantic.BaseModel):
    id: uuid.UUID
    name: str


def _get_offline_player_uuid(player_name: str) -> uuid.UUID:
    # Reference:
    # https://gist.github.com/Nikdoge/474f74688b52865bf8d682a97fd4f2fe
    player_uuid_namespace = "OfflinePlayer:"
    player_uuid = f"{player_uuid_namespace}{player_name}"

    class EmptyUUID:
        # Workaround class as uuid.uuid3() requires a UUID namespace but we
        # don't have one
        bytes = b''
    return uuid.uuid3(EmptyUUID, player_uuid)  # type: ignore


async def get_player_uuid(
    client: httpx.AsyncClient, player_name: str, is_offline_player: bool
):
    if is_offline_player:
        return _get_offline_player_uuid(player_name)

    request_url = MINECRAFT_PROFILE_API_URL.format(player_name=player_name)

    try:
        response = await client.get(request_url)
    except httpx.TimeoutException:
        raise exceptions.MinecraftProfileApiTimeoutError(
            params=exceptions.MinecraftProfileApiErrorParams(request_uri=request_url))

    if not response.is_success:
        raise exceptions.MinecraftProfileApiNonSuccessError(
            params=exceptions.MinecraftProfileApiErrorParams(status_code=response.status_code, request_uri=request_url, text=response.text))

    try:
        data = response.json()
    except json.JSONDecodeError:
        raise exceptions.MinecraftProfileApiJsonDecodeError(
            params=exceptions.MinecraftProfileApiErrorParams(status_code=response.status_code, request_uri=request_url, text=response.text))

    try:
        profile = MinecraftAPIPlayerProfile.model_validate(data)
        return profile.id
    except pydantic.ValidationError:
        raise exceptions.MinecraftProfileApiResponseValidationError(
            params=exceptions.MinecraftProfileApiErrorParams(status_code=response.status_code, request_uri=request_url, text=response.text))
