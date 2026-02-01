# Free LLM Setup Guide

Use free LLM models with the PRD Reviewer. **Ollama** (local, no limits) and **Groq** (cloud, fast) are supported.

---

## Already have Ollama installed?

1. In `backend/.env` set:
   ```env
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2
   ```
   (Use your model name if different, e.g. `llama3.1:8b`.)

2. Restart the backend. The app uses Ollama at `http://localhost:11434/v1` (OpenAI-compatible). **Full PRD context is sent** (no truncation).

3. If Ollama isn’t running: `ollama serve` (or start the app from the dock). Test: `ollama run llama3.2 "Hello"`.

---

## Installing Ollama from scratch

**macOS:** `brew install ollama` or https://ollama.ai  
**Linux:** `curl -fsSL https://ollama.ai/install.sh | sh`  
**Windows:** https://ollama.ai

Then pull a model and set `.env` as above:

```bash
ollama pull llama3.2
# Optional: ollama pull mistral | qwen2.5 | llama3.1:8b
```

---

## Groq (fast, cloud)

1. Get API key at https://console.groq.com (free signup).
2. In `backend/.env`:
   ```env
   LLM_PROVIDER=groq
   GROQ_API_KEY=your_key
   ```
3. Restart backend. Default model: `llama-3.1-8b-instant`. For higher quality set `GROQ_MODEL=llama-3.3-70b-versatile`. Groq has rate limits; use Ollama for large PRDs.

---

## Configuration

```env
LLM_PROVIDER=ollama   # or groq
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
GROQ_API_KEY=...      # when using groq
LLM_MAX_TOKENS=2000   # lower = faster output
```

---

## Troubleshooting

**Ollama – connection refused:** Run `ollama serve` or start Ollama from the dock. Check: `curl http://localhost:11434/api/tags`.

**Ollama – model not found:** `ollama pull llama3.2` (or your chosen model).

**Ollama – out of memory:** Use a smaller model, e.g. `ollama pull llama3.1:8b` and set `OLLAMA_MODEL=llama3.1:8b`.

**Groq – rate limit:** Groq free tier has TPM limits. Use Ollama for full PRD context.

**Switch provider:** Change `LLM_PROVIDER` in `backend/.env` and restart the backend.

---

- Ollama: https://ollama.ai · Groq: https://groq.com · Models: https://ollama.ai/library
