#!/usr/bin/env python3
"""
Export CopyQ clipboard history to Obsidian vault as markdown notes.
"""

import subprocess
import argparse
import sys
import os
from datetime import datetime
from pathlib import Path


def run_copyq(cmd: str) -> str:
    """Execute a CopyQ command and return output."""
    try:
        result = subprocess.run(
            ["copyq", "eval", cmd],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        print("Error: CopyQ command timed out", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: CopyQ not found. Install with: sudo apt install copyq", file=sys.stderr)
        sys.exit(1)


def get_clipboard_count() -> int:
    """Get total number of clipboard entries."""
    return int(run_copyq("size()") or "0")


def get_entry(index: int) -> str:
    """Get clipboard entry by index."""
    return run_copyq(f"str(read({index}))")


def sanitize_filename(text: str, max_length: int = 50) -> str:
    first_line = text.split('\n')[0][:max_length]
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        first_line = first_line.replace(char, '')
    first_line = first_line.strip()
    if not first_line:
        first_line = "clipboard-entry"
    return first_line


def export_to_obsidian(
    vault_path: str,
    folder: str = "Clipboard",
    limit: int = 0,
    search: str | None = None,
    single_file: bool = False
) -> None:
    """Export clipboard entries to Obsidian vault."""
    vault = Path(vault_path).expanduser()
    if not vault.exists():
        print(f"Creating vault directory: {vault}")
        vault.mkdir(parents=True)
    
    target_dir = vault / folder
    target_dir.mkdir(parents=True, exist_ok=True)
    
    count = get_clipboard_count()
    if limit > 0:
        count = min(count, limit)
    
    entries = []
    for i in range(count):
        text = get_entry(i)
        if search and search.lower() not in text.lower():
            continue
        entries.append((i, text))
    
    if not entries:
        print("No matching entries found.")
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    if single_file:
        filename = f"clipboard-export-{timestamp}.md"
        filepath = target_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Clipboard Export\n\n")
            f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total entries: {len(entries)}\n\n")
            f.write("---\n\n")
            
            for idx, text in entries:
                f.write(f"## Entry {idx}\n\n")
                f.write(f"```\n{text}\n```\n\n")
                f.write("---\n\n")
        
        print(f"Exported {len(entries)} entries to: {filepath}")
    else:
        exported = 0
        for idx, text in entries:
            safe_name = sanitize_filename(text)
            filename = f"{timestamp}-{idx:03d}-{safe_name}.md"
            filepath = target_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("---\n")
                f.write(f"created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"source: clipboard\n")
                f.write(f"index: {idx}\n")
                f.write("tags:\n  - clipboard\n")
                f.write("---\n\n")
                f.write(f"# {safe_name}\n\n")
                f.write(text)
                f.write("\n")
            
            exported += 1
        
        print(f"Exported {exported} entries to: {target_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Export CopyQ clipboard history to Obsidian vault"
    )
    parser.add_argument(
        "--vault", "-v",
        default="~/Documents/Obsidian",
        help="Path to Obsidian vault (default: ~/Documents/Obsidian)"
    )
    parser.add_argument(
        "--folder", "-f",
        default="Clipboard",
        help="Folder within vault (default: Clipboard)"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=0,
        help="Limit number of entries (0 = all)"
    )
    parser.add_argument(
        "--search", "-s",
        help="Only export entries matching search term"
    )
    parser.add_argument(
        "--single-file",
        action="store_true",
        help="Export all to single file instead of separate notes"
    )
    
    args = parser.parse_args()
    
    export_to_obsidian(
        vault_path=args.vault,
        folder=args.folder,
        limit=args.limit,
        search=args.search,
        single_file=args.single_file
    )


if __name__ == "__main__":
    main()
