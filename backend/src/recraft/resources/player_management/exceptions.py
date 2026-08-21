# Copyright 2026 dairiki-ren.
# SPDX-License-Identifier: GPL-3.0-only


import recraft.exceptions


class PlayerNotFoundError(recraft.exceptions.NotFoundError):
    message = "Player could not be found"


class PlayerListNotFoundError(recraft.exceptions.NotFoundError):
    message = "Player list could not be found"


class MembershipNotFoundError(recraft.exceptions.NotFoundError):
    message = "Membership could not be found"


class MinecraftProfileApiErrorParams(recraft.exceptions.ExternalApiErrorParams):
    pass


class MinecraftProfileApiError(recraft.exceptions.ExternalApiError):
    params_model = MinecraftProfileApiErrorParams


class MinecraftProfileApiTimeoutError(MinecraftProfileApiError):
    message = "Minecraft profile API timed out"


class MinecraftProfileApiNonSuccessError(MinecraftProfileApiError):
    message = "Minecraft profile API returned non-success status code"


class MinecraftProfileApiJsonDecodeError(MinecraftProfileApiError):
    message = "Minecraft profile API returned a JSON that could not be decoded"


class MinecraftProfileApiResponseValidationError(MinecraftProfileApiError):
    message = "Minecraft profile API returned data that could not be validated"
