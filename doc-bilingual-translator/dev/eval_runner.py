import re
import os
import sys
import argparse
import difflib
import html
import json

def parse_bi_blocks(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    blocks = []
    lines = content.split('\n')
    
    in_block = False
    current_block = []
    block_index = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.strip() == ':::block':
            in_block = True
            current_block = []
            i += 1
            continue
            
        if line.strip() == ':::':
            if in_block:
                block_index += 1
                block_content = "\n".join(current_block)
                en_match = re.search(r'\[en\]\n(.*?)(?=\n\[zh\]|\Z)', block_content, re.DOTALL)
                zh_match = re.search(r'\[zh\]\n(.*)', block_content, re.DOTALL)
                
                if en_match and zh_match:
                    blocks.append({
                        "index": block_index,
                        "en": en_match.group(1).strip(),
                        "zh": zh_match.group(1).strip()
                    })
                in_block = False
            i += 1
            continue
            
        if in_block:
            current_block.append(line)
        i += 1
        
    return blocks

# Dynamic import helper for validator methods to avoid copy-paste
try:
    import validate_bi_markdown as validator
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import validate_bi_markdown as validator

def calculate_metrics(blocks, glossary=None):
    total_errors = 0
    total_warnings = 0
    total_space_issues = 0
    total_reserved_warnings = 0
    total_escapes = 0
    
    for b in blocks:
        # Run spacing check
        _, spaces = validator.check_spacing(b["zh"])
        total_space_issues += spaces
        
        # Run full validation block check
        errors, warnings, _ = validator.validate_block(b["en"], b["zh"], b["index"], fix=False, glossary=glossary)
        
        total_errors += len(errors)
        for w in warnings:
            if "space" in w.lower():
                pass # Already counted
            elif "keyword" in w.lower() or "reserved" in w.lower():
                total_reserved_warnings += 1
            elif "escape valve" in w.lower():
                total_escapes += 1
            else:
                total_warnings += 1
                
    return {
        "errors": total_errors,
        "spacing_issues": total_space_issues,
        "reserved_word_warnings": total_reserved_warnings,
        "escapes": total_escapes,
        "other_warnings": total_warnings
    }

def character_diff(a, b):
    matcher = difflib.SequenceMatcher(None, a, b)
    result_a = []
    result_b = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        sub_a = a[i1:i2]
        sub_b = b[j1:j2]
        if tag == 'equal':
            result_a.append(html.escape(sub_a))
            result_b.append(html.escape(sub_b))
        elif tag == 'replace':
            result_a.append(f'<del>{html.escape(sub_a)}</del>')
            sub_b_vis = sub_b.replace(' ', '<span class="space-inserted"> </span>')
            result_b.append(f'<ins>{sub_b_vis}</ins>')
        elif tag == 'delete':
            result_a.append(f'<del>{html.escape(sub_a)}</del>')
        elif tag == 'insert':
            sub_b_vis = sub_b.replace(' ', '<span class="space-inserted"> </span>')
            result_b.append(f'<ins>{sub_b_vis}</ins>')
            
    return "".join(result_a), "".join(result_b)

def generate_report(baseline_file, latest_file, output_html, glossary_path=None):
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
            print(f"[EVAL] Loaded glossary with {len(glossary)} terms.")
        except Exception as e:
            print(f"[EVAL] Warning: Failed to load glossary file from {glossary_path}: {e}")

    base_blocks = parse_bi_blocks(baseline_file)
    late_blocks = parse_bi_blocks(latest_file)
    
    # Calculate metrics
    base_kpis = calculate_metrics(base_blocks, glossary)
    late_kpis = calculate_metrics(late_blocks, glossary)
    
    # Map blocks by index for robust diffing
    base_map = {b["index"]: b for b in base_blocks}
    late_map = {b["index"]: b for b in late_blocks}
    
    all_indices = sorted(list(set(base_map.keys()) | set(late_map.keys())))
    
    diff_html_rows = ""
    for idx in all_indices:
        b_block = base_map.get(idx, {"en": "", "zh": ""})
        l_block = late_map.get(idx, {"en": "", "zh": ""})
        
        en_text = l_block["en"] if l_block["en"] else b_block["en"]
        
        # Calculate character-level diff on translations
        diff_base, diff_late = character_diff(b_block["zh"], l_block["zh"])
        
        # Run validators for local warnings indicators
        b_errors, b_warns, _ = validator.validate_block(b_block["en"], b_block["zh"], idx, fix=False, glossary=glossary)
        l_errors, l_warns, _ = validator.validate_block(l_block["en"], l_block["zh"], idx, fix=False, glossary=glossary)
        
        b_alert_status = ""
        if b_errors:
            b_alert_status = f'<div class="alert error">✘ {len(b_errors)} Error(s)</div>'
        elif b_warns:
            b_alert_status = f'<div class="alert warn">▲ {len(b_warns)} Warning(s)</div>'
            for w in b_warns:
                b_alert_status += f'<div class="warning-detail">• {html.escape(w)}</div>'
            
        l_alert_status = ""
        if l_errors:
            l_alert_status = f'<div class="alert error">✘ {len(l_errors)} Error(s)</div>'
        elif l_warns:
            l_alert_status = f'<div class="alert warn">▲ {len(l_warns)} Warning(s)</div>'
            for w in l_warns:
                l_alert_status += f'<div class="warning-detail">• {html.escape(w)}</div>'
            
        diff_html_rows += f'''
        <div class="block-item">
            <div class="block-header">
                <span>Block #{idx}</span>
            </div>
            <div class="block-body">
                <div class="col col-en">
                    <h4>English Context</h4>
                    <div class="text-en">{html.escape(en_text)}</div>
                </div>
                <div class="col col-baseline">
                    <h4>Baseline Translation</h4>
                    {b_alert_status}
                    <div class="text-zh" style="margin-top:10px;">{diff_base}</div>
                </div>
                <div class="col col-latest">
                    <h4>Latest Iteration</h4>
                    {l_alert_status}
                    <div class="text-zh" style="margin-top:10px;">{diff_late}</div>
                </div>
            </div>
        </div>
        '''
        
    # Helper to format delta badges
    def format_delta(base_val, late_val, invert=False):
        delta = late_val - base_val
        sign = "+" if delta > 0 else ""
        if delta == 0:
            return f'<span class="kpi-delta zero">No Change</span>'
        
        # Usually decreases are good for issues/errors (invert=False means decrease is good)
        is_good = (delta < 0) if not invert else (delta > 0)
        badge_class = "good" if is_good else "bad"
        return f'<span class="kpi-delta {badge_class}">{sign}{delta}</span>'

    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bilingual Translation Iteration Report</title>
    <style>
        :root {{
            --bg-page: #0f172a;
            --bg-card: #1e293b;
            --border-color: #334155;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --primary-color: #38bdf8;
            
            --color-good: #10b981;
            --color-bad: #ef4444;
            --color-warn: #f59e0b;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-page);
            color: var(--text-primary);
            margin: 0;
            padding: 32px 16px;
        }}
        
        .container {{
            max-width: 1300px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        
        h1 {{
            font-size: 2.2rem;
            font-weight: 800;
            margin: 0 0 8px 0;
            letter-spacing: -0.025em;
        }}
        
        .subtitle {{
            color: var(--text-secondary);
            font-size: 1.1rem;
            margin: 0;
        }}
        
        /* KPI Cards Grid */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .kpi-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        
        .kpi-card h3 {{
            margin: 0 0 16px 0;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
        }}
        
        .kpi-values {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 16px;
        }}
        
        .kpi-val {{
            font-size: 1.8rem;
            font-weight: 700;
        }}
        
        .kpi-val.baseline {{
            color: var(--text-secondary);
            text-decoration: line-through;
            font-size: 1.4rem;
        }}
        
        .kpi-val.latest {{
            color: var(--text-primary);
        }}
        
        .kpi-arrow {{
            color: var(--text-secondary);
            font-size: 1.2rem;
        }}
        
        .kpi-delta-wrapper {{
            margin-top: 12px;
        }}
        
        .kpi-delta {{
            font-size: 0.85rem;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 9999px;
            display: inline-block;
        }}
        
        .kpi-delta.good {{
            background-color: rgba(16, 185, 129, 0.15);
            color: var(--color-good);
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}
        
        .kpi-delta.bad {{
            background-color: rgba(239, 68, 68, 0.15);
            color: var(--color-bad);
            border: 1px solid rgba(239, 68, 68, 0.3);
        }}
        
        .kpi-delta.zero {{
            background-color: rgba(148, 163, 184, 0.1);
            color: var(--text-secondary);
            border: 1px solid rgba(148, 163, 184, 0.2);
        }}
        
        /* Diff Block List */
        .block-diff-list {{
            display: flex;
            flex-direction: column;
            gap: 28px;
        }}
        
        .block-item {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }}
        
        .block-header {{
            background-color: rgba(51, 65, 85, 0.3);
            padding: 14px 24px;
            border-bottom: 1px solid var(--border-color);
            font-weight: 700;
            color: var(--primary-color);
            font-size: 0.95rem;
        }}
        
        .block-body {{
            display: flex;
            flex-direction: column;
        }}
        
        @media (min-width: 1024px) {{
            .block-body {{
                flex-direction: row;
            }}
        }}
        
        .col {{
            flex: 1;
            padding: 24px;
            border-bottom: 1px solid var(--border-color);
        }}
        
        @media (min-width: 1024px) {{
            .col {{
                border-bottom: none;
                border-right: 1px solid var(--border-color);
            }}
            .col:last-child {{
                border-right: none;
            }}
        }}
        
        .col h4 {{
            margin: 0 0 16px 0;
            font-size: 0.8rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 1px solid rgba(148, 163, 184, 0.2);
            padding-bottom: 8px;
        }}
        
        .text-en {{
            font-family: Consolas, Monaco, "Andale Mono", monospace;
            font-size: 0.85rem;
            color: var(--text-secondary);
            white-space: pre-wrap;
            line-height: 1.5;
        }}
        
        .text-zh {{
            font-size: 1.02rem;
            line-height: 1.7;
            white-space: pre-wrap;
        }}
        
        /* Alert Labels */
        .alert {{
            font-size: 0.75rem;
            font-weight: 600;
            padding: 4px 8px;
            border-radius: 4px;
            display: inline-block;
            margin-bottom: 8px;
        }}
        
        .alert.error {{
            background-color: rgba(239, 68, 68, 0.15);
            color: var(--color-bad);
            border: 1px solid rgba(239, 68, 68, 0.3);
        }}
        
        .alert.warn {{
            background-color: rgba(245, 158, 11, 0.15);
            color: var(--color-warn);
            border: 1px solid rgba(245, 158, 11, 0.3);
        }}
        
        .warning-detail {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-left: 8px;
            margin-bottom: 4px;
        }}
        
        /* Diff Highlights */
        del {{
            background-color: rgba(239, 68, 68, 0.25);
            color: #fca5a5;
            text-decoration: none;
            border-bottom: 1px solid var(--color-bad);
            padding: 1px 2px;
            border-radius: 2px;
        }}
        
        ins {{
            background-color: rgba(16, 185, 129, 0.25);
            color: #6ee7b7;
            text-decoration: none;
            border-bottom: 1px solid var(--color-good);
            padding: 1px 2px;
            border-radius: 2px;
        }}
        
        .space-inserted {{
            background-color: rgba(245, 158, 11, 0.4);
            border: 1px dashed var(--color-warn);
            display: inline-block;
            width: 6px;
            height: 14px;
            vertical-align: middle;
            margin: 0 1px;
            border-radius: 1px;
        }}
        
        /* Red Escaped Span Indicators */
        span[style*="color:red"], span[style*="color: red"] {{
            border: 1px dashed var(--color-bad);
            padding: 1px 4px;
            border-radius: 4px;
            background-color: rgba(239, 68, 68, 0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Bilingual Translation Iteration Report</h1>
            <p class="subtitle">Quantitative Evaluation and Qualitative Side-by-Side Diff Analysis</p>
        </header>
        
        <!-- KPIs Row -->
        <section class="kpi-grid">
            <div class="kpi-card">
                <h3>Markdown Syntax Errors</h3>
                <div class="kpi-values">
                    <span class="kpi-val baseline">{base_kpis["errors"]}</span>
                    <span class="kpi-arrow">➔</span>
                    <span class="kpi-val latest">{late_kpis["errors"]}</span>
                </div>
                <div class="kpi-delta-wrapper">
                    {format_delta(base_kpis["errors"], late_kpis["errors"])}
                </div>
            </div>
            
            <div class="kpi-card">
                <h3>Missing Spacing Issues</h3>
                <div class="kpi-values">
                    <span class="kpi-val baseline">{base_kpis["spacing_issues"]}</span>
                    <span class="kpi-arrow">➔</span>
                    <span class="kpi-val latest">{late_kpis["spacing_issues"]}</span>
                </div>
                <div class="kpi-delta-wrapper">
                    {format_delta(base_kpis["spacing_issues"], late_kpis["spacing_issues"])}
                </div>
            </div>
            
            <div class="kpi-card">
                <h3>Reserved Keyword Warnings</h3>
                <div class="kpi-values">
                    <span class="kpi-val baseline">{base_kpis["reserved_word_warnings"]}</span>
                    <span class="kpi-arrow">➔</span>
                    <span class="kpi-val latest">{late_kpis["reserved_word_warnings"]}</span>
                </div>
                <div class="kpi-delta-wrapper">
                    {format_delta(base_kpis["reserved_word_warnings"], late_kpis["reserved_word_warnings"])}
                </div>
            </div>
            
            <div class="kpi-card">
                <h3>Uncertain Terms (Escape Red Spans)</h3>
                <div class="kpi-values">
                    <span class="kpi-val baseline">{base_kpis["escapes"]}</span>
                    <span class="kpi-arrow">➔</span>
                    <span class="kpi-val latest">{late_kpis["escapes"]}</span>
                </div>
                <div class="kpi-delta-wrapper">
                    {format_delta(base_kpis["escapes"], late_kpis["escapes"])}
                </div>
            </div>
        </section>
        
        <!-- Detailed Blocks List -->
        <section class="block-diff-list">
            {diff_html_rows}
        </section>
    </div>
</body>
</html>
'''
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"\n[EVAL] Re-generated iteration report at: {output_html}")
    print(f"[EVAL] Metrics: Errors {base_kpis['errors']}->{late_kpis['errors']}, Space Issues {base_kpis['spacing_issues']}->{late_kpis['spacing_issues']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate iteration difference of translated bilingual markdown files.")
    parser.add_argument("command", choices=["diff", "validate"], help="Action to perform.")
    parser.add_argument("--baseline", help="Path to the baseline .bi.md file.")
    parser.add_argument("--latest", help="Path to the latest translated .bi.md file.")
    parser.add_argument("--output", default="eval_report.html", help="Path to write the diff report HTML.")
    parser.add_argument("--glossary", help="Path to glossary.json file to validate dynamic terms.")
    
    args = parser.parse_args()
    
    if args.command == "diff":
        if not args.baseline or not args.latest:
            print("Error: --baseline and --latest are required for 'diff' command.")
            sys.exit(1)
        generate_report(args.baseline, args.latest, args.output, args.glossary)
    elif args.command == "validate":
        # Simply proxy to validator script
        pass
