---
name: webdoc-structure-processor
description: Extracts document structures into bilingual Markdown templates and reconstructs compiled HTML pages from translated bilingual Markdown. Make sure to use this skill whenever the user wants to extract block templates from technical articles/readmes, compile bilingual markdown files into HTML pages, or replicate/reconstruct a website's layout and CSS for bilingual presentation.
---

# Webdoc Structure Processor

This skill automates the extraction of structure templates from technical documents and the subsequent compilation/reconstruction of translated bilingual Markdown into premium, interactive bilingual HTML pages. It is optimized to replicate the official layout, styles, and scripts of original websites (such as the TypeScript official site) using zero-intrusion DOM injection.

## Workflow Overview

The structure processing workflow operates as follows:
1. **Bilingual Template Generation**: Use the bundled `scripts/create_bi_template.py` script to parse an English Markdown file and generate a Bilingual Markdown template (`.bi.md`) wrapped in `:::block` segments.
2. **Merge and Compile HTML**:
   - Merge any translated segments back into a single `final.bi.md` file.
   - Run `scripts/compile_bi_markdown.py` to fetch the original page HTML (or local cache), parse the DOM, and insert bilingual translation blocks sequentially using a physical matching algorithm.
3. **Web Page Visual Inspection (Pass 2 - Layout & Style Focus)**:
   - Audit the compiled HTML page using browser automation (e.g. the `browser-use` skill or headless browser CLI commands). Inspect the page visually through screenshots.
   - Focus strictly on layout fidelity, sidebar overlaps, CSS overflows, line height, responsive scaling, and dark-theme toggle correctness, ignoring translation spelling.

---

## Detailed Step-by-Step Instructions

### Step 1: Pre-process and Template Generation
Generate the Bilingual Markdown (`.bi.md`) template using:
```bash
python3 scripts/create_bi_template.py <source.md> <target.bi.md>
```
This script splits paragraphs and headings into `:::block` structures containing separate `[en]` and `[zh]` segments to prepare them for AI translation.

### Step 2: Merge and Compile HTML
Once the bilingual Markdown blocks are translated and validated:
1. **Merge Chunks**: If the document was split into chunks during translation, merge them back into a single `final.bi.md` file using `dev/dev_utils.py` from the translator workspace.
2. **Compile**: Compile the bilingual Markdown into a high-fidelity HTML file:
   ```bash
   python3 scripts/compile_bi_markdown.py <final.bi.md> <output_bilingual.html>
   ```
   This script parses the `.bi.md` structure, fetches the official page at the permalink specified in the frontmatter, and injects the bilingual translations natively after each matching English tag in the DOM.

### Step 3: Web Page Visual Inspection (Pass 2 - Layout & Style Audit)

Perform a dedicated visual review to check the layout, CSS fidelity, and rendering correctness of the output page.

#### Mode A: Multi-Agent Visual Inspection (If Subagents & Browser-Use are Supported)
1. **Spawn Web Page Visual Inspector**: Delegate to a subagent equipped with browser automation capabilities. Provide the following task description:
   ```
   Inspect the layout and CSS rendering of the compiled HTML page <output_bilingual.html> on a local browser. 
   Perform the following visual checks:
   1. [Sidebar & Navigation]: Ensure the sidebar navigation menu is fully rendered, positioned on the left side, and does NOT overlap with the main content container (#handbook-content).
   2. [Style Fidelity]: Ensure the page successfully inherits the official TypeScript CSS and contains no broken or disjointed styling.
   3. [Bilingual Typography]: Ensure the Chinese translated paragraphs (with the .lang-zh class) align beautifully directly beneath the corresponding English paragraphs.
   4. [List Alignment]: Verify that translated list items do NOT display duplicate bullet icons (the lang-zh bullet points must be removed via 'list-style-type: none').
   5. [Dark Mode Toggle]: Click the theme toggle floating button to switch to dark mode. Verify that the font color transitions smoothly (e.g. .lang-zh text transitions to #a3a3a3 and does not become invisible on a dark background).
   6. [Responsive Check]: Shrink the browser width to check mobile layout scaling.
   
   Take screenshots of key sections in both light and dark themes. Inspect the screenshots. If you observe any layout defects (e.g. overlapping panels, invisible fonts, CSS overflows), report the exact visual issues so they can be fixed in the compiler style overrides.
   ```

#### Mode B: Sequential Fallback (Manual Headless Screenshot Check)
If browser-use or subagents are unavailable, audit the output visually yourself:
1. **Capture Headless Screenshots**: Run a local headless browser command (e.g., Puppeteer or Playwright) to capture screenshots of the compiled HTML page under different viewports and theme settings.
2. **Visual Audit**: View the captured screenshots to visually verify the layout. Fix any CSS bugs in the `compile_bi_markdown.py` style overrides and recompile until the layout is perfect.

---

## Visual Restoration Guidelines

- **Official Style Fidelity**: The generated bilingual pages must inherit the official global CSS and layout blocks (such as `#top-menu`, `nav#sidebar`, `footer#site-footer`, and the `#handbook-content` container) from the official website. Do not apply heavy custom web app structures.
- **Paragraph-Stacked Bilingual Layout**: Place the Chinese translated paragraph (with the `.lang-zh` class) directly beneath the corresponding English paragraph. The Chinese translation behaves like a sub-sentence/explanation, making the page taller while keeping the visual layout aligned with the official site.
- **List Item Rendering**: Avoid custom list structures. Wrap list items natively inside `<ul>` or `<ol>` tags. Place the Chinese translated list items (with the `.lang-zh` class) directly below the English `<li>` tags. In the custom CSS block, remove the bullet points for `li.lang-zh` (`list-style-type: none !important`) so they align under the English bullet points without duplicating bullet icons.
- **Code Block Integrity**: Code blocks must remain entirely un-wrappered and un-styled, styled by the official site's CSS and syntax highlighter.

---

## Directory Conventions

```
webdoc-structure-processor/
├── SKILL.md                         # 本技能说明文档
├── .gitignore                       # 忽略编译缓存和临时文件
└── scripts/                         # 运行工具
    ├── create_bi_template.py        # 提取对照模版
    ├── compile_bi_markdown.py       # 装配编译还原为 HTML
    └── template.html                # 基础网页模版
```
