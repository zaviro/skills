#!/usr/bin/env python3
"""
Extract English words from CopyQ clipboard history using regex.
Useful for vocabulary building and word collection.
"""

import subprocess
import argparse
import re
import sys
from collections import Counter
from typing import List, Set, Union


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


def extract_words(text: str, min_length: int = 3) -> List[str]:
    pattern = r'\b[a-zA-Z]+\b'
    words = re.findall(pattern, text)
    return [w.lower() for w in words if len(w) >= min_length]


def extract_from_clipboard(
    limit: int = 0,
    min_length: int = 3,
    unique: bool = False,
    with_count: bool = False
) -> Union[List[str], list]:
    count = get_clipboard_count()
    if limit > 0:
        count = min(count, limit)
    
    all_words = []
    
    for i in range(count):
        text = get_entry(i)
        words = extract_words(text, min_length)
        all_words.extend(words)
    
    if with_count:
        counter = Counter(all_words)
        return counter.most_common()
    
    if unique:
        return list(sorted(set(all_words)))
    
    return all_words


def main():
    parser = argparse.ArgumentParser(
        description="Extract English words from CopyQ clipboard history"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=0,
        help="Process last N entries (0 = all)"
    )
    parser.add_argument(
        "--min-length", "-m",
        type=int,
        default=3,
        help="Minimum word length (default: 3)"
    )
    parser.add_argument(
        "--unique", "-u",
        action="store_true",
        help="Only output unique words"
    )
    parser.add_argument(
        "--sort", "-s",
        action="store_true",
        help="Sort words alphabetically"
    )
    parser.add_argument(
        "--count", "-c",
        action="store_true",
        help="Show word frequency count"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--format",
        choices=["plain", "json", "csv"],
        default="plain",
        help="Output format"
    )
    
    args = parser.parse_args()
    
    if args.count:
        results = extract_from_clipboard(
            limit=args.limit,
            min_length=args.min_length,
            with_count=True
        )
        
        output_lines = []
        if args.format == "json":
            import json
            output = json.dumps([{"word": w, "count": c} for w, c in results], indent=2)
            output_lines = [output]
        elif args.format == "csv":
            output_lines = ["word,count"] + [f"{w},{c}" for w, c in results]
        else:
            output_lines = [f"{w}: {c}" for w, c in results]
    else:
        words = extract_from_clipboard(
            limit=args.limit,
            min_length=args.min_length,
            unique=args.unique
        )
        
        if args.sort:
            words = sorted(words)
        
        if args.format == "json":
            import json
            output_lines = [json.dumps(words, indent=2)]
        elif args.format == "csv":
            output_lines = ["word"] + words
        else:
            output_lines = words
    
    output_text = "\n".join(str(line) for line in output_lines)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_text)
            f.write("\n")
        print(f"Saved to: {args.output}")
        if not args.count:
            word_count = len(output_lines) if args.format != 'json' else len(output_lines)
            print(f"Total words: {word_count}")
    else:
        print(output_text)
        if not args.count and args.format == "plain":
            print(f"\n--- Total: {len(output_lines)} words ---")


if __name__ == "__main__":
    main()
