# Desktop Agent Skills

This bundle implements the split architecture:

```text
desktop-control  → immediate runtime actions
desktop-system   → declarative configuration/capabilities/iteration
                       │
                       └── both may use desktopctl
```

## Files

```text
desktop-control/SKILL.md
desktop-system/SKILL.md
desktop-system/references/nixos-policy.md
desktop-system/references/capabilities/dynamic-wallpaper.md
shared/desktopctl-contract.md
bin/desktopctl.ts
nix/home-manager-example.nix
```

## Why this boundary

`desktop-control` is intentionally low-risk and runtime-only.

`desktop-system` owns persistent NixOS/Home Manager changes, including both scalar configuration changes and larger capability additions. It treats runtime experiments as temporary and promotes only the final desired state into the declarative repository.

`desktopctl` stays small. It wraps official Niri/Noctalia commands for discovery, validation and immediate actions. It does not try to parse/rewrite arbitrary Nix source.

## Initial desktopctl commands

```sh
desktopctl doctor
desktopctl inspect noctalia
desktopctl validate niri
desktopctl validate noctalia
desktopctl action niri focus-workspace 3
desktopctl action noctalia panel-toggle launcher
desktopctl paths
```

Before relying on an unfamiliar Niri/Noctalia action, inspect the installed tool's own help because IPC commands can evolve.

## Dynamic wallpaper

The first capability recipe is:

```text
desktop-system/references/capabilities/dynamic-wallpaper.md
```

It is intentionally modeled as a capability rather than a Boolean setting, so future features can bring packages, services, shell integration, validation and removal logic without changing the Skill architecture.
