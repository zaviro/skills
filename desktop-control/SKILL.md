---
name: desktop-control
description: Operate the current Linux desktop session without changing its long-term declarative configuration. Use for immediate actions such as switching workspaces, controlling windows, volume, brightness, media, wallpaper, Noctalia panels, and other runtime-only desktop operations.
---

# Desktop Control

Operate the **current desktop session**. Do not change the user's long-term desired configuration.

## Boundary

Use this skill when the request means **"do this now"**:

- switch/focus/move a workspace or window
- change volume, brightness, media playback
- set or change the current wallpaper
- open/close/toggle a Noctalia surface
- invoke a Niri action
- temporarily toggle a runtime feature
- inspect current desktop state

Do **not** use this skill when the request means:

- "always", "by default", "after reboot", "persist", "save this"
- install/remove a package or service
- add a new desktop capability
- change NixOS/Home Manager/Niri/Noctalia declarative configuration
- iterate on a configuration until it becomes the new default

Those belong to `desktop-system`.

## Core rule

**Runtime state is not declarative state.**

Never edit Home Manager/NixOS-generated files to perform a runtime action.

Prefer official IPC and CLI interfaces in this order:

1. compositor/shell IPC
2. service CLI
3. narrowly scoped system command
4. GUI automation only if no programmatic interface exists

Never use arbitrary shell mutation when an official IPC exists.

## Niri

Prefer:

```sh
niri msg action <action> [args...]
```

Every bindable Niri action is intended to be invokable through `niri msg action`.

Examples:

```sh
niri msg action focus-workspace 3
niri msg action focus-column-right
niri msg action close-window
```

Before using an unfamiliar action:

```sh
niri msg action
```

and inspect the current installed version's help instead of guessing syntax.

## Noctalia

Prefer:

```sh
noctalia msg <command> [args...]
```

Discover commands from the installed version:

```sh
noctalia msg --help
```

Examples include panel toggles, wallpaper/theme actions, volume, brightness, media, screenshots and session controls.

Do not edit Noctalia TOML for an operation that is already available through IPC.

## Bundled helper

When available, prefer the `desktopctl` wrapper:

```sh
desktopctl doctor
desktopctl action niri ...
desktopctl action noctalia ...
desktopctl inspect noctalia
```

`desktopctl` is a guardrail and discovery layer, not the source of truth.

This Skill owns the helper implementation and its supporting material:

```text
scripts/desktopctl.ts
references/desktopctl-contract.md
examples/home-manager.nix
```

Read `references/desktopctl-contract.md` before extending the helper. The Home Manager example shows one way to expose both the CLI and Skills declaratively.

## Safety

Before destructive runtime actions:

- identify the exact target window/output/workspace
- avoid broad process killing unless explicitly required
- do not alter system configuration
- do not persist a temporary experiment

If the user says the current result should become permanent, hand off to `desktop-system`.
