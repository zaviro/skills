import sys
import os
import html
import re
import urllib.request
import subprocess
from bs4 import BeautifulSoup

def get_match_key(text):
    if not text:
        return ""
    text = text.lower()
    # Remove markdown link URLs (e.g. [text](url) -> text)
    text = re.sub(r'\[([^\]\n]+)\]\([^\)\n]+\)', r'\1', text)
    # Remove markdown syntax characters
    text = re.sub(r'[`\*_\[\]\(\)]', '', text)
    # Restore html entities
    text = html.unescape(text)
    # Remove list prefixes
    text = re.sub(r'^[\-\*]\s+', '', text)
    text = re.sub(r'^\d+\.\s+', '', text)
    # Keep only alphanumeric characters to avoid punctuation/space mismatch
    text = re.sub(r'[^a-z0-9]', '', text)
    return text

def format_inline_md(text):
    text = html.escape(text)
    text = re.sub(r'\*\*(.*?)\*\*|__(.*?)__', r'<strong>\1\2</strong>', text)
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
    
    # Unescape red span fallback
    text = text.replace('&lt;span style=&quot;color:red&quot;&gt;', '<span style="color:red">')
    text = text.replace('&lt;span style=&#x27;color:red&#x27;&gt;', '<span style="color:red">')
    text = text.replace('&lt;/span&gt;', '</span>')
    return text

def clean_prefix(text):
    text = re.sub(r'^[\-\*]\s+', '', text)
    text = re.sub(r'^\d+\.\s+', '', text)
    return text

