#!/usr/bin/env python3
"""
ElevenLabs ConvAI Agent Update Script
Updates an existing agent via API (PATCH).

Safety gates:
1. Without --confirm it is a dry run only: shows the agent name and the fields to be
   patched, patches nothing.
2. No-clobber check: if the payload contains a prompt block WITH "prompt" text but
   WITHOUT "built_in_tools", the PATCH wipes the system tools server-side
   (end_call, voicemail_detection, transfer_to_agent) and possibly knowledge_base/rag.
   The script blocks that case unless --allow-clobber is set explicitly.
   The safe route: build the payload from the live config with build_patch.py.

Usage:
    python3 update_agent.py <agent_id> <updates.json>            # dry run
    python3 update_agent.py <agent_id> <updates.json> --confirm  # patches LIVE
"""

import os
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


def top_level_paths(obj: dict, prefix: str = "", depth: int = 3) -> list:
    """Flat path list of the fields that are set, for the dry run output."""
    paths = []
    for k, v in obj.items():
        p = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict) and depth > 1 and v:
            paths.extend(top_level_paths(v, p, depth - 1))
        else:
            paths.append(p)
    return paths


def clobber_risk(updates: dict) -> bool:
    """True if the prompt block replaces text but built_in_tools is missing."""
    prompt_block = (updates.get("conversation_config", {})
                    .get("agent", {})
                    .get("prompt"))
    if not isinstance(prompt_block, dict):
        return False
    return "prompt" in prompt_block and "built_in_tools" not in prompt_block


def update_agent(agent_id: str, updates: dict) -> dict:
    url = f"{API_BASE}/v1/convai/agents/{agent_id}"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    data = json.dumps(updates).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='PATCH')
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"ERROR: API returned {e.code}", file=sys.stderr)
        print(e.read().decode('utf-8'), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("agent_id")
    ap.add_argument("updates_file")
    ap.add_argument("--confirm", action="store_true", help="Actually runs the LIVE PATCH")
    ap.add_argument("--allow-clobber", action="store_true",
                    help="Allows a prompt block without built_in_tools (WIPES the system tools!)")
    args = ap.parse_args()

    if not os.path.exists(args.updates_file):
        print(f"ERROR: Updates file not found: {args.updates_file}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.updates_file, 'r', encoding='utf-8') as f:
            updates = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: {args.updates_file} is not valid JSON ({e}). "
              f"Rebuild the payload (e.g. with build_patch.py).", file=sys.stderr)
        sys.exit(1)

    if clobber_risk(updates) and not args.allow_clobber:
        print("BLOCKED (no-clobber check): the payload replaces the prompt block but carries", file=sys.stderr)
        print("no built_in_tools. The PATCH would wipe end_call/voicemail_detection/transfer_to_agent", file=sys.stderr)
        print("and possibly knowledge_base/rag from the live agent.", file=sys.stderr)
        print("→ Safe route: build the payload from the live config with build_patch.py.", file=sys.stderr)
        print("→ Only if that wipe is intended: set --allow-clobber.", file=sys.stderr)
        sys.exit(1)

    agent = get_agent(args.agent_id)
    live_name = agent.get("name", "?")

    if not args.confirm:
        print(f"DRY RUN — LIVE PATCH on agent \"{live_name}\" ({args.agent_id}):")
        for p in top_level_paths(updates):
            print(f"  would be set: {p}")
        print(f"\nNot patched. To execute: append --confirm.")
        print("→ ALWAYS obtain the user's explicit confirmation first.")
        sys.exit(2)

    result = update_agent(args.agent_id, updates)
    print(json.dumps(result, indent=2))
