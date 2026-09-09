#!/usr/bin/env python3
"""
VAC Settings Applier — applies the agent-independent settings baseline at deploy time.

Reads settings-baseline.json + settings-{usecase}.json (overlay) and combines them
deterministically with the agent-specific config. ONE PATCH/create sets both
conversation_config and platform_settings (empirically verified 2026-06-04).

Modes:
  build   <outbound|inbound> <config.json> --prompt <prompt.md> --voice <voice_id> [--out <file>]
          -> builds a ready-to-use .deploy-config.json for POST /create
  apply   <outbound|inbound> <agent_id>
          -> brings an EXISTING agent up to standard (GET + selective merge + PATCH),
             without losing prompt/voice/variables
  verify  <outbound|inbound> <agent_id>
          -> GET + expected/actual report against baseline+overlay (exit 1 on deviation)

ENV: ELEVENLABS_API_KEY. Optional ELEVENLABS_API_BASE (default: EU Residency).
"""
import os, sys, json, re, argparse, urllib.request, urllib.error

BASE = "https://api.eu.residency.elevenlabs.io"
SETTINGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "settings")


def _key():
    k = os.environ.get("ELEVENLABS_API_KEY")
    if not k:
        sys.exit("ERROR: ELEVENLABS_API_KEY not set (source .env)")
    return k


