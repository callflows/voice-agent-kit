# Glossary

This document explains the terms around voice-agent building in plain language — for everyone without a technical background. Look things up here whenever you hit a word you cannot place while building or ordering a voice agent. The terms are sorted into three blocks: **Conversation** (what the agent does and says), **Technology** (what it is built with) and **Process** (how we build, deploy and sell).

---

## Conversation

**Voice Agent**
An AI caller or callee that holds a real conversation on the phone. It listens, understands and answers with a synthetic voice in real time. Example: an agent calls staffing agencies, introduces itself and qualifies whether there is interest in our offer.

**Prompt**
The complete written instruction the agent follows during the conversation. Who it is, what it wants, what it may never say, how it reacts to objections. Think of it as the script plus the stage directions. The more precise the prompt, the more reliable the agent.

**System prompt**
The foundational part of the prompt that the customer never hears but that governs everything. It holds the identity ("You are Lena, the digital assistant of …"), the conversation rules and the guardrails. In the VAC skill pack the prompt is written entirely in English (the language model works better with it), but the agent speaks German only.

**First Message / Opener**
The first sentence the agent opens the conversation with: greeting, name, company, reason for the call. Important: on **outbound** the first message is technically empty, because the person called says "Hallo?" (hello?) first. The agent then delivers its opener as a reply. On **inbound** the first message is set, because the agent should greet the caller immediately.

**Outbound vs. inbound**
Outbound = the agent actively calls someone (the classic sales call). Inbound = someone calls us and the agent picks up. The two cases work differently under the hood (first message and answering-machine detection, for instance), so it must always be clear which of the two is meant when building.

**Guardrail**
A hard rule the agent must not break under any circumstances. Examples: name no prices, disclose being an AI when asked directly, hang up immediately and politely on an opt-out. Guardrails outrank everything else, even when the conversation pulls in another direction.

**SPIN Selling**
A sales method that works towards the need through four question types: **S**ituation, **P**roblem, **I**mplication, **N**eed-Payoff. Instead of pitching straight away, the agent uses questions to get the other person to recognize their own need.

**Challenger Sale**
A sales approach in which the agent does not just ask politely but offers the other person a new perspective on their problem and respectfully challenges them. The opposite of the pure "relationship seller". Used when an agent should come across as advisory rather than merely interrogative.

