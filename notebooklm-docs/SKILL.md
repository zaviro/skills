---
name: notebooklm-docs
description: "Use when the user wants to learn a new technology (language, framework, tool), asks 'prepare docs for NotebookLM', 'gather learning materials', or mentions using NotebookLM for study. Searches the web, recommends high-quality sources, downloads to local disk, and syncs a flattened copy to Google Drive."
license: MIT
metadata:
  version: 1.3.0
  author: Claude Code (adapted for Hermes Agent)
  hermes:
    tags: [notebooklm, learning, documentation, google-drive, curation]
    related_skills: []
---

# NotebookLM Document Preparation

Use this skill when the user wants to gather learning materials for Google NotebookLM.

## What NotebookLM Is

NotebookLM is a **RAG-based (Retrieval-Augmented Generation)** AI research assistant by Google. It answers questions exclusively from sources the user uploads — it does NOT search the web or use external knowledge. This grounded design eliminates hallucination but means output quality depends entirely on source quality.

**Key constraints to remember:**

| Constraint | Limit |
|------------|-------|
| Sources per notebook | **150** (hard limit — merge if approaching) |
| Words per source | 500,000 |
| Max file size | 200 MB |
| Supported formats | `.md`, `.pdf`, `.txt`, `.docx`, `.pptx`, `.csv`, `.epub`, Google Docs, Google Slides, YouTube URLs, pasted text |

**NotebookLM best practices (encode into your recommendations):**

1. **One notebook = one mission.** Don't create a generic "Learn X" notebook. Name with action + outcome, e.g. "Master TS type system: handbook + exercises."
2. **Curate sources ruthlessly.** Quality > quantity. A quick test: "Would I personally refer back to this multiple times?" If no, skip it.
3. **Merge related documents by default.** NotebookLM has a 150-source hard limit. Group related pages into coherent chapter-like files (e.g. all HTTP server pages → one `http-server.md`, all package manager CLI commands → one `package-manager.md`). This also improves retrieval quality by reducing overlapping sources. Only keep files separate if the user explicitly requests per-file granularity.
4. **Set a role in the notebook config.** E.g. "You are a technical learning assistant with engineering experience. Output structured study notes suitable for review."
5. **Prefer official documentation** + 1-2 high-quality supplementary books/guides + exercises. Avoid "just in case" articles, outdated tutorials, release notes, and framework-specific content unless the user specifically wants that framework.
6. **Ask for structured output** from NotebookLM every time (bullet lists, comparison tables, code examples with pitfalls).
7. **Save good answers back as notes** → promote to sources for a virtuous feedback loop.

## Workflow

This skill has three phases. Always complete phase 1 and get user approval before proceeding to phases 2-3.

---

### Phase 1: Research & Recommend

**Goal:** Understand what the user wants to learn, search for the best sources, and present a download plan.

#### Step 1.1: Clarify the learning goal

If the user's request is vague (e.g. "I want to learn Rust"), ask 2-3 clarifying questions (use the `clarify` tool):

- What's their current experience level? (beginner / experienced in similar languages)
- What's the learning goal? (build projects / pass interviews / understand internals)
- Any specific areas of focus? (web backend / systems / embedded)
- Do they use a related framework? (e.g. React + TS, Django + Python)

#### Step 1.2: Search for sources

Search the web for the best learning materials. Use `web_search` and `web_extract` tools. Prioritize in this order:

1. **Official documentation** — always the first choice. Find the official docs repo.
2. **One high-quality open-source book** — look for community-standard deep-dive books (e.g. "TypeScript Deep Dive" by Basarat, "Rust Book", "Eloquent JavaScript").
3. **Exercises / challenges** — interactive practice repos (e.g. type-challenges for TS, rustlings for Rust).
4. **Official wiki / FAQ** — common errors and coding guidelines.
5. **Framework cheatsheet** — only if the user works with a related framework (React+TS, Rocket+Diesel for Rust, etc.).

**What to SKIP:**

