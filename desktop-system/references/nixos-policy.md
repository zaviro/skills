# NixOS / Home Manager Policy

## Principle

The declarative repository is the durable source of truth.

Runtime and generated locations are observations or temporary state, not durable configuration.

## Before editing

Resolve the owner of the relevant state.

Check:

```sh
readlink -f <path>
stat <path>
rg -n '<setting-or-filename>' <nix-repo>
```

If a generated file resolves into `/nix/store`, do not edit the store path.

If Home Manager uses an out-of-store symlink, edit the source path that owns it.

## Activation

Do not invent an activation command.

Inspect the repository for:

- README/AGENTS instructions
- `justfile`
- scripts
- flake apps
- host modules
- Home Manager commands
- CI checks

Use the project's established path.

## Iteration

Declarative iteration is acceptable and often preferable on NixOS:

```text
edit source → validate → activate → observe → edit again
```

A runtime preview layer is optional, not mandatory.

Use a runtime preview only when:

- it is clearly reversible
- it does not overwrite unrelated runtime state
- its provenance is obvious
- it can be removed after promotion

## Overrides

Noctalia's app-managed settings can override curated TOML. Treat them as runtime/app state.

Niri optional includes can provide a clean temporary preview layer, but must not become permanent shadow configuration.

## VCS

Preserve unrelated work.

If using Jujutsu:

- inspect `jj status` and `jj diff`
- isolate a non-trivial experiment in its own change when useful
- do not squash/commit/push unless the user asks or repository workflow requires it

If using Git, follow the equivalent discipline.

## Capability modules

Prefer one module per meaningful feature when the feature has several resources.

Example:

```text
desktop/
├── niri.nix
├── noctalia.nix
└── capabilities/
    └── dynamic-wallpaper.nix
```

Do not create a capability module for every single scalar setting.
