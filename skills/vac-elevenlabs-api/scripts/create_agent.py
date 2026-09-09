#!/usr/bin/env python3
"""
ElevenLabs ConvAI Agent Creation Script
Creates a new conversational agent via API.

Safety gate: without --confirm the script only prints a summary of what would
go LIVE (dry run) and aborts. The deploy creates a production agent that costs
real money — so running it must be a deliberate decision, not a side effect.

Usage:
    python3 create_agent.py <config.json>            # dry run: shows what would happen
    python3 create_agent.py <config.json> --confirm  # deploys LIVE
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


def summarize(config: dict) -> str:
    """Compact summary of the deploy payload for the confirmation gate."""
    cc = config.get("conversation_config", {})
    agent = cc.get("agent", {})
    prompt = agent.get("prompt", {})
    tts = cc.get("tts", {})
    dyn = agent.get("dynamic_variables", {}).get("dynamic_variable_placeholders", {})
    lines = [
        f"  Name:            {config.get('name', '?')}",
        f"  Language:        {agent.get('language', '?')}",
        f"  first_message:   {json.dumps(agent.get('first_message', ''), ensure_ascii=False)}",
        f"  Voice ID:        {tts.get('voice_id', '?')}",
        f"  TTS model:       {tts.get('model_id', '?')}",
        f"  Prompt length:   {len(prompt.get('prompt', ''))} chars",
        f"  Dynamic vars:    {len(dyn)} ({', '.join(list(dyn)[:6])}{'…' if len(dyn) > 6 else ''})",
    ]
    return "\n".join(lines)


def create_agent(config: dict) -> dict:
    url = f"{API_BASE}/v1/convai/agents/create"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    data = json.dumps(config).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"ERROR: API returned {e.code}", file=sys.stderr)
        print(e.read().decode('utf-8'), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("config_file")
    ap.add_argument("--confirm", action="store_true", help="Actually runs the LIVE deploy")
    args = ap.parse_args()

    if not os.path.exists(args.config_file):
        print(f"ERROR: Config file not found: {args.config_file}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: {args.config_file} is not valid JSON ({e}). "
              f"Rebuild the deploy config (apply_settings.py build).", file=sys.stderr)
        sys.exit(1)

    if not args.confirm:
        print("DRY RUN — this agent WOULD be deployed LIVE on ElevenLabs:")
        print(summarize(config))
        print(f"\nNOT deployed. To execute: python3 create_agent.py {args.config_file} --confirm")
        print("→ ALWAYS obtain the user's explicit confirmation first.")
        sys.exit(2)

    result = create_agent(config)
    print(json.dumps(result, indent=2))
