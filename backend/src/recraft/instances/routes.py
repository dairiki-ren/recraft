# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import fastapi
import sqlmodel

import recraft.deps
from recraft.resources.player_management.models import (
    AccessPermission,
    Player,
    PlayerListPlayerLink,
)

from . import models
from .manager.abc.game import Player as AllowlistPlayer
from .manager.instance import DockerInstanceManager

router = fastapi.APIRouter()


@router.get("/", response_model=list[models.InstanceRead])
async def get_instances(database: recraft.deps.DBSessionDep):
    return (await database.exec(sqlmodel.select(models.Instance))).all()


@router.post("/", response_model=models.InstanceRead)
async def post_instance(
    instance: models.InstanceCreate,
    database: recraft.deps.DBSessionDep,
    httpx_async_client: recraft.deps.HttpxAsyncClientDep,
    httpx_async_client_docker: recraft.deps.HttpxAsyncClientDockerDep,
    instance_managers: recraft.deps.InstanceManagersDep,
    configuration: recraft.deps.ConfigurationDep
):
    db_instance = models.Instance.model_validate(instance)
    database.add(db_instance)
    await database.commit()
    await database.refresh(db_instance)
    instance_managers[db_instance.id] = DockerInstanceManager(
        f"recraft_{db_instance.id}",
        configuration.shared_data_path,
        httpx_async_client,
        httpx_async_client_docker
    )
    return db_instance


@router.post("/{instance_id}/start", status_code=200)
async def start(instance_id: int, instance_managers: recraft.deps.InstanceManagersDep, database: recraft.deps.DBSessionDep):
    db_instance = await database.get(models.Instance, instance_id)
    assert db_instance is not None
    if db_instance.player_list_id is None:
        return
    db_memberships = await database.exec(sqlmodel.select(PlayerListPlayerLink).where(PlayerListPlayerLink.player_list_id == db_instance.player_list_id))
    allowlist = []
    for membership in db_memberships:
        if membership.access_permission == AccessPermission.ALLOWED:
            db_player = await database.get(Player, membership.player_id)
            assert db_player is not None
            allowlist.append(AllowlistPlayer(
                name=db_player.name, id=db_player.uuid))

    await instance_managers[instance_id].start(allowlist)


@router.post("/{instance_id}/stop", status_code=200)
async def stop(instance_id: int, instance_managers: recraft.deps.InstanceManagersDep):
    await instance_managers[instance_id].stop()


@router.post("/{instance_id}/provision", status_code=200)
async def provision(instance_id: int, instance_managers: recraft.deps.InstanceManagersDep):
    await instance_managers[instance_id].provision()
