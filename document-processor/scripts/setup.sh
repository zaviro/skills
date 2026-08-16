#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# document-processor — Internal environment setup
#
# Creates a self-contained .venv INSIDE this skill directory.
# Nothing is installed into the global Python environment.
#
# Usage:
#   bash scripts/setup.sh           # mandatory: beautifulsoup4 + lxml
#   bash scripts/setup.sh --pdf     # also installs pdfplumber + pillow
# ─────────────────────────────────────────────────────────────────────────────
set -e
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$SKILL_DIR/.venv"

echo "→ Skill dir : $SKILL_DIR"
echo "→ Venv      : $VENV"

# Create venv if absent
if [ ! -d "$VENV" ]; then
    echo "→ Creating internal venv..."
    python3 -m venv "$VENV"
    # Bootstrap pip if missing (some distros ship venv without pip)
    "$VENV/bin/python" -m ensurepip --upgrade --default-pip 2>/dev/null || true
    if [ ! -f "$VENV/bin/pip" ] && [ ! -f "$VENV/bin/pip3" ]; then
        curl -sS https://bootstrap.pypa.io/get-pip.py | "$VENV/bin/python"
    fi
fi

PIP="$VENV/bin/python -m pip"

# Mandatory: beautifulsoup4 + lxml (tolerant XHTML parsing)
echo "→ Installing beautifulsoup4, lxml..."
$PIP install beautifulsoup4 lxml -q

# Optional PDF support
if [[ "${1:-}" == "--pdf" ]]; then
    echo "→ Installing pdfplumber, pillow (PDF support)..."
    $PIP install pdfplumber pillow -q
    echo "✓ PDF support enabled."
fi

echo ""
echo "✓ Setup complete."
echo "  Use: $VENV/bin/python scripts/<script>.py"
