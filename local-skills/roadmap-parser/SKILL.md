---
name: roadmap-parser
description: Fetches, parses, and decodes any roadmap from roadmap.sh (such as /linux, /backend, /frontend, etc.) using their underlying React Router stream (devalue) data structures, formatting them into structured lists of main nodes and their branches in Chinese. Trigger this skill whenever a user mentions roadmap.sh, requests a roadmap's outline, text version, node hierarchy, or wants a structured breakdown of a roadmap.
---

# Roadmap Parser Skill

A skill for parsing any interactive roadmap from `roadmap.sh` and exporting its complete node hierarchy, including main nodes (topics) and branches (subtopics) with optional Chinese translations.

## Setup & Compatibility

This skill requires:
- Python 3
- Network connectivity to fetch `roadmap.sh` pages (or access to local HTML page dumps).

The core parsing script is bundled at `scripts/parse_roadmap.py`.

## How to Use

When the user asks you to parse or fetch a roadmap from `roadmap.sh` (e.g., `https://roadmap.sh/backend` or simply the slug `backend`):

1. **Verify Python Script Location**:
   The script is located at `[parse_roadmap.py](file:///home/zaviro/workspace/play/localskills/roadmap-parser/scripts/parse_roadmap.py)`. Ensure it is executable.

2. **Execute the Script**:
   Run the python script from your terminal using `run_command` with the URL, slug, or a local HTML file.
   
   **Examples:**
   ```bash
   python3 /home/zaviro/workspace/play/localskills/roadmap-parser/scripts/parse_roadmap.py backend
   python3 /home/zaviro/workspace/play/localskills/roadmap-parser/scripts/parse_roadmap.py https://roadmap.sh/frontend
   ```

3. **Format the Output**:
   The script will print the structured roadmap in markdown with:
   - A numbered list of all core topics (main nodes).
   - An itemized sub-list of all subtopics (branches) clustered near each core topic.
   - Translations of common developer/computer terms to Chinese where available.

4. **Return Results to User**:
   Provide the parsed text version directly to the user as requested.

## Parsing Rationale (Under the Hood)
`roadmap.sh` roadmaps are visual flowcharts rendered via React Flow. The web application is built on Remix / React Router. 
The complete nodes, edges, and positions data are streamed to the client and embedded in the HTML body within a `<script>` tag initializing:
`window.__reactRouterContext.streamController.enqueue(...)`

This data is encoded using the `devalue`/`turbo-stream` serialization format. The Python script:
1. Regex-matches the data stream from the page's raw HTML.
2. Recursively decodes indices and pointers in the `devalue` list to reconstruct the original `roadmap.nodes` and `roadmap.edges` structures.
3. Groups each `subtopic` node to its nearest `topic` node using 2D grid coordinates (Y-axis distance is weighted higher to align with visual columns).
