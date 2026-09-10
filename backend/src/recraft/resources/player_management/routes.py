# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import fastapi

import recraft.deps

from . import schemas, services

router = fastapi.APIRouter()

# Players


@router.post(
    "/players",
    response_model=schemas.PlayerRead,
    status_code=fastapi.status.HTTP_201_CREATED,
)
async def post_player(
    database: recraft.deps.DBSessionDep,
    client: recraft.deps.HttpxAsyncClientDep,
    player: schemas.PlayerCreate,
):
    return await services.create_player(database, client, player)


@router.get("/players", response_model=list[schemas.PlayerRead])
async def get_players(database: recraft.deps.DBSessionDep):
    return await services.read_players(database)


@router.get("/players/{player_id}", response_model=schemas.PlayerRead)
async def get_player(database: recraft.deps.DBSessionDep, player_id: int):
    return await services.read_player(database, player_id)


@router.patch("/players/{player_id}", response_model=schemas.PlayerRead)
async def patch_player(
    database: recraft.deps.DBSessionDep,
    client: recraft.deps.HttpxAsyncClientDep,
    player_id: int,
    player: schemas.PlayerUpdate,
):
    return await services.update_player(database, client, player_id, player)


@router.delete("/players/{player_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def delete_player(database: recraft.deps.DBSessionDep, player_id: int):
    await services.delete_player(database, player_id)


# Player Lists


@router.get("/player-lists", response_model=list[schemas.PlayerListRead])
async def get_player_lists(database: recraft.deps.DBSessionDep):
    return await services.read_player_lists(database)


@router.post(
    "/player-lists",
    response_model=schemas.PlayerListRead,
    status_code=fastapi.status.HTTP_201_CREATED,
)
async def post_player_list(
    database: recraft.deps.DBSessionDep, player_list: schemas.PlayerListCreate
):
    return await services.create_player_list(database, player_list)


@router.get("/player-lists/{player_list_id}", response_model=schemas.PlayerListRead)
async def get_player_list(database: recraft.deps.DBSessionDep, player_list_id: int):
    return await services.read_player_list(database, player_list_id)


@router.patch("/player-lists/{player_list_id}", response_model=schemas.PlayerListRead)
async def patch_player_list(
    database: recraft.deps.DBSessionDep,
    player_list_id: int,
    player_list: schemas.PlayerListUpdate,
):
    return await services.update_player_list(database, player_list_id, player_list)


@router.delete(
    "/player-lists/{player_list_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT
)
async def delete_player_list(database: recraft.deps.DBSessionDep, player_list_id: int):
    return await services.delete_player_list(database, player_list_id)

# Memeberships


@router.get("/memberships/", response_model=list[schemas.PlayerListPlayerLinkRead])
async def get_memberships(database: recraft.deps.DBSessionDep):
    return await services.read_memberships(database)


@router.put("/memberships/", response_model=schemas.PlayerListPlayerLinkRead, status_code=fastapi.status.HTTP_201_CREATED)
async def put_membership(
    database: recraft.deps.DBSessionDep,
    player_list_id: int,
    player_id: int,
    membership: schemas.PlayerListPlayerLinkCreate
):
    return await services.create_membership(database, player_list_id, player_id, membership)


@router.patch("/memberships/", response_model=schemas.PlayerListPlayerLinkRead)
async def patch_membership(
    database: recraft.deps.DBSessionDep,
    player_list_id: int,
    player_id: int,
    membership: schemas.PlayerListPlayerLinkUpdate
):
    return await services.update_membership(database, player_list_id, player_id, membership)


@router.delete("/memberships/", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def delete_membership(database: recraft.deps.DBSessionDep, player_list_id: int, player_id: int):
    await services.delete_membership(database, player_list_id, player_id)
