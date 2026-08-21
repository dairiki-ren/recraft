# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import enum
import uuid

import sqlmodel

import recraft.instances.models

# Players


class PlayerBase(sqlmodel.SQLModel):
    name: str
    is_offline_player: bool = False


class Player(PlayerBase, table=True):
    id: int = sqlmodel.Field(default=None, primary_key=True)
    uuid: uuid.UUID
    player_list_links: list[PlayerListPlayerLink] = sqlmodel.Relationship(
        back_populates="player", cascade_delete=True)


# Player Lists


class PlayerList(sqlmodel.SQLModel, table=True):
    id: int = sqlmodel.Field(default=None, primary_key=True)
    name: str
    player_links: list[PlayerListPlayerLink] = sqlmodel.Relationship(
        back_populates="player_list", cascade_delete=True)

    used_by_instances: list[recraft.instances.models.Instance] = sqlmodel.Relationship(
        back_populates="player_list")


class AccessPermission(enum.Enum):
    BANNED = 0
    WHITELISTED = 1


class OperatorLevel(enum.Enum):
    MODERATOR = 1
    GAMEMASTER = 2
    ADMIN = 3
    OWNER = 4


class PlayerListPlayerLinkBase(sqlmodel.SQLModel):
    access_permission: AccessPermission | None = None
    is_operator: bool = False
    operator_level: OperatorLevel = OperatorLevel.GAMEMASTER
    operator_bypasses_player_limit: bool = False


class PlayerListPlayerLink(PlayerListPlayerLinkBase, table=True):
    player_id: int = sqlmodel.Field(foreign_key="player.id", primary_key=True)
    player_list_id: int = sqlmodel.Field(
        foreign_key="playerlist.id", primary_key=True)

    player: Player = sqlmodel.Relationship(back_populates="player_list_links")
    player_list: PlayerList = sqlmodel.Relationship(
        back_populates="player_links")
