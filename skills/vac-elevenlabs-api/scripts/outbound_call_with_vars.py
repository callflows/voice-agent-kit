#!/usr/bin/env python3
"""
ElevenLabs Outbound Call WITH Dynamic Variables (mandatory).

Fetches the agent's dynamic_variable_placeholders from the API,
merges with optional overrides, and triggers the call.

This ensures ALL variables are always passed — no more missing variable errors.

Safety gate: without --confirm the script only prints the target number and the
variables (dry run) and places NO call. An outbound call reaches a real person and
costs money — so always check the target number deliberately before executing.

Usage:
  python3 outbound_call_with_vars.py <agent_id> <phone_number_id> <to_number> [overrides_json]            # dry run
  python3 outbound_call_with_vars.py <agent_id> <phone_number_id> <to_number> [overrides_json] --confirm  # places the call

  overrides_json: Optional JSON string to override specific default values.
                  All other variables keep their defaults from the agent config.

Example:
  python3 outbound_call_with_vars.py agent_xxx phnum_xxx +49176... '{"call_ansprechpartner":"Herr Müller"}' --confirm
"""

import os
import sys
import json
import urllib.request
import urllib.error

API_BASE = os.environ.get("ELEVENLABS_API_BASE", "https://api.eu.residency.elevenlabs.io")
API_KEY = os.environ.get("ELEVENLABS_API_KEY")

def get_agent_variables(agent_id):
    """Fetch dynamic_variable_placeholders from agent config."""
    url = f"{API_BASE}/v1/convai/agents/{agent_id}"
    req = urllib.request.Request(url, headers={
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            placeholders = (data
                .get("conversation_config", {})
                .get("agent", {})
                .get("dynamic_variables", {})
                .get("dynamic_variable_placeholders", {}))
            return placeholders
    except urllib.error.HTTPError as e:
        print(f"✗ Failed to fetch agent config: {e.code} {e.read().decode()[:200]}", file=sys.stderr)
        sys.exit(1)

def trigger_outbound_call(agent_id, phone_number_id, to_number, dynamic_variables):
    """Trigger outbound call with ALL dynamic variables."""
    url = f"{API_BASE}/v1/convai/twilio/outbound-call"
    
    payload = {
        "agent_id": agent_id,
        "agent_phone_number_id": phone_number_id,
        "to_number": to_number,
        "conversation_initiation_client_data": {
            "dynamic_variables": dynamic_variables
        }
    }
    
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, headers={
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    })
    
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            print(f"\n✓ Call triggered successfully")
            print(f"  Conversation ID: {result.get('conversation_id', '?')}")
            print(f"  Call SID: {result.get('callSid', '?')}")
            print(f"  Variables sent: {len(dynamic_variables)} ({', '.join(dynamic_variables.keys())})")
            print(json.dumps(result, indent=2))
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"\n✗ Call failed: {e.code}", file=sys.stderr)
        print(error_body, file=sys.stderr)
        sys.exit(1)

def main():
    args = [a for a in sys.argv[1:] if a != "--confirm"]
    confirm = "--confirm" in sys.argv[1:]

    if len(args) < 3:
        print("Usage: outbound_call_with_vars.py <agent_id> <phone_number_id> <to_number> [overrides_json] [--confirm]")
        print("\nFetches ALL dynamic variables from agent config, merges with overrides, triggers call.")
        print("Without --confirm: dry run (shows number + variables, places no call).")
        sys.exit(1)

    if not API_KEY:
        print("Error: ELEVENLABS_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    agent_id = args[0]
    phone_number_id = args[1]
    to_number = args[2]

    # Parse optional overrides
    overrides = {}
    if len(args) >= 4:
        try:
            overrides = json.loads(args[3])
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON for overrides: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Step 1: Fetch ALL variable defaults from agent config
    print(f"Fetching dynamic variables from agent {agent_id}...")
    defaults = get_agent_variables(agent_id)
    
    if not defaults:
        print("⚠ WARNING: No dynamic_variable_placeholders found in agent config!", file=sys.stderr)
        print("  The agent may not use dynamic variables, or they weren't set during creation.", file=sys.stderr)
        if not overrides:
            print("  No overrides provided either. Proceeding without variables.", file=sys.stderr)
    
    # Step 2: Merge defaults with overrides (overrides win)
    final_vars = {**defaults, **overrides}
    
    print(f"Variables to send ({len(final_vars)}):")
    for k, v in final_vars.items():
        source = "override" if k in overrides else "default"
        print(f"  {k}: {v} ({source})")
    
    # Step 3: gate, then call
    if not confirm:
        print(f"\nDRY RUN — this call WOULD go out RIGHT NOW:")
        print(f"  Agent:         {agent_id}")
        print(f"  Target number: {to_number}")
        print("No call placed. To execute: append --confirm.")
        print("→ Check the target number deliberately first — real person, real cost.")
        sys.exit(2)

    trigger_outbound_call(agent_id, phone_number_id, to_number, final_vars)

if __name__ == "__main__":
    main()
