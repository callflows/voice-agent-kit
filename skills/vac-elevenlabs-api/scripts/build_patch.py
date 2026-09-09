#!/usr/bin/env python3
"""
No-clobber PATCH payload builder

Builds a safe PATCH payload for update_agent.py by pulling the complete
prompt block from the LIVE config and replacing only the prompt text.
That way built_in_tools, knowledge_base and rag are guaranteed to survive —
the most common and most expensive failure mode of hand-written PATCHes.

The prompt text comes from prompt.md: what counts is the content of the
"## Prompt (English)" section (same convention as apply_settings.py).

Usage:
    python3 build_patch.py <agent_id> --prompt <prompt.md> --out <patch.json>
    python3 build_patch.py <agent_id> --prompt-text "raw text" --out <patch.json>

Then:  python3 update_agent.py <agent_id> <patch.json>   (dry run)
       python3 update_agent.py <agent_id> <patch.json> --confirm
"""

import os
import re
import sys
import json
import argparse
import urllib.request
import urllib.error

API_BASE = os.environ.get("ELEVENLABS_API_BASE", "https://api.eu.residency.elevenlabs.io")
API_KEY = os.environ.get("ELEVENLABS_API_KEY")

if not API_KEY:
    print("ERROR: ELEVENLABS_API_KEY environment variable not set", file=sys.stderr)
    sys.exit(1)


def get_agent(agent_id: str) -> dict:
    url = f"{API_BASE}/v1/convai/agents/{agent_id}"
    req = urllib.request.Request(url, headers={"xi-api-key": API_KEY})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"ERROR: could not fetch agent (API {e.code})", file=sys.stderr)
        print(e.read().decode('utf-8'), file=sys.stderr)
        sys.exit(1)


def extract_prompt_text(prompt_md_path: str) -> str:
    """Extracts the '## Prompt (English)' section from prompt.md."""
    try:
        with open(prompt_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except OSError as e:
        print(f"ERROR: cannot read prompt.md: {prompt_md_path} ({e.strerror})", file=sys.stderr)
        sys.exit(1)
    m = re.search(r"^## Prompt \(English\)\s*\n(.*?)(?=^## |\Z)", content, re.M | re.S)
    if not m:
        print("ERROR: section '## Prompt (English)' not found in prompt.md.", file=sys.stderr)
        sys.exit(1)
    text = m.group(1).strip()
    if len(text) < 500:
        print(f"ERROR: extracted prompt suspiciously short ({len(text)} chars) — wrong section?", file=sys.stderr)
        sys.exit(1)
    return text


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("agent_id")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--prompt", help="path to prompt.md (the '## Prompt (English)' section is used)")
    src.add_argument("--prompt-text", help="raw prompt text, passed directly")
    ap.add_argument("--out", required=True, help="target file for the PATCH payload")
    args = ap.parse_args()

    new_text = extract_prompt_text(args.prompt) if args.prompt else args.prompt_text

    agent = get_agent(args.agent_id)
    live_prompt_block = (agent.get("conversation_config", {})
                         .get("agent", {})
                         .get("prompt"))
    if not isinstance(live_prompt_block, dict):
        print("ERROR: live config contains no prompt block — check the agent ID.", file=sys.stderr)
        sys.exit(1)

    old_len = len(live_prompt_block.get("prompt", ""))
    live_prompt_block["prompt"] = new_text

    payload = {"conversation_config": {"agent": {"prompt": live_prompt_block}}}
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    preserved = [k for k in ("built_in_tools", "knowledge_base", "rag") if k in live_prompt_block]
    print(f"✓ PATCH payload written: {args.out}")
    print(f"  Agent:           \"{agent.get('name', '?')}\" ({args.agent_id})")
    print(f"  Prompt:          {old_len} → {len(new_text)} chars")
    print(f"  Preserved (live): {', '.join(preserved) if preserved else 'no extra fields in the live block'}")
    print(f"  Next step:       python3 update_agent.py {args.agent_id} {args.out}   (dry run first)")
