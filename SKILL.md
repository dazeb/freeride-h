---
name: freeride-h
description: "Multi-provider free-model manager for Hermes. Browse, switch, and auto-rotate across 9 providers and 43+ free AI models via the freeride CLI. Triggers: user asks about free models, wants to switch models mid-task, mentions big-pickle/qwen3.5/llama/local, watcher daemon, quota exhaustion, or model rotation."
---

# FreeRide-H — Free Model Manager

**PyPI:** `pip install freeride-h`
**Source:** `pip install git+https://github.com/dazeb/freeride-h.git`
**Docs:** `freeride list | freeride --help`

Browse, switch, and auto-rotate across **9 providers** and **43+ free AI models**.

## Quick Start

```bash
# Install
pip install freeride-h

# Browse free models
freeride list                        # all 46 models
freeride free                        # only free-tier (43 models)
freeride list --provider ollama      # filter by provider

# Switch models mid-task
freeride switch big-pickle           # OpenCode Zen
freeride switch qwen3.5:9b           # Ollama Local (GPU, no API key)
freeride switch codestral            # Mistral (256K ctx)
freeride switch llama-3.3-70b        # Groq (fast inference)
freeride switch nemotron             # NVIDIA NIM / OpenRouter

# Configure all free providers
freeride auto

# Background auto-rotation daemon
freeride-watcher                     # probes every 60s, rotates on fail/slow
freeride-watcher --once              # single check-and-rotate
freeride-watcher --status            # show rotation state
```

## Provider Catalog

For the full provider catalog with all model IDs, context lengths, and API endpoints, see [`references/provider-catalog.md`](references/provider-catalog.md).

### Cloud Free Tier (need API key)

| Provider | Env Var | Free Tier | Models |
|----------|---------|-----------|--------|
| OpenRouter | `OPENROUTER_API_KEY` | ~6M/mo per model | owl-alpha, elephant-alpha, hy3-preview, nemotron-3-120b, ring-2.6-1t, pareto-code |
| OpenCode Zen | `OPENCODE_ZEN_API_KEY` | Free tier | big-pickle, deepseek-v4-flash-free, qwen3.6-plus-free, minimax-m2.5-free, nemotron-3-super-free |
| Mistral | `MISTRAL_API_KEY` | ~1B/mo shared | Mistral Large, Ministral 8B, Codestral (256K ctx), Mistral Saba |
| Groq | `GROQ_API_KEY` | ~30M/mo per model | Llama 3.3 70B, Llama 4 Scout, Qwen3 32B, GPT-OSS 120B |
| Cerebras | `CEREBRAS_API_KEY` | ~30M/mo shared | Qwen3 235B, GPT-OSS 120B, Llama 3.1 8B |
| SambaNova | `SAMBANOVA_API_KEY` | ~3M/mo shared | DeepSeek V3.1/V3.2, Llama 4 Maverick, Llama 3.3 70B, Gemma 3 12B, GPT-OSS 120B |
| NVIDIA NIM | `NVIDIA_API_KEY` | Credit-based | Llama 3.1 70B, Nemotron 4 340B, Mistral Large |

### Local (no API key)

| Provider | Base URL | Models |
|----------|----------|--------|
| Ollama Local | `http://localhost:11434/v1` | qwen3.5:9b, gemma4-abliterated, nemotron-3-nano, llama3.2:1b (+ more) |

### Cloud GPU

| Provider | Env Var | Models |
|----------|---------|--------|
| Ollama Cloud | `OLLAMA_API_KEY` | GPT-OSS, GLM-4.7, Qwen3, Kimi K2 |

## When to Use

- **Model stuck on quota** — `freeride list` → `freeride switch <model>`
- **User asks for a specific model** — auto-detects provider from registry
- **User wants local inference** — `freeride switch qwen3.5:9b`
- **Rate limits** — start `freeride-watcher` as background daemon
- **What's available?** — `freeride free` shows all free models with context sizes

## Architecture

```
PROVIDERS = [
  Provider(name="Groq", env_var="GROQ_API_KEY", base_url="...", hermes_name="groq", models=[...]),
  ...
]
```

To add a provider, append to the `PROVIDERS` list in `freeride.py`. The CLI, auto-config, and watcher auto-discover it.

## Files

| File | Purpose |
|------|---------|
| `freeride.py` | CLI — list, free, switch, auto, status |
| `watcher.py` | Background daemon — probes and auto-rotates |
| `setup.py` / `pyproject.toml` | Pip packaging |
| `__init__.py` | Module imports |
| `references/provider-catalog.md` | Full model catalog |
