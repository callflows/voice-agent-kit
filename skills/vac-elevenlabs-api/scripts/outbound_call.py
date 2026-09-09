#!/usr/bin/env python3
"""
ElevenLabs ConvAI Outbound Call Script
Triggers an outbound call via Twilio integration.
"""

import os
import sys
import json
import urllib.request
import urllib.error

API_BASE = os.environ.get("ELEVENLABS_API_BASE", "https://api.eu.residency.elevenlabs.io")
API_KEY = os.environ.get("ELEVENLABS_API_KEY")

if not API_KEY:
    print("ERROR: ELEVENLABS_API_KEY environment variable not set", file=sys.stderr)
    sys.exit(1)


def trigger_outbound_call(agent_id: str, phone_number_id: str, to_number: str, dynamic_variables: dict = None) -> dict:
    """
    Trigger an outbound call.
    
    Args:
        agent_id: Agent ID to use for the call
        phone_number_id: Phone number ID to call from
        to_number: Target phone number (E.164 format, e.g. +49XXXXXXXXXXX)
        dynamic_variables: Optional dict of dynamic variables for the agent's first_message and prompt
        
    Returns:
        dict: API response with conversation_id and callSid
    """
    url = f"{API_BASE}/v1/convai/twilio/outbound-call"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "agent_id": agent_id,
        "agent_phone_number_id": phone_number_id,
        "to_number": to_number
    }
    
    if dynamic_variables:
        payload["conversation_initiation_client_data"] = {
            "dynamic_variables": dynamic_variables
        }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"ERROR: API returned {e.code}", file=sys.stderr)
        print(e.read().decode('utf-8'), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 outbound_call.py <agent_id> <phone_number_id> <to_number> [dynamic_variables_json]")
        print("\nExample:")
        print("  python3 outbound_call.py agent_xxx phnum_xxx +49XXXXXXXXXXX")
        print("  python3 outbound_call.py agent_xxx phnum_xxx +49XXXXXXXXXXX '{\"firma_name\":\"ACME\",\"call_ansprechpartner\":\"Herr Mueller\"}'")
        sys.exit(1)
    
    agent_id = sys.argv[1]
    phone_number_id = sys.argv[2]
    to_number = sys.argv[3]
    
    dynamic_vars = None
    if len(sys.argv) > 4:
        try:
            dynamic_vars = json.loads(sys.argv[4])
        except json.JSONDecodeError:
            print(f"ERROR: Invalid JSON for dynamic_variables: {sys.argv[4]}", file=sys.stderr)
            sys.exit(1)
    
    result = trigger_outbound_call(agent_id, phone_number_id, to_number, dynamic_vars)
    
    print(json.dumps(result, indent=2))
    
    if result.get('success'):
        print(f"\n✓ Call triggered successfully", file=sys.stderr)
        print(f"  Conversation ID: {result.get('conversation_id')}", file=sys.stderr)
        print(f"  Call SID: {result.get('callSid')}", file=sys.stderr)
    else:
        print(f"\n✗ Call failed", file=sys.stderr)
        sys.exit(1)
