#!/usr/bin/env python3
"""
ElevenLabs ConvAI Conversation Transcript Fetcher

Pulls real conversation transcripts for an agent as evidence BEFORE a prompt is
changed (vac-update step 1). Lists the last N conversations and prints their
transcripts plus metadata.

Usage:
    python3 fetch_transcripts.py <agent_id> [--limit N] [--out FILE] [--full]

    --limit N   number of most recent conversations (default 10)
    --out FILE  write to a file instead of stdout (e.g. transcripts-evidence.md)
    --full      raw JSON per conversation instead of compact Markdown

ENV: ELEVENLABS_API_KEY must be set.
"""

import os
import sys
import json
import argparse
import urllib.parse
import urllib.request
import urllib.error

API_BASE = os.environ.get("ELEVENLABS_API_BASE", "https://api.eu.residency.elevenlabs.io")
API_KEY = os.environ.get("ELEVENLABS_API_KEY")

if not API_KEY:
    print("ERROR: ELEVENLABS_API_KEY environment variable not set", file=sys.stderr)
    sys.exit(1)

HEADERS = {"xi-api-key": API_KEY}


def _get(path: str) -> dict:
    url = f"{API_BASE}{path}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"ERROR: API returned {e.code} for {path}", file=sys.stderr)
        print(e.read().decode("utf-8"), file=sys.stderr)
        sys.exit(1)


def list_conversations(agent_id: str, limit: int) -> list:
    """The agent's most recent conversations (newest first)."""
    q = urllib.parse.urlencode({"agent_id": agent_id, "page_size": limit})
    data = _get(f"/v1/convai/conversations?{q}")
    return data.get("conversations", [])[:limit]


def get_conversation(conversation_id: str) -> dict:
    return _get(f"/v1/convai/conversations/{conversation_id}")


def render_markdown(agent_id: str, convs: list) -> str:
    lines = [f"# Transcript evidence — agent `{agent_id}`", ""]
    lines.append(f"{len(convs)} conversations (newest first).")
    lines.append("")
    for i, meta in enumerate(convs, 1):
        cid = meta.get("conversation_id", "?")
        detail = get_conversation(cid)
        dur = meta.get("call_duration_secs", "?")
        status = meta.get("status", "?")
        success = meta.get("call_successful", detail.get("analysis", {}).get("call_successful", "?"))
        msgs = meta.get("message_count", "?")
        lines.append(f"## {i}. Conversation `{cid}`")
        lines.append(f"- Duration: {dur}s · Status: {status} · Success: {success} · Turns: {msgs}")
        summary = (detail.get("analysis") or {}).get("transcript_summary")
        if summary:
            lines.append(f"- Summary: {summary}")
        lines.append("")
        lines.append("```transcript")
        for turn in detail.get("transcript", []):
            role = turn.get("role", "?")
            text = (turn.get("message") or "").strip()
            if text:
                speaker = "AGENT" if role == "agent" else "USER "
                lines.append(f"{speaker}: {text}")
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("agent_id")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--out")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    convs = list_conversations(args.agent_id, args.limit)
    if not convs:
        print(f"No conversations found for agent {args.agent_id}.", file=sys.stderr)
        sys.exit(2)

    if args.full:
        out = json.dumps(
            [get_conversation(c["conversation_id"]) for c in convs], indent=2, ensure_ascii=False
        )
    else:
        out = render_markdown(args.agent_id, convs)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"{len(convs)} transcripts written to {args.out}", file=sys.stderr)
    else:
        print(out)


if __name__ == "__main__":
    main()
