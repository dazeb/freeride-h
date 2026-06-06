# Provider Catalog

Full list of all 46 models across 9 providers with context lengths, tier, API endpoints, and details.

## OpenRouter

- **Env var:** `OPENROUTER_API_KEY`
- **Base URL:** `https://openrouter.ai/api/v1`
- **Free tier:** ~6M tokens/mo per model

| Model | Context | Details |
|-------|---------|---------|
| openrouter/owl-alpha | 131,072 | General purpose, 1B param model |
| openrouter/elephant-alpha | 131,072 | General purpose, 1B param model |
| tencent/hy3-preview:free | 131,072 | Tencent's preview model |
| nvidia/nemotron-3-super-120b-a12b:free | 131,072 | 120B MoE, strong reasoning |
| inclusionai/ring-2.6-1t:free | 131,072 | 1T MoE, very capable |
| openrouter/pareto-code | 131,072 | Code-optimized model |

## OpenCode Zen

- **Env var:** `OPENCODE_ZEN_API_KEY`
- **Base URL:** `https://opencode.ai/zen/v1`
- **Free tier:** Free (with API key)

| Model | Context | Tier | Details |
|-------|---------|------|---------|
| opencode-zen/big-pickle | 128,000 | free | Strong general model |
| opencode-zen/deepseek-v4-flash-free | 128,000 | free | Fast reasoning, free |
| opencode-zen/qwen3.6-plus-free | 128,000 | free | Alibaba Qwen, free tier |
| opencode-zen/minimax-m2.5-free | 128,000 | free | MiniMax model, free |
| opencode-zen/nemotron-3-super-free | 128,000 | free | NVIDIA Nemotron via Zen |
| opencode-zen/gpt-5.4-mini | 128,000 | paid | OpenAI GPT 5.4 Mini |
| opencode-zen/gpt-5.4 | 128,000 | paid | OpenAI GPT 5.4 |
| opencode-zen/claude-sonnet-4 | 200,000 | paid | Anthropic Sonnet 4 |

## Mistral

- **Env var:** `MISTRAL_API_KEY`
- **Base URL:** `https://api.mistral.ai/v1`
- **Free tier:** ~1B tokens/mo shared — biggest free pool

| Model | Context | Details |
|-------|---------|---------|
| mistral/mistral-large-2508 | 128,000 | Strongest Mistral model |
| mistral/ministral-8b-2508 | 128,000 | Lightweight, fast |
| mistral/codestral-2505 | 256,000 | Code-specialized, huge context |
| mistral/mistral-saba-2502 | 32,000 | Arabic-focused model |

## Groq

- **Env var:** `GROQ_API_KEY`
- **Base URL:** `https://api.groq.com/openai/v1`
- **Free tier:** ~30M tokens/mo per model, fastest inference

| Model | Context | Details |
|-------|---------|---------|
| groq/llama-3.3-70b-versatile | 128,000 | Meta Llama 70B |
| groq/llama-4-scout | 128,000 | Meta Llama 4 Scout |
| groq/qwen-3-32b | 128,000 | Alibaba Qwen3 32B |
| groq/gpt-oss-120b | 128,000 | Open-source GPT 120B |

## Cerebras

- **Env var:** `CEREBRAS_API_KEY`
- **Base URL:** `https://api.cerebras.ai/v1`
- **Free tier:** ~30M tokens/mo shared, fastest chips

| Model | Context | Details |
|-------|---------|---------|
| cerebras/qwen3-235b | 128,000 | Qwen 235B |
| cerebras/gpt-oss-120b | 128,000 | Open-source GPT 120B |
| cerebras/llama-3.1-8b | 128,000 | Lightweight, fastest tokens |

## SambaNova

- **Env var:** `SAMBANOVA_API_KEY`
- **Base URL:** `https://api.sambanova.ai/v1`
- **Free tier:** ~3M tokens/mo shared

| Model | Context | Details |
|-------|---------|---------|
| sambanova/deepseek-v3.1 | 128,000 | DeepSeek V3.1 |
| sambanova/deepseek-v3.2 | 128,000 | DeepSeek V3.2 |
| sambanova/llama-4-maverick | 128,000 | Meta Llama 4 Maverick |
| sambanova/llama-3.3-70b | 128,000 | Meta Llama 3.3 70B |
| sambanova/gemma-3-12b | 128,000 | Google Gemma 3 12B |
| sambanova/gpt-oss-120b | 128,000 | Open-source GPT 120B |

## NVIDIA NIM

- **Env var:** `NVIDIA_API_KEY`
- **Base URL:** `https://integrate.api.nvidia.com/v1`
- **Free tier:** Credit-based (may need to opt in at build.nvidia.com)

| Model | Context | Details |
|-------|---------|---------|
| nvidia/llama-3.1-70b | 128,000 | Meta Llama 70B hosted on NIM |
| nvidia/nemotron-4-340b | 128,000 | NVIDIA Nemotron 4, 340B params |
| nvidia/mistral-large | 128,000 | Mistral Large on NIM |

## Ollama Local (GPU)

- **Env var:** *(none — no API key needed)*
- **Base URL:** `http://localhost:11434/v1`
- **Free tier:** Your GPU (RTX 3080 Ti or similar)

| Model | Size | Context | Details |
|-------|------|---------|---------|
| ollama-local/qwen3.5:9b | 6.6 GB | 32,768 | RTX 3080 Ti, local GPU inference |
| ollama-local/gemma4-obliterated-tools:latest | 5.0 GB | 32,768 | Tools-capable, uncensored |
| ollama-local/gemma4-uncensored:latest | 5.8 GB | 32,768 | Local GPU, uncensored |
| ollama-local/huihui_ai/qwen3.5-abliterated:9b | 6.6 GB | 32,768 | Uncensored Qwen |
| ollama-local/hf.co/OBLITERATUS/gemma-4-E4B-it-OBLITERATED:Q8_0 | 8.0 GB | 32,768 | Q8 quant, high quality |
| ollama-local/qwen3.5:4b | 3.4 GB | 32,768 | Fast local inference |
| ollama-local/llama3.2:1b | 1.3 GB | 128,000 | Tiny, fast, 128K context |
| ollama-local/hf.co/unsloth/Nemotron-3-Nano-30B-A3B-GGUF:Q4_K_M | 24 GB | 32,768 | Strong reasoning (split load) |

## Ollama Cloud

- **Env var:** `OLLAMA_API_KEY`
- **Base URL:** `https://api.ollama.ai/v1`
- **Free tier:** Free GPU-time, 1 concurrent model

| Model | Context | Details |
|-------|---------|---------|
| ollama-cloud/gpt-oss | 128,000 | Free GPU-time |
| ollama-cloud/glm-4.7 | 128,000 | Zhipu GLM-4.7 |
| ollama-cloud/qwen3 | 128,000 | Alibaba Qwen3 |
| ollama-cloud/kimi-k2 | 128,000 | Moonshot Kimi K2 |
