# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import httpx
import sqlmodel.ext.asyncio.session

from . import exceptions, models, schemas, utils


async def read_players(database: sqlmodel.ext.asyncio.session.AsyncSession):
    result = await database.exec(sqlmodel.select(models.Player))
    return result.all()


async def create_player(database: sqlmodel.ext.asyncio.session.AsyncSession, client: httpx.AsyncClient, player: schemas.PlayerCreate):
    player_uuid = await utils.get_player_uuid(
        client, player.name, player.is_offline_player
    )
    db_player = models.Player.model_validate(
        player, update={"uuid": player_uuid}
    )
    database.add(db_player)
    await database.commit()
    await database.refresh(db_player)
    return db_player


async def read_player(database: sqlmodel.ext.asyncio.session.AsyncSession, player_id: int):
    db_player = await database.get(models.Player, player_id)
    if not db_player:
        raise exceptions.PlayerNotFoundError()
    return db_player


async def update_player(database: sqlmodel.ext.asyncio.session.AsyncSession, client: httpx.AsyncClient, player_id: int, player: schemas.PlayerUpdate):
    db_player = await database.get(models.Player, player_id)
    if not db_player:
        raise exceptions.PlayerNotFoundError()

    update_data = player.model_dump(exclude_unset=True)
    player_data = db_player.model_dump(exclude_unset=True)

    if utils.player_identity_changed(player_data, db_player):
        db_player.sqlmodel_update(update_data)
        db_player.uuid = await utils.get_player_uuid(
            client, db_player.name, db_player.is_offline_player
        )
    else:
        db_player.sqlmodel_update(update_data)

    database.add(db_player)
    await database.commit()
    await database.refresh(db_player)
    return db_player


async def delete_player(database: sqlmodel.ext.asyncio.session.AsyncSession, player_id: int):
    player = await database.get(models.Player, player_id)
    if not player:
        raise exceptions.PlayerNotFoundError()
    await database.delete(player)
    await database.commit()


async def read_player_lists(database: sqlmodel.ext.asyncio.session.AsyncSession):
    result = await database.exec(sqlmodel.select(models.PlayerList))
    return result.all()


async def create_player_list(database: sqlmodel.ext.asyncio.session.AsyncSession, player_list: schemas.PlayerListCreate):
    db_player_list = models.PlayerList.model_validate(player_list)
    database.add(db_player_list)
    await database.commit()
    await database.refresh(db_player_list)
    return db_player_list


async def read_player_list(database: sqlmodel.ext.asyncio.session.AsyncSession, player_list_id: int):
    player_list = await database.get(models.PlayerList, player_list_id)
    if not player_list:
        raise exceptions.PlayerListNotFoundError()
    return player_list


async def update_player_list(database: sqlmodel.ext.asyncio.session.AsyncSession, player_list_id: int, player_list: schemas.PlayerListUpdate):
    db_player_list = await database.get(models.PlayerList, player_list_id)
    if not db_player_list:
        raise exceptions.PlayerListNotFoundError()
    db_player_list.sqlmodel_update(player_list.model_dump(exclude_unset=True))
    database.add(db_player_list)
    await database.commit()
    await database.refresh(db_player_list)
    return db_player_list


async def delete_player_list(database: sqlmodel.ext.asyncio.session.AsyncSession, player_list_id: int):
    player_list = await database.get(models.PlayerList, player_list_id)
    if not player_list:
        raise exceptions.PlayerListNotFoundError()
    await database.delete(player_list)
    await database.commit()


async def read_memberships(database: sqlmodel.ext.asyncio.session.AsyncSession):
    result = await database.exec(sqlmodel.select(models.Membership))
    return result.all()


async def create_membership(database: sqlmodel.ext.asyncio.session.AsyncSession, player_list_id: int, player_id: int, membership: schemas.PlayerListPlayerLinkCreate):
    db_membership = models.Membership.model_validate(
        membership, update={"player_list_id": player_list_id, "player_id": player_id})
    database.add(db_membership)
    await database.commit()
    await database.refresh(db_membership)
    return db_membership


async def update_membership(database: sqlmodel.ext.asyncio.session.AsyncSession, player_list_id: int, player_id: int, membership: schemas.PlayerListPlayerLinkUpdate):
    db_membership = await database.get(
        models.Membership, (player_list_id, player_id))
    if not db_membership:
        raise exceptions.MembershipNotFoundError()
    db_membership.sqlmodel_update(membership.model_dump(exclude_unset=True))
    database.add(db_membership)
    await database.commit()
    await database.refresh(db_membership)
    return db_membership


async def delete_membership(database: sqlmodel.ext.asyncio.session.AsyncSession, player_list_id: int, player_id: int):
    membership = await database.get(
        models.Membership, (player_list_id, player_id))
    if not membership:
        raise exceptions.MembershipNotFoundError()
    await database.delete(membership)
    await database.commit()
