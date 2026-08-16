#!/usr/bin/env python3
"""
Clipboard Query Tool - Advanced search and filtering for CopyQ clipboard history.
"""

import subprocess
import json
import argparse
import sys
from datetime import datetime


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


def search_clipboard(pattern: str, limit: int = 0, case_sensitive: bool = False) -> list:
    """Search clipboard entries matching pattern."""
    count = get_clipboard_count()
    if limit > 0:
        count = min(count, limit)
    
    results = []
    pattern_lower = pattern.lower() if not case_sensitive else pattern
    
    for i in range(count):
        text = get_entry(i)
        check_text = text if case_sensitive else text.lower()
        
        if pattern_lower in check_text:
            results.append({
                "index": i,
                "text": text,
                "preview": text[:200] + "..." if len(text) > 200 else text
            })
    
    return results


def list_entries(limit: int = 10) -> list:
    """List clipboard entries."""
    count = get_clipboard_count()
    limit = min(limit, count) if limit > 0 else count
    
    entries = []
    for i in range(limit):
        text = get_entry(i)
        entries.append({
            "index": i,
            "text": text,
            "preview": text[:100].replace("\n", " ") + ("..." if len(text) > 100 else "")
        })
    
    return entries


def main():
    parser = argparse.ArgumentParser(description="Query CopyQ clipboard history")
    parser.add_argument("--search", "-s", help="Search pattern")
    parser.add_argument("--limit", "-l", type=int, default=0, help="Limit results")
    parser.add_argument("--case-sensitive", "-c", action="store_true", help="Case sensitive search")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--list", action="store_true", help="List entries")
    parser.add_argument("--count", action="store_true", help="Show count only")
    parser.add_argument("--read", "-r", type=int, help="Read specific entry by index")
    
    args = parser.parse_args()
    
    if args.count:
        print(get_clipboard_count())
        return
    
    if args.read is not None:
        print(get_entry(args.read))
        return
    
    if args.search:
        results = search_clipboard(args.search, args.limit, args.case_sensitive)
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print(f"Found {len(results)} matches for '{args.search}':\n")
            for r in results:
                print(f"[{r['index']}] {r['preview']}\n")
        return
    
    if args.list or not any([args.search, args.count, args.read]):
        limit = args.limit if args.limit > 0 else 10
        entries = list_entries(limit)
        if args.json:
            print(json.dumps(entries, indent=2, ensure_ascii=False))
        else:
            total = get_clipboard_count()
            print(f"Clipboard History ({len(entries)} of {total} entries):\n")
            for e in entries:
                print(f"[{e['index']}] {e['preview']}")


if __name__ == "__main__":
    main()
