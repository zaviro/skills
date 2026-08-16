# desktopctl Contract

`desktopctl` is a thin guardrail around official desktop interfaces.

It is **not** a declarative database and must not replace Nix/Home Manager.

## Stable command families

```text
desktopctl doctor

desktopctl inspect noctalia

desktopctl validate niri [config-path]
desktopctl validate noctalia [config-path]

desktopctl action niri <action> [args...]
desktopctl action noctalia <command> [args...]

desktopctl paths
```

Future additions may include structured state queries, but mutating persistent configuration belongs to `desktop-system`.

## Exit behavior

- `0`: success
- non-zero: command/validation failure
- preserve stdout/stderr from upstream tools where useful

## Security boundary

`desktopctl action` only dispatches to known desktop IPC executables.

Do not add a generic:

```text
desktopctl shell <arbitrary command>
```

That would erase the purpose of the guardrail.

## Discovery

Syntax changes across versions. For unfamiliar commands, inspect:

```sh
niri msg action
noctalia msg --help
```

rather than baking every possible action into `desktopctl`.
