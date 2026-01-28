# Latency Optimization Summary

## Rules Enforced

- **≤1 primary LLM call per request (default)** – Fast path uses a single full-doc LLM call. No per-section calls unless `deep=true`.
- **≤1 tool call for 80% of requests** – Default path: 1 LLM call (treated as 1 tool call).
- **No ReAct / retry loops** – Single-pass execution; no think-act-observe or self-reflection.
- **Deterministic routing** – Rule-based: `deep=false` → 1 LLM call; `deep=true` → slow path (per-section). No LLM used for routing.
- **Single-pass execution** – One LLM call max on fast path; slow path is explicit and opt-in.
- **Decision-level caching** – Structure extraction cached by content hash (`structure_cache`). No raw LLM output caching.
- **Instrumentation** – Logs `llm_calls`, `tool_calls` (0 unless function calling added), `time_to_first_useful_ms` per request. Request fails if `llm_calls > 2`.
- **Parallel non-dependent ops** – Fast path: structure fetch runs in parallel with the single LLM call; scoring uses the pre-fetched structure so no extra wall-clock after LLM.
- **Deep path** – Structure is extracted once and reused for scoring; no second extraction or cache lookup.

## Expected Latency Improvements

- **Before:** N LLM calls when PRD had sections (Stage 2), 1 call when no sections.
- **After (default):** Always 1 LLM call. Wall-clock reduced by ~(N-1) × (section LLM latency) for multi-section PRDs.
- **Structure extraction:** Cached by content hash; repeat analyses skip re-extraction.
- **Scoring:** Deterministic, no LLM. Fast path: structure fetched in parallel with LLM so scoring adds no extra wait. Deep path: structure reused from initial extract.
- **Tool calls:** Logged explicitly (0 on default path); increment when/if tool use is added.

## Remaining Bottlenecks

- **Single LLM call latency** – Dominated by Groq and prompt size. Further gains require smaller prompts or faster model.
- **No additional tools** – Only LLM; no retrieval/enrichment to parallelize beyond structure fetch.
- **Streaming** – SSE streams progress but does not reduce time to first useful response; it only improves perceived latency.

## API

- **POST /api/analyze** – Creates PRD, starts background analysis (fast path: 1 LLM call).
- **POST /api/analyze/stream** – Same input; streams SSE. Query param `deep=true` for slow path (per-section analysis).
