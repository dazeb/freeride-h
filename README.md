# 🏄 FreeRide-H

> **Multi-provider free-model manager for Hermes AI agents.**
>
> Browse, switch, and auto-rotate across **9 providers** and **43+ free AI models** — cloud and local.
> Run it mid-task without breaking your flow.

![FreeRide-H Banner](banner.jpg)

## Why FreeRide-H?

AI agents burn through API quota fast. FreeRide-H solves this with a model browser + auto-fallback daemon:

- **`freeride list`** — see every free model across every provider, with context size and details
- **`freeride switch big-pickle`** — switch models mid-task, auto-detects the provider
- **`freeride-watcher`** — background daemon that probes your current model and rotates to the next free one when quota runs out
- **`freeride auto`** — configure all free providers in Hermes with one command

## Supported Providers

| Provider | Env Var | Free Tier | Free Models |
|----------|---------|-----------|-------------|
| **OpenRouter** | `OPENROUTER_API_KEY` | ~6M/mo per model | owl-alpha, elephant-alpha, hy3-preview, nemotron-3-120b, ring-2.6-1t, pareto-code |
| **OpenCode Zen** | `OPENCODE_ZEN_API_KEY` | Free tier | big-pickle, deepseek-v4-flash-free, qwen3.6-plus-free, minimax-m2.5-free, nemotron-3-super-free |
| **Mistral** | `MISTRAL_API_KEY` | ~1B/mo shared | Mistral Large, Ministral 8B, Codestral (256K ctx) |
| **Groq** | `GROQ_API_KEY` | ~30M/mo per model | Llama 3.3 70B, Llama 4 Scout, Qwen3 32B, GPT-OSS 120B |
| **Cerebras** | `CEREBRAS_API_KEY` | ~30M/mo shared | Qwen3 235B, GPT-OSS 120B, Llama 3.1 8B |
| **SambaNova** | `SAMBANOVA_API_KEY` | ~3M/mo shared | DeepSeek V3.1/V3.2, Llama 4 Maverick, Llama 3.3 70B, Gemma 3 12B, GPT-OSS 120B |
| **NVIDIA NIM** | `NVIDIA_API_KEY` | Credit-based | Llama 3.1 70B, Nemotron 4 340B, Mistral Large |
| **Ollama Local** | *(none)* | Local GPU | qwen3.5, gemma4, nemotron-3-nano, llama3.2 |
| **Ollama Cloud** | `OLLAMA_API_KEY` | Free GPU-time | GPT-OSS, GLM-4.7, Qwen3, Kimi K2 |

> **Total: 43 free models across 9 providers.** All OpenAI-compatible.

## Quick Start

```bash
# 1. Set API keys for the providers you want to use
export OPENROUTER_API_KEY="sk-or-v1-..."
export MISTRAL_API_KEY="..."
export GROQ_API_KEY="..."

# 2. Configure all free providers in Hermes
freeride auto

# 3. Browse available models
freeride list

# 4. Switch to a specific model
freeride switch big-pickle

# 5. Start the background watcher (optional)
freeride-watcher
```

## CLI Reference

### `freeride list`

Show all models across all providers with context size, tier, and details.

```bash
freeride list                       # all 46 models
freeride free                       # only free-tier (43 models)
freeride list --provider mistral    # filter by provider
freeride list --provider ollama     # local + cloud Ollama
```

Output:
```
Provider         Model ID                                        Ctx Tier    Details
------------------------------------------------------------------------------------
OpenRouter       openrouter/owl-alpha                        131,072 free    General purpose
OpenRouter       openrouter/elephant-alpha                   131,072 free    General purpose
...
Ollama Local     ollama-local/qwen3.5:9b                      32,768 free    RTX 3080 Ti, 6.6 GB

Total: 46 models  |  Free: 43  |  Providers: 9
```

### `freeride switch <model>`

Switch Hermes to a specific model. Auto-detects which provider owns it.

```bash
freeride switch big-pickle         # OpenCode Zen
freeride switch qwen3.5:9b         # Ollama Local
freeride switch codestral          # Mistral
freeride switch llama-3.3-70b      # Groq
freeride switch gpt-5.4-mini       # OpenCode Zen (partial match works)
```

### `freeride auto`

Configure all free providers in Hermes config at once. Sets `model.provider`, `model.default`, `model.base_url`, and provider-specific fields.

