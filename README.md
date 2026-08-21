# recraft

Minecraft servers for you & your friends.

## Features

- Player management
    - Get online players via API
    - Allowlist/Banlist management
- Mod management
    - Automatically get mods with dependencies and install

## Concept

- Instances: Correspond to MC server instances
    - One container per instance, launched over Docker socket
        - Different container images that self-setup (e.g. Bedrock, Vanilla,
          Fabric, NeoForge...)
        - Manifests for instance profiles
            - Name
            - Description
            - Container Image
            - RPC Provider to use (Java/Bedrock)
    - Status & basic telemetry by JSON-RPC exposed by Minecraft server
        - 2 RPC providers: One for Java, one for Bedrock
- Resources: Parts that can be reused by multiple instances in RO mode
    - Modpacks
    - Whitelists/Banlists
    - Webhooks
        - Shouterr Destination
        - Events to notify for
    - Worlds
- Configuration: Recraft configuration
    - Users
    - 

## API

- /instances
- /instances/<id>
