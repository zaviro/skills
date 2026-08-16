---
name: desktop-system
description: Design, add, remove, debug, and iteratively refine declarative Linux desktop configuration and capabilities on NixOS/Home Manager, including Niri and Noctalia. Use when changes must persist, when adding new desktop functionality, or when promoting a successful runtime experiment into the declarative source of truth.
---

# Desktop System

Manage the desktop as a **declarative system**, not as a pile of generated dotfiles.

Read `references/nixos-policy.md` before making persistent changes.
For capability additions, check `references/capabilities/` for an existing recipe.

## Scope

Use this skill for:

- persistent Niri or Noctalia changes
- desktop appearance iteration
- new packages, services, modules, hooks, templates or plugins
- new capabilities such as dynamic wallpaper, screen translation, theme sync, idle/lock behavior
- debugging why declared state differs from runtime state
- promoting a successful temporary experiment into Nix/Home Manager
- removing or replacing an existing desktop capability

Configuration modification and configuration iteration belong to this **same skill**.

Use `desktop-control` for runtime-only actions.

## Mental model

Treat requests as one of four objects:

### Property

A value inside an existing capability.

Examples:

- Niri gaps
- Noctalia theme mode
- bar thickness
- animation duration

### Resource

A concrete dependency.

Examples:

- package
- systemd user service
- config file
- directory
- template
- plugin

### Capability

A user-visible feature composed of one or more resources.

Examples:

- dynamic wallpaper
- Material You Fcitx theme
- screen translation
- clipboard history
- desktop AI
- idle lock

### Action

An immediate runtime operation.

Actions should normally be delegated to `desktop-control`.

## Source-of-truth rule

For persistent state:

> **NixOS/Home Manager source is authoritative. Generated files are outputs.**

Never permanently edit:

```text
~/.config/niri/config.kdl
~/.config/noctalia/*.toml
```

without first determining whether they are generated or linked from declarative source.

Resolve provenance before mutation.

Useful checks:

```sh
readlink -f ~/.config/niri/config.kdl
readlink -f ~/.config/noctalia/config.toml
stat ~/.config/niri/config.kdl
```

Also inspect the Nix repository and search for the setting/module that owns the file.

If the source is managed by Nix/Home Manager, modify that source.

If the source is genuinely hand-maintained outside Nix, state that explicitly before editing it.

## Workflow

### 1. Inspect

Determine:

- current runtime state
- effective Niri/Noctalia configuration
- declarative owner/provenance
- existing packages/services/modules
- activation/check commands already used by the repository
- version-control state

Prefer:

```sh
desktopctl doctor
desktopctl inspect noctalia
niri validate
noctalia config export full
```

Do not guess repository structure or activation commands when they can be discovered.

### 2. Classify

Decide whether the request is:

```text
property / resource / capability
```

For a capability, enumerate its resources and integrations before editing.

Example:

```text
dynamic-wallpaper
├── package: mpvpaper
├── package: mpv
├── optional package: ffmpeg
├── Noctalia integration/plugin
├── wallpaper directory
├── optional theme-frame extraction
└── optional pause policy
```

### 3. Plan the smallest coherent change

Prefer extending existing modules over introducing a parallel configuration system.

A capability should have:

- one clear owner module
- explicit dependencies
- an enable/disable boundary where practical
- validation
- removal path
- no hidden mutable state required for normal operation

Avoid creating generic abstractions before a second real use case needs them.

### 4. Establish a rollback point

Before a non-trivial persistent change:

- inspect the current VCS diff
- preserve unrelated changes
- create/use an isolated change/workspace when appropriate
- never overwrite unrelated user work

Do not commit/push unless asked.

### 5. Implement declaratively

Modify the real Nix/Home Manager source.

Prefer Nix-native resources:

- `home.packages`
- Home Manager modules/options
- `systemd.user.services`
- declaratively managed config files
- explicit hooks/templates
- package paths rather than ambient PATH assumptions where practical

Do not solve a persistent NixOS requirement with an imperative installer script unless no declarative option exists.

### 6. Validate before activation

For Niri:

```sh
niri validate
```

For an alternate candidate config, use the installed `niri validate` help/options rather than guessing.

For Noctalia:

```sh
noctalia config validate
```

or validate a generated TOML file directly:

```sh
noctalia config validate ./candidate.toml
```

Then run the repository's existing Nix checks/formatters/tests.

Examples may include `nix flake check`, `nix eval`, `just`, `nh`, or a project-specific verification command, but discover the repository's convention first.

### 7. Activate

Use the repository's established Home Manager/NixOS activation path.

After activation, verify the **runtime effect**, not merely command success.

### 8. Iterate

If appearance/behavior needs tuning:

```text
inspect
→ edit declarative source
→ validate
→ activate
→ observe
→ adjust
```

Use a safe runtime preview only when the target component exposes an explicit reversible runtime layer.

Do not create a second long-lived configuration source merely to make iteration easier.

### 9. Promote / finalize

If a runtime experiment was used, transfer only the desired final values/resources into declarative source and remove temporary overrides.

Check:

- runtime matches declaration
- no stale override shadows the declaration
- generated files were not accidentally committed
- new capability has a clear removal path

## Noctalia-specific policy

Noctalia has two configuration layers:

1. curated config under the config directory
2. app-managed runtime/settings overrides under the state directory

On NixOS, treat the curated config as the long-term declarative layer.

`settings.toml` may shadow declarative values. Inspect it when the runtime result disagrees with source, but do not silently turn it into the new source of truth.

Useful inspection:

```sh
noctalia config export
noctalia config export full
noctalia config validate
```

Prefer official `noctalia msg ...` IPC for runtime actions.

## Niri-specific policy

Niri supports live reload and top-level `include`.

An optional runtime include may be used for deliberately temporary experiments, for example:

```kdl
include optional=true "~/.local/state/desktop-agent/niri-preview.kdl"
```

Keep such a preview file outside the declarative config and ensure it is cleared after promotion.

Do not use a preview include as a permanent second configuration layer.

## Capability contract

Every new capability should answer:

1. What user-visible behavior does it provide?
2. Which packages/resources does it require?
3. Which compositor/shell integrations does it require?
4. What is persistent vs runtime state?
5. How is it validated?
6. How is it disabled/removed?
7. Does it introduce a daemon or continuous resource cost?
8. Does it send data to an external service?
9. Can it be reused with a different shell/compositor later?

If a capability has a recipe in `references/capabilities/`, use it as guidance, not as an unquestionable template.

## Shared helper

`desktopctl` should remain intentionally small.

It may:

- discover installed desktop tools
- invoke official IPC
- export effective config
- run validators
- expose runtime state paths

It should **not** become a second declarative configuration database and should not attempt to rewrite arbitrary Nix ASTs.

The Agent is responsible for understanding and editing the user's actual declarative repository.
