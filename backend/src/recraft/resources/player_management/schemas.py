# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import uuid

import sqlmodel

from . import models


class PlayerCreate(models.PlayerBase):
    pass


class PlayerRead(models.PlayerBase):
    id: int
    uuid: uuid.UUID


class PlayerUpdate(sqlmodel.SQLModel):
    name: str | None = None
    is_offline_player: bool | None = None


class PlayerListCreate(sqlmodel.SQLModel):
    name: str


class PlayerListRead(sqlmodel.SQLModel):
    id: int
    name: str


class PlayerListUpdate(sqlmodel.SQLModel):
    name: str | None = None


class PlayerListPlayerLinkCreate(models.MembershipBase):
    pass


class PlayerListPlayerLinkRead(models.MembershipBase):
    player_id: int
    player_list_id: int


class PlayerListPlayerLinkUpdate(sqlmodel.SQLModel):
    access_permission: models.AccessPermission | None = None
    is_operator: bool | None = None
    operator_level: models.OperatorLevel | None = None
    operator_bypasses_player_limit: bool | None = None