def compile_to_html(bi_md_path, output_path, container_selector=None):
    with open(bi_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse metadata
    permalink = ""
    title = ""
    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if fm_match:
        fm_block = fm_match.group(1)
        content = content[fm_match.end():]
        for line in fm_block.split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k == "permalink":
                    permalink = v
                elif k == "title":
                    title = v

    if not permalink:
        print("Error: permalink not found in frontmatter.")
        sys.exit(1)

    # 1. Fetch original HTML page from official site or local cache
    if not permalink.startswith('/'):
        permalink = '/' + permalink
    url = f"https://www.typescriptlang.org{permalink}"
    
    cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../.html_cache')
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, permalink.replace('/', '_') + '.html')
    
    html_content = ""
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as cf:
            html_content = cf.read()
    else:
        print(f"Fetching original HTML from {url}...")
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                html_content = response.read().decode('utf-8')
            with open(cache_file, 'w', encoding='utf-8') as cf:
                cf.write(html_content)
        except Exception as e:
            print(f"Warning: urllib failed: {e}. Trying curl...")
            try:
                res = subprocess.run(['curl', '-s', url], capture_output=True, text=True, timeout=15)
                if res.returncode == 0 and res.stdout:
                    html_content = res.stdout
                    with open(cache_file, 'w', encoding='utf-8') as cf:
                        cf.write(html_content)
            except Exception as e2:
                print(f"Error fetching original HTML: {e2}")
                sys.exit(1)

    if not html_content:
        print("Error: Could not retrieve original HTML page.")
        sys.exit(1)

    # 2. Parse bilingual translations mapping into an ordered list of translation blocks
    translation_blocks = []
    lines = content.split('\n')
    i = 0
    current_block_type = None
    current_bi_lines = []
    
    while i < len(lines):
        line = lines[i]
        if line.strip() == ':::block':
            current_block_type = 'bilingual'
            current_bi_lines = []
            i += 1
            continue
            
        if line.strip() == ':::':
            if current_block_type == 'bilingual':
                bi_content = "\n".join(current_bi_lines)
                en_match = re.search(r'\[en\]\n(.*?)(?=\n\[zh\]|\Z)', bi_content, re.DOTALL)
                zh_match = re.search(r'\[zh\]\n(.*)', bi_content, re.DOTALL)
                
                en_text = en_match.group(1).strip() if en_match else ""
                zh_text = zh_match.group(1).strip() if zh_match else ""
                
                translation_blocks.append({
                    'en': en_text,
                    'zh': zh_text
                })
                
                current_bi_lines = []
                current_block_type = None
            i += 1
            continue
            
        if current_block_type == 'bilingual':
            current_bi_lines.append(line)
            i += 1
            continue
        i += 1

    # 3. Parse and manipulate original HTML DOM using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Gather target tags outside of code blocks, prioritizing the custom content container
    content_container = None
    if container_selector:
        try:
            content_container = soup.select_one(container_selector)
        except Exception as e:
            print(f"Warning: Invalid CSS selector '{container_selector}': {e}")
            
    if content_container:
        print(f"Restricting search domain to container selector: '{container_selector}'")
        target_tags = [
            tag for tag in content_container.find_all(['p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if tag.find_parent('pre') is None
        ]
    else:
        print("Searching globally in body (excluding navigation and sidebars)...")
        target_tags = [
            tag for tag in soup.find_all(['p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if tag.find_parent('pre') is None and tag.find_parent('nav', id='sidebar') is None and tag.find_parent('header') is None and tag.find_parent('footer') is None
        ]
    
    tag_idx = 0
    matched_count = 0
    
    # Natural physical sequence matching algorithm
    for block in translation_blocks:
        en_sub_lines = [l.strip() for l in block['en'].split('\n') if l.strip()]
        zh_sub_lines = [l.strip() for l in block['zh'].split('\n') if l.strip()]
        has_list_or_header = False
        for line in en_sub_lines:
            line_str = line.strip()
            if line_str.startswith('#') or line_str.startswith(('- ', '* ')) or re.match(r'^\d+\.\s+', line_str):
                has_list_or_header = True
                break
        
        # 3a. Line-by-line alignment matching (only for lists or headers)
        if len(en_sub_lines) == len(zh_sub_lines) and has_list_or_header:
            for el, zl in zip(en_sub_lines, zh_sub_lines):
                el_key = get_match_key(el)
                if not el_key:
                    continue
                
                found = False
                limit = min(tag_idx + 8, len(target_tags))
                for idx in range(tag_idx, limit):
                    tag = target_tags[idx]
                    tag_key = get_match_key(tag.get_text())
                    
                    if not tag_key:
                        continue
                    
                    if el_key == tag_key or (len(tag_key) > 15 and el_key.startswith(tag_key)) or (len(el_key) > 15 and tag_key.startswith(el_key)):
                        # Format translation HTML
                        zh_html = format_inline_md(zl)
                        new_tag = soup.new_tag(tag.name)
                        new_tag['class'] = tag.get('class', []) + ['lang-zh']
                        new_tag.append(BeautifulSoup(zh_html, 'html.parser'))
                        
                        # Insert translation node directly after
                        tag.insert_after(new_tag)
                        
                        # Advance matching cursor
                        tag_idx = idx + 1
                        matched_count += 1
                        found = True
                        break
        # 3b. Fallback whole-block matching
        else:
            block_key = get_match_key(block['en'])
            if block_key:
                found = False
                limit = min(tag_idx + 8, len(target_tags))
                for idx in range(tag_idx, limit):
                    tag = target_tags[idx]
                    tag_key = get_match_key(tag.get_text())
                    
                    if not tag_key:
                        continue
                    
                    if block_key == tag_key or (len(tag_key) > 15 and block_key.startswith(tag_key)):
                        zh_html = format_inline_md(block['zh'])
                        new_tag = soup.new_tag(tag.name)
                        new_tag['class'] = tag.get('class', []) + ['lang-zh']
                        new_tag.append(BeautifulSoup(zh_html, 'html.parser'))
                        
                        tag.insert_after(new_tag)
                        tag_idx = idx + 1
                        matched_count += 1
                        break

    print(f"Sequentially matched and inserted {matched_count} translation elements.")

    # 4. Inject style overrides for bilingual typography and float theme toggles
    head = soup.head
    if head:
        style_tag = soup.new_tag('style')
        style_tag.string = """
        .lang-zh {
            color: #737373 !important;
            font-size: 0.9em !important;
            margin-top: -0.4em !important;
            margin-bottom: 0.8em !important;
            display: block !important;
        }
        .dark-theme .lang-zh {
            color: #a3a3a3 !important;
        }
        h1.lang-zh, h2.lang-zh, h3.lang-zh, h4.lang-zh {
            border: none !important;
            padding-bottom: 0 !important;
            margin-top: -0.3em !important;
        }
        li.lang-zh {
            list-style-type: none !important;
            padding-left: 0 !important;
            margin-top: -0.2em !important;
        }
        #theme-toggle-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: var(--raised-background-color, #313131);
            border: 1px solid var(--border-color, #444);
            color: var(--text-color, #fff);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: var(--raised-box-shadow);
            z-index: 1000;
        }
        """
        head.append(style_tag)

    # 5. Inject theme toggle button scripts
    body = soup.body
    if body:
        toggle_html = """
        <button id="theme-toggle-btn" onclick="toggleLocalTheme()" title="切换主题">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
        </button>
        <script>
            function toggleLocalTheme() {
                const htmlEl = document.documentElement;
                if (htmlEl.classList.contains("dark-theme")) {
                    htmlEl.className = "light-theme";
                    localStorage.setItem("theme", "light-theme");
                } else {
                    htmlEl.className = "dark-theme";
                    localStorage.setItem("theme", "dark-theme");
                }
            }
        </script>
        """
        body.append(BeautifulSoup(toggle_html, 'html.parser'))

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(f"Successfully compiled {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compile_bi_markdown.py <input.bi.md> <output.html> [container_selector]")
        sys.exit(1)
    container = sys.argv[3] if len(sys.argv) > 3 else None
    compile_to_html(sys.argv[1], sys.argv[2], container)
