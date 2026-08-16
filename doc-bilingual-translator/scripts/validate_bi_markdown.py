# Copyright (c) 2026. This implementation is inspired by the "Pangu Spacing" standard
# (originally specified in vinta's pangu.js under the MIT License) to improve readability
# of CJK and Latin mixed typography.
# 
# Pangu Spacing rules: Adds a space between CJK (Chinese, Japanese, Korean) and half-width
# English letters, numbers, or symbols.

import re
import sys
import os
import json
import argparse

# Common TypeScript reserved words that should not be translated to Chinese
RESERVED_WORDS = {
    "string": ["字符串"],
    "number": ["数字"],
    "boolean": ["布尔", "布尔值"],
    "any": ["任意", "任意类型"],
    "never": ["从不", "绝不"],
    "void": ["空", "无效"],
    "unknown": ["未知", "未知类型"],
    "typeof": ["类型为", "的类型"],
    "instanceof": ["实例为", "的实例"],
    "strictNullChecks": ["严格空检查"],
    "noImplicitAny": ["无隐式任意"]
}

def check_spacing(text):
    # Isolate Markdown syntax markers and HTML tags to prevent corruption
    # (e.g. inline code, links, bolds, italics, html structures)
    pattern_isolate = re.compile(
        r'('
        r'```[\s\S]*?```'             # Fenced code blocks
        r'|`[^`\n]+`'                 # Inline code
        r'|!?\[[^\]\n]*\]\([^\)\n]+\)' # Markdown links / images
        r'|<\/?[a-zA-Z0-9_#-]+(?:\s+[^>\n]*)?>' # HTML tags
        r'|\*\*[^\*\n]+\*\*'          # Markdown Bold
        r'|__[^\_\n]+__'              # Markdown Bold (underscores)
        r'|\*[^\*\n]+\*'              # Markdown Italic
        r'|_[^\_\n]+_'                # Markdown Italic (underscores)
        r')'
    )
    
    placeholders = []
    
    def isolate_match(match):
        val = match.group(0)
        placeholders.append(val)
        return f"{{===MD_PLACEHOLDER_{len(placeholders) - 1}===}}"
        
    isolated_text = pattern_isolate.sub(isolate_match, text)
    
    corrections = 0
    
    # 1. Chinese followed by English/Number/Placeholder-start
    # '{' matches the beginning of our placeholder '{===MD_PLACEHOLDER_...'
    pattern1 = re.compile(r'([\u4e00-\u9fa5])([a-zA-Z0-9{])')
    def repl1(match):
        nonlocal corrections
        corrections += 1
        return f"{match.group(1)} {match.group(2)}"
    
    # 2. English/Number/Placeholder-end followed by Chinese
    # '}' matches the ending of our placeholder '===}'
    pattern2 = re.compile(r'([a-zA-Z0-9}])([\u4e00-\u9fa5])')
    def repl2(match):
        nonlocal corrections
        corrections += 1
        return f"{match.group(1)} {match.group(2)}"

    # Perform replacements
    fixed_text = pattern1.sub(repl1, isolated_text)
    fixed_text = pattern2.sub(repl2, fixed_text)
    
    # Remove any accidental double spaces created
    fixed_text = re.sub(r' +', ' ', fixed_text)
    
    # Reconstruct the original Markdown/HTML markers from placeholders
    for idx, original_val in enumerate(placeholders):
        placeholder_str = f"{{===MD_PLACEHOLDER_{idx}===}}"
        fixed_text = fixed_text.replace(placeholder_str, original_val)
        
    return fixed_text, corrections

def validate_block(en_text, zh_text, block_index, fix=False, glossary=None):
    errors = []
    warnings = []
    fixed_zh = zh_text

    # 1. Spacing Validation & Auto-fix
    new_zh, space_issues = check_spacing(fixed_zh)
    if space_issues > 0:
        if fix:
            fixed_zh = new_zh
            warnings.append(f"Auto-fixed {space_issues} missing spaces between Chinese and English/Numbers.")
        else:
            errors.append(f"Detected {space_issues} locations missing spaces between Chinese and English/Numbers.")

    # 2. Markdown Syntax Symmetrical Verification
    # Check backticks count
    en_backticks = en_text.count('`')
    zh_backticks = fixed_zh.count('`')
    if en_backticks != zh_backticks:
        errors.append(f"Backtick (`) mismatch: English has {en_backticks}, Chinese has {zh_backticks}.")

    # Check bold markers count
    en_bolds = en_text.count('**')
    zh_bolds = fixed_zh.count('**')
    if en_bolds != zh_bolds:
        errors.append(f"Bold marker (**) mismatch: English has {en_bolds}, Chinese has {zh_bolds}.")

    # Check Markdown Links count and URLs
    en_links = re.findall(r'\[(.*?)\]\((.*?)\)', en_text)
    zh_links = re.findall(r'\[(.*?)\]\((.*?)\)', fixed_zh)
    if len(en_links) != len(zh_links):
        errors.append(f"Link count mismatch: English has {len(en_links)}, Chinese has {len(zh_links)}.")
    else:
        # Check if URL part is identical
        for i, (en_l, zh_l) in enumerate(zip(en_links, zh_links)):
            if en_l[1] != zh_l[1]:
                errors.append(f"Link URL mismatch at link #{i+1}: English has '{en_l[1]}', Chinese has '{zh_l[1]}'. URL must not be translated or edited.")

    # 3. Reserved Word Check (Warning only)
    for word, translations in RESERVED_WORDS.items():
        if re.search(r'\b' + re.escape(word) + r'\b', en_text, re.IGNORECASE):
            for trans in translations:
                if trans in fixed_zh:
                    warnings.append(f"Technical keyword '{word}' might be incorrectly translated to '{trans}' in Chinese text. Consider keeping it as '{word}'.")

    # 4. Dynamic Glossary Consistency Check
    if glossary:
        for en_word, zh_trans in glossary.items():
            pattern = r'\b' + re.escape(en_word) + r'\b' if en_word.isalnum() else re.escape(en_word)
            if re.search(pattern, en_text, re.IGNORECASE):
                # Verify that the designated Chinese translation or original term exists in the translated string
                if zh_trans not in fixed_zh and en_word not in fixed_zh:
                    warnings.append(f"Glossary mismatch: English contains '{en_word}', but Chinese translation contains neither '{zh_trans}' nor '{en_word}'.")

    # 5. Red Span (Escape Valve) Check
    # Detect <span style="color:red">...</span> or <span style="color: red">...</span>
    red_spans = re.findall(r'<span style="color:\s*red;?">(.*?)</span>', fixed_zh, re.IGNORECASE)
    for span in red_spans:
        warnings.append(f"Detected escape valve (uncertain term marked in red): '{span}'.")

    return errors, warnings, fixed_zh

