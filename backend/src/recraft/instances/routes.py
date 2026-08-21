# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import fastapi
import sqlmodel

import recraft.deps

from . import models

router = fastapi.APIRouter()


@router.get("/", response_model=list[models.InstanceRead])
async def get_instances(database: recraft.deps.DBSessionDep):
    return (await database.exec(sqlmodel.select(models.Instance))).all()


@router.post("/", response_model=models.InstanceRead)
async def post_instance(instance: models.InstanceCreate, database: recraft.deps.DBSessionDep):
    db_instance = models.Instance.model_validate(instance)
    database.add(db_instance)
    await database.commit()
    return db_instance
