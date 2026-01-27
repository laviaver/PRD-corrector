# Free LLM Setup Guide

This guide explains how to use free LLM models with the PRD Reviewer application.

## 🆓 Free Options

### 1. **Ollama** (Recommended - Completely Free, Local)
- ✅ **100% Free** - No API key needed
- ✅ **Runs Locally** - Your data stays on your machine
- ✅ **No Rate Limits** - Use as much as you want
- ✅ **Multiple Models** - Llama 3.2, Mistral, Qwen, etc.
- ⚠️ Requires ~4-8GB RAM for good models

### 2. **Groq** (Fast & Free Tier)
- ✅ **Free Tier Available** - Very generous limits
- ✅ **Extremely Fast** - Fastest inference available
- ✅ **Cloud-Based** - No local setup needed
- ⚠️ Requires API key (free to get)

### 3. **Hugging Face** (Free Tier)
- ✅ **Free Tier** - Limited but usable
- ✅ **Many Models** - Access to thousands of models
- ⚠️ Rate limits on free tier
- ⚠️ Requires API key

---

## 🚀 Quick Start: Ollama (Recommended)

### Step 1: Install Ollama

**macOS:**
```bash
brew install ollama
# Or download from https://ollama.ai
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download installer from https://ollama.ai

### Step 2: Pull a Model

```bash
# Recommended: Llama 3.2 (good balance of quality and speed)
ollama pull llama3.2

# Alternative models:
# ollama pull mistral        # Fast and efficient
# ollama pull qwen2.5        # Good for structured output
# ollama pull llama3.1:8b    # Smaller, faster
```

### Step 3: Configure Backend

Create or update `backend/.env`:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### Step 4: Start Ollama

```bash
# Start Ollama server (if not running automatically)
ollama serve
```

### Step 5: Test

```bash
# Test Ollama is working
ollama run llama3.2 "Hello, can you help me analyze a PRD?"
```

That's it! The backend will now use Ollama for free LLM analysis.

---

## ⚡ Quick Start: Groq (Fast Alternative)

### Step 1: Get API Key

1. Go to https://console.groq.com
2. Sign up (free)
3. Create an API key
4. Copy the key

### Step 2: Configure Backend

Update `backend/.env`:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
```

### Step 3: Install Dependencies

```bash
cd backend
source venv/bin/activate
pip install openai  # Already in requirements.txt
```

That's it! Groq is extremely fast and free.

---

## 🔧 Configuration Options

### Environment Variables

```env
# Choose your provider
LLM_PROVIDER=ollama  # Options: ollama, groq, openai, huggingface

# Ollama settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Groq settings
GROQ_API_KEY=your_key_here

# OpenAI settings (if you want to use paid OpenAI)
OPENAI_API_KEY=your_key_here

# Hugging Face settings
HUGGINGFACE_API_KEY=your_key_here
```

---

## 📊 Model Comparison

| Model | Speed | Quality | Cost | Setup |
|-------|-------|---------|------|-------|
| **Ollama (Llama 3.2)** | Medium | High | Free | Easy |
| **Groq (Llama 3.1)** | Very Fast | High | Free | Very Easy |
| **Hugging Face** | Medium | Medium | Free | Easy |
| **OpenAI GPT-4** | Medium | Very High | Paid | Easy |

---

## 🐛 Troubleshooting

### Ollama Issues

**Problem**: `Connection refused` error
```bash
# Solution: Make sure Ollama is running
ollama serve

# Or check if it's running
curl http://localhost:11434/api/tags
```

**Problem**: Model not found
```bash
# Solution: Pull the model
ollama pull llama3.2
```

**Problem**: Out of memory
```bash
# Solution: Use a smaller model
ollama pull llama3.1:8b  # Smaller model
# Then update .env: OLLAMA_MODEL=llama3.1:8b
```

### Groq Issues

**Problem**: API key invalid
- Check your API key at https://console.groq.com
- Make sure it's set in `backend/.env`

**Problem**: Rate limit exceeded
- Groq free tier has limits
- Wait a bit or switch to Ollama

---

## 💡 Tips

1. **For Development**: Use Ollama - completely free, no limits
2. **For Speed**: Use Groq - fastest inference available
3. **For Privacy**: Use Ollama - everything runs locally
4. **For Production**: Consider Groq or OpenAI for reliability

---

## 🔄 Switching Providers

Just change `LLM_PROVIDER` in `backend/.env` and restart the backend:

```env
# Switch to Groq
LLM_PROVIDER=groq
GROQ_API_KEY=your_key

# Switch back to Ollama
LLM_PROVIDER=ollama
```

No code changes needed!

---

## 📚 More Information

- **Ollama**: https://ollama.ai
- **Groq**: https://groq.com
- **Hugging Face**: https://huggingface.co
- **Model List**: https://ollama.ai/library

---

**Happy analyzing! 🎉**