### `freeride status`

Run `hermes config check` to verify current configuration.

## Background Watcher

The `freeride-watcher` daemon runs as a background process and:

1. **Probes** your current model every 60 seconds with a lightweight ping
2. **Detects failures** — 4xx/5xx errors, timeouts, quota exhaustion
3. **Measures speed** — rotates off models slower than 12s response time
4. **Rotates** to the next free model across all providers (cyclic)

```bash
freeride-watcher              # run as daemon
freeride-watcher --once       # run one check-and-rotate cycle
freeride-watcher --status     # show rotation state
freeride-watcher -i 300       # custom interval (300s)
```

Rotation state is persisted to `~/.hermes/.freeride-watcher-state.json`:
```json
{
  "rotation_count": 12,
  "last_rotation_at": "2026-06-06T21:18:46",
  "last_rotation_reason": "quota",
  "last_model": "opencode-zen/big-pickle",
  "last_provider": "opencode-zen"
}
```

## How It Works

```
                    ┌─ freeride list ──────────────────────┐
                    │ Browse 46 models across 9 providers   │
                    │ Filter by provider, tier, context     │
                    └──────────┬───────────────────────────┘
                               │
                    ┌──────────▼───────────────────────────┐
                    │ freeride switch <model>              │
                    │ Auto-detects provider from registry  │
                    │ Sets model.provider, model.default,  │
                    │ model.base_url, provider config      │
                    └──────────┬───────────────────────────┘
                               │
                    ┌──────────▼───────────────────────────┐
                    │ freeride-watcher (daemon)            │
                    │ 1. Probes current model every 60s    │
                    │ 2. On fail/slow → pick next free     │
                    │ 3. Set config → switch provider+model│
                    └─────────────────────────────────────┘
```

### Provider Registry

Providers are defined as data in `freeride.py`:

```python
Provider(
    name="Groq",
    env_var="GROQ_API_KEY",
    base_url="https://api.groq.com/openai/v1",
    hermes_name="groq",
    models=[
        {"id": "groq/llama-3.3-70b-versatile", ...},
        {"id": "groq/llama-4-scout", ...},
    ],
)
```

To add a new provider, just append to the `PROVIDERS` list. The CLI, watcher, and config auto-discover it.

## Installation

### Hermes Skill (recommended)

```bash
# Clone the repo
git clone https://github.com/YOUR_USER/freeride-h.git ~/.hermes/skills/freeride-h

# Make commands available
ln -sf ~/.hermes/skills/freeride-h/freeride.py ~/.local/bin/freeride
chmod +x ~/.local/bin/freeride
ln -sf ~/.hermes/skills/freeride-h/watcher.py ~/.local/bin/freeride-watcher
chmod +x ~/.local/bin/freeride-watcher
```

### Standalone

```bash
pip install freeride-h
```

**Requirements:** Python 3.10+, Hermes CLI (for `freeride auto` / `freeride switch`)

## Ollama Local Setup

If you run Ollama locally, no API key is needed:

```bash
# Start Ollama
ollama serve

# Pull models
ollama pull qwen3.5:9b
ollama pull llama3.2:1b

# Browse local models
freeride list --provider ollama

# Switch to local inference
freeride switch qwen3.5:9b
```

The watcher automatically detects local models and skips API key checks.

## Adding a New Provider

1. Edit `freeride.py` and add a `Provider(...)` to the `PROVIDERS` list
2. Set the env var, base URL, and model list
3. The CLI, auto-config, and watcher pick it up automatically

```python
Provider(
    name="MyProvider",
    env_var="MY_API_KEY",
    base_url="https://api.myprovider.com/v1",
    hermes_name="my-provider",
    models=[
        {"id": "my-provider/model-1", "label": "Model 1", "context_length": 128_000, "tier": "free", "details": "Description"},
    ],
)
```

## Why "H"?

The "H" stands for **Hermes**. This is a complete rewrite of the original FreeRide skill (by Shaishav Pidadi) as a Hermes-native multi-provider model manager. The original was OpenRouter-only; FreeRide-H covers 9 providers with auto-rotation.

## License

MIT — use it, ship it, fork it.

---

*Built for [Hermes Agent](https://hermes-agent.nousresearch.com) created by Nous Research.*  

Freeride-h is *not* affiliated with Hermes or Nous Research in *any way*. 
