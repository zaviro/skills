---
name: obsidian-guide
description: Manage Obsidian vaults and markdown notes on disk. Use when the user wants the agent to create/update/search Obsidian notes, organize vault structure, add frontmatter/tags/links, export content to Obsidian, or open the Obsidian app. Prefer file-based operations; launch GUI only when requested.
---

# Obsidian Guide

Operate Obsidian as a file-based markdown vault.

## Agent Operating Rules

- Use file tools to create/update notes (Write/Edit/Read).
- Use Glob to list notes and folders.
- Use Grep to search note content.
- Create missing directories as needed.
- Return paths of files created or updated.
- Do not install Obsidian unless explicitly requested; assume snap install for launch.

## Defaults

- Vault path: `~/Documents/Obsidian`
- Notes are `.md` files
- Links use `[[note-name]]` syntax

## Workflow: Create or Update a Note

1. Determine vault path (user-specified or default).
2. Choose target folder; create if missing.
3. Choose filename (kebab-case or title-case; avoid special characters).
4. Build frontmatter if needed:
   ```yaml
   ---
   created: 2026-01-26 22:00
   tags:
     - tag1
     - tag2
   ---
   ```
5. Write note body with a top-level title and content.
6. Return the final file path.

Example (programmatic write):
```python
from pathlib import Path
from datetime import datetime

vault = Path.home() / "Documents/Obsidian"

def write_note(title: str, content: str, folder: str = ""):
    target = vault / folder / f"{title}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    frontmatter = f"""---\ncreated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n---\n\n"""
    target.write_text(frontmatter + f"# {title}\n\n" + content, encoding="utf-8")
    return target
```

## Workflow: Link Notes

- Create links with `[[note-name]]`.
- Ensure the linked file exists or create a stub.
- For headings: `[[note-name#Heading]]`.
- For display alias: `[[note-name|Alias]]`.
- For embeds: `![[note-name]]`.

## Workflow: Search Notes

Use the Grep tool with `path=~/Documents/Obsidian` and `include="*.md"`.
Return matching file paths and short excerpts.

## Workflow: Export Content to Obsidian

When the user asks to export clipboard history:
```bash
python3 ~/.codex/skills/clipboard-manager/scripts/export_to_obsidian.py --vault ~/Documents/Obsidian
```

## Launch Obsidian (when requested)

```bash
obsidian
# If PATH is missing snap bin:
/snap/bin/obsidian
```

## References

- `references/vault-structure.md` - Folder organization patterns
- `references/markdown-syntax.md` - Markdown and Obsidian syntax
- `references/plugins.md` - Recommended plugins and settings locations
