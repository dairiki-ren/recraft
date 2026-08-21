# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import sqlmodel

import recraft.resources.player_management.models


class InstanceBase(sqlmodel.SQLModel):
    name: str = sqlmodel.Field(default="")


class Instance(InstanceBase, table=True):
    id: int = sqlmodel.Field(default=None, primary_key=True)
    player_list_id: int | None = sqlmodel.Field(default=None,
                                                foreign_key="playerlist.id")

    player_list: recraft.resources.player_management.models.PlayerList | None = sqlmodel.Relationship(
        back_populates="used_by_instances")


class InstanceCreate(InstanceBase):
    player_list_id: int | None = None


class InstanceRead(InstanceBase):
    id: int
    player_list_id: int | None
