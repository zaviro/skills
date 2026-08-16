# CopyQ Scripting Reference

## Basic Commands

```bash
copyq count                    # Total entries
copyq read N                   # Read entry at index N
copyq clipboard                # Current clipboard content
copyq add "text"               # Add new entry
copyq remove N                 # Remove entry at index N
```

## JavaScript Eval

```bash
copyq eval "size()"
copyq eval "str(read(0))"
copyq eval "for(i=0; i<size(); i++) print(str(read(i)) + '\n')"
```

## Common Functions

| Function | Description |
|----------|-------------|
| `size()` | Number of items |
| `read(row)` | Get item data |
| `str(data)` | Convert to string |
| `add(text)` | Add item |
| `remove(row)` | Remove item |
| `select(row)` | Copy item to clipboard |

## MIME Types

- `text/plain` - Plain text
- `text/html` - HTML content
- `mimeText` - Alias for text/plain
