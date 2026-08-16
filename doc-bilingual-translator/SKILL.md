---
name: doc-bilingual-translator
description: Translates technical documents (e.g., Markdown) into premium bilingual (English/Chinese) editions. Make sure to use this skill whenever the user wants to translate articles, technical docs, readme files, or handbook pages into bilingual format, or asks for "双语翻译", "中英对照", "bilingual translation", or wants to proofread and validate bilingual markdown files.
---

# Document Bilingual Translator

This skill automates the high-quality bilingual (English/Chinese) translation and validation of technical documents (such as Markdown). It integrates industry best practices including **Translate-Reflect-Refine** multi-agent workflows, **dynamic glossary extraction & binding**, **escape-valve red styling for uncertain terms**, and **automated format & terminology validation**.

## Workflow Overview

The translation workflow operates as follows:
1. **Dynamic Glossary Extraction**: Extract a chapter-specific terminology list (`glossary.json`) from the source document.
2. **Translate-Reflect-Refine**: Translate the bilingual Markdown blocks. For documents longer than 300 lines, split the file into segments first.
3. **Bilingual Markdown Review (Pass 1 - Semantic Audit)**: Spawn a dedicated proofreading subagent (or audit sequentially) to check for completeness, terminology alignment, and ensure no sentence or formatting syntax is omitted.
4. **Automated Spacing & Syntax Validation**: Run `scripts/validate_bi_markdown.py` to auto-correct CJK/Latin spacing (Pangu Spacing), enforce glossary usage, and audit syntax symmetry.
5. **Quality Comparison (Dev/Eval Mode)**: Run `dev/eval_runner.py` to evaluate iteration metrics against baselines.

---

## Detailed Step-by-Step Instructions

### Step 1: Context-Aware Translation & Peer-Review Audit

If the source document is longer than 300 lines, split the file into parts (e.g., `part1.bi.md`, `part2.bi.md`) using `dev/dev_utils.py` before translating.

#### Mode A: Multi-Agent Orchestration (If Subagents are Supported)
Spawn a team of subagents to handle translation and proofreading concurrently for maximum quality:

1. **Spawn Translators**: Launch parallel `self` subagents for each segment. Inject the entire original English document and `glossary.json` as read-only context, and provide the following translation prompt:
   ```
   Translate the Bilingual Markdown file <part.bi.md>.
   Please first read the entire <source.md> file and the dynamic glossary mapping in <glossary.json> for full context.
   
   For each :::block element in <part.bi.md>, perform the translation in a 3-step loop:
   1. [Translate]: Provide an initial direct translation of the [en] text to Chinese. Follow <glossary.json>.
   2. [Reflect]: Critically evaluate your translation: check for reserve words (types/APIs), glossary alignment, markdown format markers symmetry, spacing, and completeness (make sure no sentence is omitted).
   3. [Refine]: Write the polished translation into [zh], replacing the original English placeholder.
   ```

2. **Spawn Bilingual Markdown Reviewer (Pass 1 - Semantic Audit)**: After a segment is translated, delegate to a separate `self` subagent acting as a strict text-only Proofreader/Reviewer to audit the translation. Prompt:
   ```
   You are a strict, senior technical editor and bilingual proofreader. Your task is to audit <part.bi.md> translated by another agent. Your review must focus strictly on the text quality and translation semantics:
   1. [Accuracy]: Verify that the technical meaning is fully and precisely preserved. Do NOT allow types, keywords, or API names to be translated or altered.
   2. [Completeness]: Ensure NO sentence, clause, or phrase is omitted. If the English block contains multiple sentences, ensure every sentence has its corresponding translation in the Chinese block.
   3. [Readability]: Polish the translation to ensure it reads naturally and conforms to professional developer community standards.
   4. [Typesetting]: Check that a space is correctly placed between Chinese and English/numeric characters.
   
   If you find any issue, directly rewrite the [zh] block with the corrected translation. Overwrite the file with your reviewed version.
   ```

#### Mode B: Sequential Fallback (If Subagents are Unsupported)
If you cannot spawn subagents, handle the translation and proofreading sequentially in your own context:
1. **Translation Pass**: Iterate through all :::block elements in the template/segments. Translate the `[en]` text into `[zh]` using the glossary. Reflect on formatting and terminologies before writing each translation block.
2. **Review Pass**: Perform a separate, dedicated review pass. Compare the English and Chinese texts sentence-by-sentence to ensure no sentence or meaning has been omitted, and directly fix any formatting/readability issues.

### Step 2: Format and Glossary Validation
Execute the validator script to check formatting symmetry, auto-fix spacing issues (using placeholder-isolated Pangu Spacing), and audit glossary alignment:
```bash
python3 scripts/validate_bi_markdown.py <part.bi.md> --fix --glossary glossary.json
```
If errors are reported, or if warnings indicate red escape spans, review the block manually.

---

## Technical Translation Guidelines

- **Code Block Preservation**: Do NOT wrap code blocks (sections starting with ```` ``` ````) inside `:::block` wrappers. Code blocks must be preserved in their raw Markdown format directly between translation blocks. They are kept purely as read-only context for the AI agent to understand the technical flow and variable scope, but must never undergo translation or custom parsing.
- **Professionalism Over Fluency**: Tech-圈 default untranslated proper nouns and identifiers must remain in English. Keep types (`string`, `number`, `boolean`, `any`, `never`), runtime APIs (`typeof`, `instanceof`, `toString`), library/framework names, configuration flags, and variable names in English.
- **Typesetting**: Insert a space between Chinese and English/number characters.
- **Consistent Glossary**: Keep a consistent translation of standard terminology. Use:
  - `Narrowing` -> `收窄`
  - `Type Guard` -> `类型守卫`
  - `Union` -> `联合类型`
  - `Static Type-Checking` -> `静态类型检查`
  - `Downleveling` -> `降级`
  - `Control Flow Analysis` -> `控制流分析`
  - `Discriminated Union` -> `可辨识联合`
  - `Exhaustiveness checking` -> `穷尽性检查`

---

## Directory Conventions

```
doc-bilingual-translator/
├── SKILL.md                         # 本技能说明文档
├── .gitignore                       # 忽略 dev/evals/results/ 和 __pycache__
├── scripts/                         # 生产运行时脚本
│   └── validate_bi_markdown.py      # 双语 Markdown 格式/排版校验
└── dev/                             # 开发者工具（skill 评估用）
    ├── eval_runner.py               # 对比评估脚本
    └── evals/                       # 评估基础设施
        ├── evals.json               # 评估元数据
        ├── test_cases/              # 英文源文档
        │   └── <chapter>.md
        ├── glossaries/              # 各章节术语表
        │   └── <chapter>.json
        └── results/                 # 每次 eval 运行产物（gitignored）
            └── <chapter>/
                ├── baseline.bi.md
                ├── latest.bi.md
                └── comparison.html
```
