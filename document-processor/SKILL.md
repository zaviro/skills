---
name: document-processor
description: >
  Process, clean, and reconstruct EPUB/TXT documents using LLM-guided editing.
  Handles ad removal, OCR typo correction, illustration preservation, and format conversion.
  Trigger when the user wants to clean a book, fix typos, remove ads, or reformat a document to clean EPUB/TXT.
---

# Document Processor

将 EPUB/TXT 文档转换为 Markdown 中间格式，由单一 Agent（LLM）在同一个会话中逐页阅读，并通过局部替换（Patch/Diff）方式进行智能编辑（去广告、OCR 纠错、插图处理），最终打包为干净的 EPUB 或 TXT。

## 核心原则

1. **Markdown 为中间格式**：所有内容先转为 Markdown，方便 LLM 理解和编辑。
2. **单一代理，全局一致**：为保证人名、地名、场景名等专有名词在全书中的绝对一致，禁止并行子代理。必须由单一 LLM 会话顺序阅读和校对全文。
3. **局部差异修改（Patch）**：为规避输出 Token 限制，禁止输出并覆盖整个页面文件。必须使用 `replace_file_content` 或 `multi_replace_file_content` 工具仅对有错误的行进行定向行替换。
4. **零外部依赖**：所有脚本仅使用 Python 标准库。
5. **输出隔离**：最终产物输出至 `./outputs/document-processor/`。

---

## 流程

### Step 1: 内容提取

```bash
python3 scripts/extract_content.py <input_file> <output_dir>
```

- **EPUB**：解析 OPF spine，按阅读顺序提取文本为 Markdown，提取图片资源。
- **TXT/HTML**：读取并按固定大小分页。

输出：
- `<output_dir>/extracted/pages/page_XXXX.txt` — 分页 Markdown
- `<output_dir>/extracted/images/` — 提取的图片
- `<output_dir>/extracted/raw_text.txt` — 合并的未修改全文（用于校验对比）
- `<output_dir>/extracted/manifest.json` — 提取元数据

---

### Step 2: 初始化精修工作区与全局规则

在进行编辑前，执行初始化准备：
1. 创建精修工作区，将提取内容复制为精修基准：
   ```bash
   mkdir -p <output_dir>/refined/pages <output_dir>/refined/images
   cp -r <output_dir>/extracted/pages/* <output_dir>/refined/pages/
   cp -r <output_dir>/extracted/images/* <output_dir>/refined/images/
   cp <output_dir>/extracted/manifest.json <output_dir>/refined/refined_manifest.json
   ```
2. **分析文档并制定规则**：主代理阅读部分提取出的页面，动态提炼出该书的 OCR 识别特征、垃圾广告水印模式，并在当前会话中建立全局“人名/地名术语对齐表”（Glossary）。

---

### Step 3: 单一代理滚动局部校对

**⚠️ 强制要求：必须由单一 LLM 实例（同一个会话）顺序读取并修改所有页面。严禁重写全文件，必须使用局部替换工具（如 replace_file_content 或 multi_replace_file_content）仅对有错字的行进行定向修改。**

执行流程：
1. 保持同一个 LLM 会话，依次对 `<output_dir>/refined/pages/` 下的每一个 `page_XXXX.txt`：
   - 使用 `view_file` 完整读入该页内容（大页面可分批读入）。
   - 发现错字、格式或广告问题时，精确定位有错误的行。
   - 使用 `replace_file_content` 或 `multi_replace_file_content`，**只将有错误的行替换为修改后的行**。
   - 这样每次操作只需输出几十个 Token 的差异块，不仅处理极快，还能彻底规避生成超限错误。
   - 在处理后文时，严格遵循在前文中已经做出的译名和修改决策，保证全局一致性。

---

### Step 4: 打包

```bash
python3 scripts/package_output.py --refined-dir <output_dir>/refined --format <epub|txt> --output <file>
```

- EPUB：标准 zipfile 打包，含 CSS、NCX 目录，每一物理行会被自动包装为独立的段落 `<p>` 标签。
- TXT：纯文本合并，插图标记为 `【插图位置：xxx】`。

---

### Step 5: 校验

```bash
python3 scripts/validate_book.py <output_file> --extracted-dir <output_dir>/extracted
```

校验项：文本留存率（与原始 raw_text.txt 的字数比对）、残留广告、段落拆分健康度（确保段落结尾标点规范率 > 94%）。

---

## 目录结构

```
document-processor/
├── SKILL.md
└── scripts/
    ├── extract_content.py    # 内容提取（标准库）
    ├── package_output.py     # EPUB/TXT 打包（标准库）
    └── validate_book.py      # 质量校验（标准库）
```

## 依赖

无。所有脚本仅依赖 Python 3.6+ 标准库。
