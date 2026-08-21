# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only

import fastapi

import recraft.resources.player_management.routes

router = fastapi.APIRouter()
router.include_router(
    recraft.resources.player_management.routes.router, prefix="/player-management"
)