def api(method, path, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        BASE + path, data=data, method=method,
        headers={"xi-api-key": _key(), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, (json.loads(r.read()) if r.status != 204 else {})
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {}


def deep_merge(base, over):
    """Recursive merge. over wins. Lists are replaced, not concatenated.
    Does not strip None keys from over (None is a valid value, e.g. to disable a tool)."""
    if not isinstance(base, dict) or not isinstance(over, dict):
        return over
    out = dict(base)
    for k, v in over.items():
        out[k] = deep_merge(base[k], v) if (k in base and isinstance(v, dict)) else v
    return out


def strip_comments(d):
    """Removes _comment keys recursively (documentation in the JSONs, not for the API)."""
    if isinstance(d, dict):
        return {k: strip_comments(v) for k, v in d.items() if k != "_comment"}
    if isinstance(d, list):
        return [strip_comments(x) for x in d]
    return d


def load_settings(usecase):
    if usecase not in ("outbound", "inbound"):
        sys.exit(f"ERROR: usecase must be 'outbound' or 'inbound', got '{usecase}'")
    with open(os.path.join(SETTINGS_DIR, "settings-baseline.json"), encoding="utf-8") as f:
        baseline = strip_comments(json.load(f))
    with open(os.path.join(SETTINGS_DIR, f"settings-{usecase}.json"), encoding="utf-8") as f:
        overlay = strip_comments(json.load(f))
    return deep_merge(baseline, overlay)


def extract_prompt(prompt_md_path):
    with open(prompt_md_path, encoding="utf-8") as f:
        md = f.read()
    m = re.search(r"## Prompt \(English\)\s*\n(.+)\Z", md, re.DOTALL)
    if not m:
        sys.exit("ERROR: '## Prompt (English)' section not found in prompt.md")
    return m.group(1).strip()


# ---- build: ready-to-use deploy config for a NEW agent ----
def cmd_build(args):
    settings = load_settings(args.usecase)
    with open(args.config, encoding="utf-8") as f:
        content = strip_comments(json.load(f))
    # Settings win over the content config (central control of the technical settings)
    final = deep_merge(content, settings)
    # Inject prompt + voice
    final.setdefault("conversation_config", {}).setdefault("agent", {}).setdefault("prompt", {})
    final["conversation_config"]["agent"]["prompt"]["prompt"] = extract_prompt(args.prompt)
    final["conversation_config"].setdefault("tts", {})["voice_id"] = args.voice
    out = args.out or ".deploy-config.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)
    print(f"Wrote {out} ({len(json.dumps(final))} bytes). Deploy via create_agent.py.")


# ---- apply: bring an EXISTING agent up to standard (non-destructive) ----
SUBTREES_CC = ["asr", "turn", "conversation", "tts"]


def cmd_apply(args):
    settings = load_settings(args.usecase)
    scc, sps = settings["conversation_config"], settings["platform_settings"]
    st, agent = api("GET", f"/v1/convai/agents/{args.agent_id}")
    if st != 200:
        sys.exit(f"ERROR: GET {st}: {json.dumps(agent)[:400]}")
    cc, ps = agent["conversation_config"], agent["platform_settings"]

    patch_cc = {}
    for key in SUBTREES_CC:
        if key in scc:
            patch_cc[key] = deep_merge(cc.get(key, {}), scc[key])
    # agent.prompt: keep the existing prompt/voice/vars, overlay the settings.
    # Drop the tools array -> it is regenerated server-side from built_in_tools.
    prompt_merged = deep_merge(cc["agent"]["prompt"], scc["agent"]["prompt"])
    prompt_merged.pop("tools", None)
    # Neutralise the reasoning fields when the existing agent switches LLM. The baseline runs
    # without reasoning (reasoning_effort/thinking_budget = null) -> otherwise API 400.
    # PATCH merges server-side: omitted fields stay as they are -> set them to None explicitly.
    if cc["agent"]["prompt"].get("llm") != scc["agent"]["prompt"].get("llm"):
        for f in ("reasoning_effort", "thinking_budget"):
            if f in prompt_merged:
                prompt_merged[f] = None
    patch_cc["agent"] = {"prompt": prompt_merged}

    patch_ps = {}
    for key in ("guardrails", "workspace_overrides", "call_limits",
                "data_collection", "data_collection_scopes", "summary_language"):
        if key in sps:
            patch_ps[key] = deep_merge(ps.get(key, {}) or {}, sps[key])

    body = {"conversation_config": patch_cc, "platform_settings": patch_ps}
    st, resp = api("PATCH", f"/v1/convai/agents/{args.agent_id}", body)
    if st != 200:
        sys.exit(f"ERROR: PATCH {st}: {json.dumps(resp)[:600]}")
    print(f"PATCH HTTP 200 — {args.agent_id} brought up to the {args.usecase} standard.")
    cmd_verify(args)


# ---- verify: expected/actual against baseline+overlay ----
def cmd_verify(args):
    settings = load_settings(args.usecase)
    st, a = api("GET", f"/v1/convai/agents/{args.agent_id}")
    if st != 200:
        sys.exit(f"ERROR: GET {st}")
    cc, ps = a["conversation_config"], a["platform_settings"]
    p = cc["agent"]["prompt"]
    bt = p.get("built_in_tools", {})
    stc = cc["turn"]["soft_timeout_config"]
    cs = (ps.get("data_collection") or {}).get("call_summary") or {}
    cs_scope = (ps.get("data_collection_scopes") or {}).get("call_summary")
    # Expected values come from the baseline, not from literals — otherwise the
    # baseline and this check drift apart the moment someone edits the baseline.
    sp = settings["conversation_config"]["agent"]["prompt"]
    sps = settings["platform_settings"]
    exp_tools = ["end_call", "skip_turn"] + (["voicemail_detection"] if args.usecase == "outbound" else [])
    checks = [
        ("llm", p.get("llm"), sp["llm"]),
        ("temperature", p.get("temperature"), sp["temperature"]),
        ("max_tokens", p.get("max_tokens"), -1),
        ("enable_reasoning_summary", p.get("enable_reasoning_summary"), False),
        ("reasoning_effort", p.get("reasoning_effort"), None),
        ("thinking_budget", p.get("thinking_budget"), None),
        ("timezone", p.get("timezone"), sp["timezone"]),
        ("turn_model", cc["turn"].get("turn_model"), "turn_v3"),
        ("turn_eagerness", cc["turn"].get("turn_eagerness"), settings["conversation_config"]["turn"]["turn_eagerness"]),
        ("speculative_turn", cc["turn"].get("speculative_turn"), True),
        ("soft_timeout override", bool(stc.get("llm_generated_message_prompt_override")), True),
        ("file_input.enabled", cc["conversation"]["file_input"]["enabled"], False),
        ("asr.provider", cc["asr"].get("provider"), "scribe_realtime"),
        ("tts.model_id", cc["tts"].get("model_id"), "eleven_v3_conversational"),
        ("built_in_tools", sorted([k for k, v in bt.items() if v]), sorted(exp_tools)),
        ("guardrails.focus", ps["guardrails"]["focus"]["is_enabled"], True),
        ("guardrails.prompt_injection", ps["guardrails"]["prompt_injection"]["is_enabled"], True),
        ("bursting_enabled", ps["call_limits"]["bursting_enabled"], False),
        ("summary_language", ps.get("summary_language"), sps["summary_language"]),
        ("call_summary present", bool(cs.get("description")), True),
        ("call_summary llm", cs.get("llm"), "gemini-2.5-flash"),
        ("call_summary scope", cs_scope, "conversation"),
]
    ok = True
    print(f"\n=== VERIFY {args.agent_id} ({args.usecase}) ===")
    for name, got, exp in checks:
        good = got == exp
        ok = ok and good
        print(f"[{'OK ' if good else 'XX '}] {name}: {got}" + ("" if good else f"  (expected: {exp})"))
    if not ok:
        sys.exit("\nVERIFY FAILED")
    print("\nVERIFY PASSED")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build"); b.add_argument("usecase"); b.add_argument("config")
    b.add_argument("--prompt", required=True); b.add_argument("--voice", required=True); b.add_argument("--out")
    b.set_defaults(func=cmd_build)
    ap2 = sub.add_parser("apply"); ap2.add_argument("usecase"); ap2.add_argument("agent_id"); ap2.set_defaults(func=cmd_apply)
    v = sub.add_parser("verify"); v.add_argument("usecase"); v.add_argument("agent_id"); v.set_defaults(func=cmd_verify)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
