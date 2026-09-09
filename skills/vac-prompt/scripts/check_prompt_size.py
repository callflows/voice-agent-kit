#!/usr/bin/env python3
"""
Prompt size check (latency budget)

Checks the agent prompt length against the latency budget from vac-prompt:
- up to 10,000 characters: green (simple agents)
- 10,000-15,000: green for engaged agents with an answer bank
- 15,000-18,000: yellow - still deployable, keep an eye on latency
- over 18,000: red - latency suffers noticeably; cut it down or move content to the knowledge base

Accepts prompt.md (uses the '## Prompt (English)' section) or a plain text file.

Usage:
    python3 check_prompt_size.py <prompt.md>

Exit 0 = green/yellow, exit 1 = red (>18,000).
"""

import re
import sys

if len(sys.argv) < 2:
    print("Usage: python3 check_prompt_size.py <prompt.md>")
    sys.exit(1)

try:
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        content = f.read()
except OSError as e:
    print(f"[ERROR] Cannot read file: {sys.argv[1]} ({e.strerror})", file=sys.stderr)
    sys.exit(1)

# IMPORTANT: identical to extract_prompt() in vac-deploy/scripts/apply_settings.py.
# The prompt body contains "## " subsections itself - a lookahead on those
# would measure less here than what is deployed later.
m = re.search(r"## Prompt \(English\)\s*\n(.+)\Z", content, re.S)
text = m.group(1).strip() if m else content.strip()
n = len(text)

print(f"Prompt length: {n:,} characters")

if n > 18000:
    print("[RED] Over the 18,000-character budget - the agent will answer noticeably slower.")
    print("→ Cut it down: tighten the answer bank, move stable facts to the knowledge base (vac-knowledge-base).")
    sys.exit(1)
elif n > 15000:
    print("[YELLOW] 15,000-18,000 characters - deployable, but at the upper edge. On latency feedback, cut here first.")
elif n > 10000:
    print("[GREEN] Normal for engaged agents with an answer bank (13,000-17,000 is typical).")
else:
    print("[GREEN] Compact - good for simple agents.")
sys.exit(0)