def validate_file(filepath, fix=False, glossary_path=None):
    glossary = None
    if glossary_path and os.path.exists(glossary_path):
        try:
            with open(glossary_path, 'r', encoding='utf-8') as gf:
                data = json.load(gf)
                if isinstance(data, dict):
                    if "terms" in data and isinstance(data["terms"], list):
                        glossary = {t["en"]: t["zh"] for t in data["terms"] if "en" in t and "zh" in t}
                    else:
                        glossary = data
                elif isinstance(data, list):
                    glossary = {t["en"]: t["zh"] for t in data if isinstance(t, dict) and "en" in t and "zh" in t}
            print(f"Loaded glossary with {len(glossary)} terms for validation.")
        except Exception as e:
            print(f"Warning: Failed to load glossary file from {glossary_path}: {e}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into blocks
    parts = []
    lines = content.split('\n')
    
    in_block = False
    current_block = []
    
    new_lines = []
    
    i = 0
    block_index = 0
    total_errors = 0
    total_warnings = 0
    
    while i < len(lines):
        line = lines[i]
        
        if line.strip() == ':::block':
            in_block = True
            current_block = []
            new_lines.append(line)
            i += 1
            continue
            
        if line.strip() == ':::':
            if in_block:
                block_index += 1
                block_content = "\n".join(current_block)
                en_match = re.search(r'\[en\]\n(.*?)(?=\n\[zh\]|\Z)', block_content, re.DOTALL)
                zh_match = re.search(r'\[zh\]\n(.*)', block_content, re.DOTALL)
                
                if en_match and zh_match:
                    en_text = en_match.group(1)
                    zh_text = zh_match.group(1)
                    
                    errors, warnings, fixed_zh = validate_block(en_text, zh_text, block_index, fix, glossary)
                    
                    if errors or warnings:
                        print(f"\n[Block #{block_index}]")
                        print(f"  English: {en_text[:80].strip()}...")
                        for err in errors:
                            print(f"  \033[91m[ERROR]\033[0m {err}")
                            total_errors += 1
                        for warn in warnings:
                            print(f"  \033[93m[WARNING]\033[0m {warn}")
                            total_warnings += 1
                    
                    # Reconstruction
                    new_lines.append("[en]")
                    new_lines.append(en_text)
                    new_lines.append("[zh]")
                    new_lines.append(fixed_zh)
                else:
                    print(f"\n[Block #{block_index}] \033[91m[ERROR] Failed to parse [en]/[zh] inside block.\033[0m")
                    total_errors += 1
                    new_lines.extend(current_block)
                
                new_lines.append(line)
                in_block = False
            else:
                new_lines.append(line)
            i += 1
            continue
            
        if in_block:
            current_block.append(line)
        else:
            new_lines.append(line)
        i += 1

    if fix and (total_errors > 0 or total_warnings > 0):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(new_lines))
        print(f"\n\033[92mSaved auto-fixes directly back to {filepath}\033[0m")
        
    print(f"\nValidation Summary: {total_errors} error(s), {total_warnings} warning(s) found across {block_index} blocks.")
    return total_errors == 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate Bilingual Markdown (.bi.md) translation files.")
    parser.add_argument("file", help="Path to the bilingual markdown file.")
    parser.add_argument("--fix", action="store_true", help="Auto-fix spacing errors and save them back to the file.")
    parser.add_argument("--glossary", help="Path to glossary.json file to validate dynamic terms.")
    
    args = parser.parse_args()
    success = validate_file(args.file, args.fix, args.glossary)
    if not success and not args.fix:
        sys.exit(1)
