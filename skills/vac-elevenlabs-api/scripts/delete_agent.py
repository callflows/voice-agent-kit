#!/usr/bin/env python3
"""
ElevenLabs ConvAI Agent Deletion Script
Deletes an agent via API. IRREVERSIBLE.

Safety gate: deleting requires --confirm-name with the exact agent name.
The script fetches the agent via GET first and compares the name, so a
mis-copied agent_id string cannot silently destroy the wrong agent.
Without the flag the script only shows WHAT would be deleted.

Usage:
    python3 delete_agent.py <agent_id>                          # shows the agent, deletes NOTHING
    python3 delete_agent.py <agent_id> --confirm-name "<name>"  # deletes (name must match exactly)
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


def delete_agent(agent_id: str) -> bool:
    url = f"{API_BASE}/v1/convai/agents/{agent_id}"
    req = urllib.request.Request(url, headers={"xi-api-key": API_KEY}, method='DELETE')
    try:
        with urllib.request.urlopen(req) as response:
            return response.status in [200, 204]
    except urllib.error.HTTPError as e:
        if e.code in [200, 204]:
            return True
        print(f"ERROR: API returned {e.code}", file=sys.stderr)
        print(e.read().decode('utf-8'), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("agent_id")
    ap.add_argument("--confirm-name", help="exact agent name, as deletion confirmation")
    args = ap.parse_args()

    agent = get_agent(args.agent_id)
    live_name = agent.get("name", "?")

    if not args.confirm_name:
        print(f"AGENT: \"{live_name}\" (id: {args.agent_id})")
        print("NOT deleted. Deletion is IRREVERSIBLE.")
        print(f"To delete: python3 delete_agent.py {args.agent_id} --confirm-name \"{live_name}\"")
        print("→ ALWAYS obtain the user's explicit confirmation first.")
        sys.exit(2)

    if args.confirm_name != live_name:
        print(f"ABORTED: --confirm-name \"{args.confirm_name}\" does not match the real name \"{live_name}\".", file=sys.stderr)
        sys.exit(1)

    if delete_agent(args.agent_id):
        print(f"✓ Agent \"{live_name}\" ({args.agent_id}) deleted (irreversible)")
