# Agent Skills

Personal monorepo for reusable Agent Skills. Every active Skill is a first-class directory at the repository root, regardless of whether it is authored locally, mirrored from upstream, or locally patched.

## Layout

```text
<skill-name>/
├── SKILL.md
├── scripts/       # optional; owned by this Skill
├── references/    # optional; owned by this Skill
├── assets/        # optional; owned by this Skill
└── examples/      # optional; owned by this Skill

disabled/          # inactive Skills kept for reference
sources.lock.json  # provenance/update policy for external Skills
README.md
```

Repository-level directories should contain only genuinely cross-Skill infrastructure. A script, reference, example, or integration used by one Skill belongs inside that Skill.

## Active Skills

- `browser-use`
- `clipboard-manager`
- `desktop-control`
- `desktop-system`
- `doc-bilingual-translator`
- `document-processor`
- `find-skills`
- `integrate-remote-handoffs`
- `notebooklm-docs`
- `proton-game-helper`
- `remote-handoff`
- `roadmap-parser`
- `skill-creator`
- `tavily-search`
- `updating-plugin-model`
- `webdoc-structure-processor`

## Source and update policy

`sources.lock.json` records provenance only for Skills with an external update source:

- `mirror`: local Skill should match the recorded upstream Skill.
- `patched`: upstream is the base, with explicitly retained local overlays.
- `registry`: version is managed by an external Skill registry.

Locally authored Skills do not need synthetic upstream entries; Git history is their source of truth.

## Desktop Skills

The desktop capability is split intentionally:

```text
desktop-control  → immediate runtime actions
desktop-system   → persistent declarative NixOS/Home Manager state
```

`desktop-control` owns the `desktopctl` implementation and its documentation/examples. `desktop-system` may use the installed `desktopctl` command, but persistent configuration remains owned by the user's declarative Nix source.
