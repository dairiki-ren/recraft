# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import sqlalchemy
import sqlalchemy.ext.asyncio
import sqlmodel

import recraft.config

sqlite_url = f"sqlite+aiosqlite:///{recraft.config.configuration.sqlite_path}"

async_engine = sqlalchemy.ext.asyncio.create_async_engine(sqlite_url)


async def init_database():
    async with async_engine.connect() as connection:
        await connection.run_sync(sqlmodel.SQLModel.metadata.create_all)
        await connection.execute(sqlalchemy.text("PRAGMA foreign_keys = ON;"))
