---
name: clipboard-manager
description: Manage and query clipboard history using CopyQ. Export clipboard entries to Obsidian vault as markdown notes with timestamps. Extract English words from clipboard content using regex for vocabulary collection. Use when user asks to view clipboard history, search copied text, export clipboard to notes, or extract words from clipboard.
---

# Clipboard Manager

Query, export, and analyze clipboard history powered by CopyQ.

## Quick Commands

Use the `clipboard-history` CLI tool for common operations:

```bash
# List recent entries
clipboard-history list [N]        # Show last N entries (default: 10)

# Search clipboard
clipboard-history search "keyword"

# Export to file
clipboard-history export ~/backup.txt

# JSON output (for programmatic use)
clipboard-history json [N]

# Status check
clipboard-history status
```

## Core Capabilities

### 1. Query Clipboard History

To view clipboard entries:

```bash
# Latest entry
copyq read 0

# Specific entry by index
copyq read 5

# Count total entries
copyq count

# List with preview
clipboard-history list 20
```

### 2. Search Clipboard Content

To find specific content:

```bash
clipboard-history search "keyword"
```

Or use the script for advanced search:

```bash
python3 scripts/clipboard_query.py --search "pattern" --limit 50
```

### 3. Export to Obsidian

To export clipboard entries to Obsidian vault:

```bash
python3 scripts/export_to_obsidian.py [options]
```

Options:
- `--vault PATH`: Obsidian vault path (default: ~/Documents/Obsidian)
- `--limit N`: Number of entries to export (default: all)
- `--search KEYWORD`: Only export matching entries
- `--folder NAME`: Subfolder in vault (default: Clipboard)

Example:
```bash
# Export all clipboard to Obsidian
python3 scripts/export_to_obsidian.py --vault ~/Documents/Obsidian

# Export last 10 entries containing "important"
python3 scripts/export_to_obsidian.py --search "important" --limit 10
```

### 4. Extract English Words

To extract English words from clipboard content for vocabulary building:

```bash
python3 scripts/extract_english_words.py [options]
```

Options:
- `--limit N`: Process last N clipboard entries (default: all)
- `--min-length N`: Minimum word length (default: 3)
- `--output FILE`: Save to file (default: stdout)
- `--unique`: Only unique words
- `--sort`: Sort alphabetically

Example:
```bash
# Extract unique words from all clipboard, min 4 chars
python3 scripts/extract_english_words.py --unique --min-length 4 --sort

# Save vocabulary to file
python3 scripts/extract_english_words.py --unique --output ~/vocabulary.txt
```

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `clipboard_query.py` | Advanced clipboard search and filtering |
| `export_to_obsidian.py` | Export entries to Obsidian markdown notes |
| `extract_english_words.py` | Regex extract English words |

## CopyQ Direct Commands

For advanced usage, use CopyQ's scripting API directly:

```bash
# Evaluate JavaScript
copyq eval "for(i=0; i<size(); i++) print(str(read(i)) + '\n')"

# Get with format
copyq clipboard text/plain

# Add entry
copyq add "text to add"
```

See `references/copyq-scripting.md` for complete CopyQ API reference.