**ARC Objection Handling (Acknowledge-Reframe-Continue)**
The pattern the agent uses to respond to objections: **Acknowledge** (recognize the objection rather than brushing it aside), **Reframe** (put it in a new light), **Continue** (carry the conversation on). Example objection "Wir haben sowas schon probiert" (we've already tried something like that): acknowledge it briefly, ask what exactly did not work, then address that specifically. In the prompt, ARC is always stated as an intent, never as a ready-made sentence (see Few-Shot).

**Task extraction**
The step after the call in which the concrete follow-up tasks are read out of the conversation automatically. Example: "callback agreed for Thursday" or "send email with information material". Every agent gets its own task-extraction prompt for this, which the campaign platform applies after the call.

**Transcript**
The word-for-word record of a conversation that took place. The basis for evaluation, for task extraction and for later improvements to the agent. When we adjust an existing agent, we always pull real transcripts instead of guessing what is going wrong.

---

## Technology

**ElevenLabs / 11labs**
The platform our voice agents run on. It supplies the voice (text-to-speech), the listening (speech recognition) and the conversation control. When we "deploy" an agent, it lands at ElevenLabs and can be reached by phone from there.

**LLM (Large Language Model)**
The language model that does "the thinking" for the agent: it understands what was said and formulates the reply. Without an LLM the agent would just be a voice without a mind.

**claude-haiku-4-5**
The specific language model currently behind our agents. It is fast and handles longer prompts without noticeable delay, which gives us a bit of headroom on prompt length.

**Voice ID**
The unique identifier of a particular voice at ElevenLabs. Every agent is assigned exactly one voice. Example: for two campaigns of the same customer we deliberately pick different voices so they can be told apart on the phone.

**agent_id**
The unique identifier of a fully deployed agent at ElevenLabs (looks like `agent_1001ks7…`). It is how the agent is addressed, tested and updated. On a successful deployment ElevenLabs returns it, and we record it in the file AGENT.md.

**Dynamic Variable / dynamic_variable_placeholders**
Placeholders in the prompt that are filled with real values per call, such as `{{lead_first_name}}` or `{{account_agent_name}}`. This lets a single prompt work for thousands of leads. Every placeholder needs a sensible default value (the `dynamic_variable_placeholder`) in case no real value is passed for a call. Example: if no first name is known, the agent asks openly instead of speaking an empty placeholder out loud.

**Knowledge Base (KB)**
An externalised body of knowledge the agent pulls answers from when needed. Useful when an agent has to answer many in-depth questions (examples, success figures, details on how something works) that would otherwise overload the prompt. Frequent standard answers stay in the prompt, the long remainder moves into the KB.

**RAG / RAG index (Retrieval-Augmented Generation)**
The procedure the agent uses to pick exactly the fitting text passages out of the knowledge base before answering. Simplified: on a question, the KB is searched for the most relevant sections and the agent formulates its answer from them. The **RAG index** is the pre-computed "search map" over the KB that makes this lookup fast. If the KB changes, the index has to be recomputed.

**turn_eagerness**
Sets how quickly the agent takes the floor when the other person pauses. **eager** = jumps in briskly (good for sales, where pace matters). **normal** = balanced. **patient** = waits longer (good for data capture, where the caller has to think). Everyday analogy: an impatient salesperson (eager) vs. a listening advisor (patient).

**soft_timeout**
The short wait (usually 2 to 3 seconds) after which the agent throws in a filler such as "Moment…" (one moment…) during silence, so no awkward pause arises. Without this setting the agent would sit there mute and the conversation feels dead.

**Latency / TTFB (Time To First Byte)**
The delay between "the other person stopped talking" and "the agent starts answering". The longer the prompt, the more the language model has to process and the more sluggishly the agent reacts. That is why we keep prompts as short as possible and move depth into the knowledge base.

**Few-Shot / Few-Shot Bias**
Few-shot means giving the model example sentences. The **few-shot bias** is the trap that comes with it: the model parrots the example sentences almost verbatim instead of formulating freely. The result would be robotic conversations in which the agent works through example questions one by one. That is why we write the *intent* into the prompt ("find out whether …") instead of ready-made example questions.

**built_in_tools**
Ready-made capabilities that ElevenLabs gives the agent. We use four of them:
- **end_call** – the agent hangs up itself when the conversation is over.
- **voicemail_detection** – detects an answering machine and reacts accordingly (short message instead of pitch).
- **transfer_to_agent** – hands the conversation over to another agent (e.g. the central pitch agent).
- **skip_turn** – the agent deliberately skips a turn and waits instead of talking.

**EU Residency**
Data held exclusively on European servers. We always deploy our agents via the ElevenLabs EU residency address so that conversation data stays in the EU. That is our GDPR foundation and a selling point with data-sensitive customers.

**UUID**
A very long, globally unique string that systems use to tell individual objects apart (calls, records, configurations). You never need to memorise a UUID, it is just the technical address of a thing.

**API / API key**
An **API** is the interface through which two systems talk to each other, for example our deploy script with ElevenLabs. The **API key** is the access key for it, comparable to a password. Whoever has the key can create and change agents, which is why it is kept protected.

---

## Process

**Deploy / Deployment**
The process that puts a finished agent live: prompt, voice and all settings are transferred to ElevenLabs so the agent can make calls. After the deploy we check automatically whether everything really arrived correctly (voice, language, prompt length).

**PATCH / No-clobber PATCH**
A **PATCH** is a partial update to an existing agent — you change only one setting instead of recreating the whole agent. The danger: a sloppy PATCH can accidentally overwrite or delete other settings (the built_in_tools or the knowledge base, for instance). **No-clobber** means patching carefully enough that only the intended thing changes and the rest stays untouched. "Clobber" = overwrite; "no-clobber" = precisely not that.

**Campaign platform**
The system that runs the campaigns. It triggers the calls (dispatches them), passes the right variables to the agent per call and evaluates the conversations afterwards (among other things via task extraction). The agent running at ElevenLabs holds the conversation, the campaign platform organizes everything around it.

**Campaign**
A coherent calling assignment: a list of leads, a goal and an assigned agent. The campaign is created, started and evaluated in the campaign platform. Example: "call 500 staffing agencies in North Rhine-Westphalia and qualify interest in candidate profile sales".

**Briefing**
The starting document (`briefing.md`) that states what the agent should be able to do: customer, goal, target audience, tone. It is the first pipeline step and the basis for everything that follows. A good briefing saves many correction loops later.

**Dry run**
A trial run in which a process is played through without producing real effects (no real call, no real live change). Serves to find errors up front, before going live.