- Release notes / changelogs (low information density, NotebookLM is not a changelog reader)
- Outdated/legacy versions of docs (e.g. if there's a v2 handbook, skip v1)
- Tutorials for unrelated frameworks (Angular tutorial when learning TS basics)
- "Top 10 X in 202X" blog posts
- Video transcripts unless the user explicitly requests them

#### Step 1.3: Present the plan

Present findings as a structured plan with:

1. **A table** listing each merged source group, raw file count → merged file count, estimated word count, and why it's included.
2. **Merge plan** — explain how related files are grouped into chapter-like documents. Always merge by default; only keep files separate if the user explicitly requests per-file granularity.
3. **Proposed directory structure** (nested categorization under local path, flattened under Google Drive path).
4. **Total estimates** (merged files, words, % of 150-file limit).
5. **Explicit "skipped" list** — what you intentionally left out and why. This builds user trust.

Format the plan exactly like this:

```
## Download Plan: <Topic>

### Sources

| # | Merged Document | Raw Files | Est. Words | Why |
|---|----------------|-----------|------------|-----|
| 1 | Getting Started | ~4 → 1 | ~8,000 | Core learning path |
| 2 | ... | ... → ... | ... | ... |

**Total: ~X merged files, ~Y words (Z% of 150-file limit, W% of single-source 500k limit for the largest file)**

### Merge strategy

- `http-server.md`: 合并 http/server + http/routing + http/error-handling → 一个完整的 HTTP 服务器章节
- `package-manager.md`: 合并 add + install + remove + update + link + bunx → 日常包管理命令速查
- （列出每个合并组的理由）

### Proposed directory structure

When the plan spans multiple notebooks, use the pattern `<topic>/<sub-notebook>` to keep everything under one topic directory:

Local (`~/文档/notebooklm note/<topic>/`):
<topic>/
├── core/                  ← 第一个 notebook（核心/快速上手）
│   ├── SOURCES.md
│   ├── 01-getting-started.md
│   ├── 02-http-server.md
│   └── ...
├── advanced/              ← 第二个 notebook（进阶/滞后）
│   ├── SOURCES.md
│   ├── 11-networking.md
│   └── ...
└── exercises/             ← 可选：练习/挑战（第三个 notebook）

Google Drive (`Document/notebooklm note/<topic>/`):
<topic>/
├── core/                  ← 扁平：所有 .md 直接放在此目录
├── advanced/              ← 扁平：所有 .md 直接放在此目录
└── exercises/

**Naming rules:**
- One topic = one directory. Nest sub-notebooks inside: `<topic>/core`, `<topic>/advanced`, `<topic>/exercises`.
- Never use hyphenated suffixes like `<topic>-core`, `<topic>-advanced` — these scatter the topic across multiple top-level directories.
- Each sub-notebook becomes its own NotebookLM notebook. Flat files within each sub-directory — no nested subdirectories inside a notebook.

### Skipped

- X — reason
- Y — reason
```

Wait for user approval before proceeding.

---

### Phase 2: Download to Local

**Goal:** Execute the approved plan. Clone/download sources to `~/文档/notebooklm note/<topic>/`.

#### Step 2.1: Create `SOURCES.md`

In the root of the topic directory, create a `SOURCES.md` file using `write_file` documenting every source:

```markdown
# Sources for <Topic> — <Date>

## Source 1: <Name>
- **URL:** <repo or website URL>
- **Version:** <git branch/tag/commit, or "snapshot as of YYYY-MM-DD">
- **License:** <SPDX identifier or "See repo">
- **Selection rationale:** <one sentence why this was chosen>

## Source 2: ...
...
```

Always record the **exact version** (branch, tag, commit hash, or date) so the provenance is reproducible.

#### Step 2.2: Download and merge sources

- For GitHub repos: use `terminal` to run `git clone --depth 1 --branch <branch> <url> /tmp/<name>` then extract only the relevant files. **Never clone directly into the target directory** — clone to `/tmp/` first, then extract.
- For websites: use `web_extract` to get the page content and `write_file` to save as `.md`.
- **Create merged files** according to the approved merge plan. For each merged group, concatenate the individual source files into one chapter-like `.md` file with clear section headers and a table of contents at the top. Use the format:
  ```markdown
  # <Merged Document Title>
  
  ## 目录
  
  - [章节 1: <Title>](#章节-1-title)
  - [章节 2: <Title>](#章节-2-title)
  
  ---
  
  ## 章节 1: <Title>
  
  <original content>
  
  ---
  
  ## 章节 2: <Title>
  
  <original content>
  ```
- Preserve file provenance: at the bottom of each merged file, add a `<!-- sources: ... -->` comment listing the original source files.

#### Step 2.3: Verify

Print a summary after download:
- Total `.md` files and word count
- Per-source breakdown
- Any files that failed to download

Keep the target directory path lowercase and consistent:
```
~/文档/notebooklm note/<topic>/
```

---

### Phase 3: Sync to Google Drive

**Goal:** Copy all `.md` files to Google Drive in a **flattened** structure (no subdirectories).

#### Step 3.1: Check Google Drive mount

Verify the rclone mount is active:
```bash
mount | grep "gdrive.*rclone"
```
The expected mount point is `/home/zaviro/mnt/google-drive`. If not mounted, warn the user and skip this phase.

#### Step 3.2: Create target directory

```bash
mkdir -p "/home/zaviro/mnt/google-drive/Document/notebooklm note/<topic>"
```

#### Step 3.3: Copy files flat

**Flatten all files** — NotebookLM doesn't preserve directory structure when importing, and flat organization makes browsing sources easier. Use unique filenames to avoid collisions:

```bash
# For each .md file, use its relative path (with / replaced by -- or _) as the flat filename
find "~/文档/notebooklm note/<topic>" -name "*.md" -exec sh -c '
  rel="${1#~/文档/notebooklm note/<topic>/}"
  flatname=$(echo "$rel" | sed "s|/|_|g")
  cp "$1" "/home/zaviro/mnt/google-drive/Document/notebooklm note/<topic>/$flatname"
' _ {} \;
```

This converts e.g. `official-docs/handbook-v2/Everyday Types.md` → `official-docs_handbook-v2_Everyday Types.md`, preserving the source context in the filename while keeping everything in one directory.

The `SOURCES.md` file is copied as-is (it's already at the root level).

#### Step 3.4: Verify

```bash
echo "Local:  $(find ~/文档/notebooklm\ note/<topic> -name '*.md' | wc -l) files"
echo "Drive:  $(find /home/zaviro/mnt/google-drive/Document/notebooklm\ note/<topic> -name '*.md' | wc -l) files"
```

Both counts should match.

#### Step 3.5: Final summary

Tell the user:
- Local path and Google Drive path
- File counts match
- Next step: "Open NotebookLM → create notebook → import from Google Drive → `Document/notebooklm note/<topic>/`"

---

## Reference: Case studies

These real-world examples illustrate how the curation principles above translate into concrete decisions. Use them as patterns, not rules — each topic has its own shape.

### Example 1: TypeScript

**Context:** Learning TS from scratch, user has frontend (React) experience.

**What was curated (final output: ~20 merged files):**
| # | Merged Document | Raw → Merged | Role |
|---|----------------|-------------|------|
| 1 | Getting Started | 6 → 1 | Installation, config, first steps |
| 2 | Handbook | 15 → 1 | Core type system walkthrough |
| 3 | Reference | 10 → 1 | Utility types, enums, modules |
| 4 | Declaration Files | 8 → 1 | .d.ts authoring |
| 5 | TS Deep Dive (basarat) | 60 → 5 | Community deep dive, grouped by theme |
| 6 | Release Notes 4.0–6.0 | 21 → 1 | Modern feature specs |
| 7 | TS Wiki | 4 → 1 | FAQ + coding guidelines |
| 8 | type-challenges | 30 → 3 | Exercises grouped by difficulty |
| 9 | React+TS Cheatsheet | 8 → 1 | Framework integration |

**Merge strategy:** Handbook chapters naturally form one coherent book chapter. 21 release notes combined into one chronological reference. 30 exercise files grouped into easy/medium/hard tiers. 60 deep-dive files grouped into 5 thematic bundles (types, patterns, advanced, etc.).

**Total: ~20 merged files, ~244k words (13% of 150-file limit)**

**What was skipped and why:**
| Skipped | Reason | Re-evaluation trigger |
|---------|--------|-----------------------|
| handbook-v1 | Superseded by v2 | — |
| Release notes TS 1.0–3.9 (~28 files) | Pre-4.0 era; TS 1.5/1.7 contain experimental decorator docs that **conflict** with the ECMAScript standard decorators in TS 5.0+. Plus, pre-4.0 notes describe a pre-strict-mode world where `strictNullChecks` was opt-in — stale pedagogical framing even if syntax is still valid | If the user needs historical context on specific features (e.g. "when was optional chaining introduced?"), add individual versions on demand |
| Angular/Gulp/ASP.NET tutorials | Framework-specific, not relevant to user's stack | Only include if user uses that framework |
| Compiler internals (AST, binder, etc.) | Too deep for learning the language | Include if user is building compiler tools |
| diagrams/ SVGs | NotebookLM can't interpret images | Only include if the accompanying .md describes them well |

### General lessons (apply to any topic)

1. **The "superseded" check:** If a source has a v2, skip v1. One canonical version per topic.
2. **The "chronological vs pedagogical" test:** Release notes and changelogs teach *what changed when*, not *how to use it now*. They can be valuable for reference but shouldn't crowd out structured learning materials. Gauge based on plan tier (Free = skip, Plus = selective inclusion).
3. **The "framework filter":** Tutorials that assume a framework the user doesn't use are noise, not signal.
4. **The "depth ceiling":** Compiler internals, build scripts, and architecture docs belong in a "contribute to X" notebook, not a "learn X" notebook.
5. **The "image blind spot":** NotebookLM is text-only. SVG diagrams, screenshots, and visual guides add no value. Skip them unless the text alone is self-sufficient.
6. **Drive sync is the most reliable import path** — always sync to Google Drive as the final step.
7. **The 150-file hard limit with mandatory merging:** The total number of sources must stay under **150 files**. Merge related documents into larger chapter-like files by default (e.g. combine all HTTP server pages into one, all package manager CLI commands into one). This keeps the notebook well under the limit and improves retrieval quality by reducing overlapping sources. Present the merge strategy in the plan for user review. Only skip merging if the user explicitly opts out.

## Notes

- The local directory is `notebooklm note` (lowercase, no dash) to match Google Drive path conventions.
- **Directory naming convention:** Use `<topic>/<sub-notebook>` (e.g. `bun/core`, `bun/advanced`), never `<topic>-<suffix>`. One topic = one top-level directory with all sub-notebooks nested inside.
- If the user already has materials in the target directory, ask before overwriting.
- If a source is a website (not a git repo), use `web_extract` to capture the content and note "snapshot as of YYYY-MM-DD" in SOURCES.md.
- Never clone git repos directly into the target directory — always use `/tmp/` as a staging area.
