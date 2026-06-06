#!/usr/bin/env python3
"""freeride — multi-provider free-model manager for Hermes.

Supports OpenRouter, OpenCode Zen, Mistral, Groq, Cerebras, SambaNova,
NVIDIA NIM, Ollama Local (GPU), and Ollama Cloud.
CLI: freeride list | freeride free | freeride auto | freeride switch <model> | freeride status
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

# ── Provider definitions ──────────────────────────────────────────────

class Provider:
    """A provider with its env var, base URL, and free models."""

    def __init__(
        self,
        name: str,
        env_var: str,
        base_url: str,
        hermes_name: str,
        models: list[dict],
    ) -> None:
        self.name = name
        self.env_var = env_var
        self.base_url = base_url
        self.hermes_name = hermes_name  # provider key in Hermes config
        self.models = models  # list of {id, label, context_length, tier, details}

    def model_ids(self) -> list[str]:
        return [m["id"] for m in self.models]


PROVIDERS: list[Provider] = [
    Provider(
        name="OpenRouter",
        env_var="OPENROUTER_API_KEY",
        base_url="https://openrouter.ai/api/v1",
        hermes_name="openrouter",
        models=[
            {"id": "openrouter/owl-alpha", "label": "Owl Alpha", "context_length": 131_072, "tier": "free", "details": "General purpose, 1B param model"},
            {"id": "openrouter/elephant-alpha", "label": "Elephant Alpha", "context_length": 131_072, "tier": "free", "details": "General purpose, 1B param model"},
            {"id": "tencent/hy3-preview:free", "label": "Tencent HY3 Preview", "context_length": 131_072, "tier": "free", "details": "Tencent's preview model"},
            {"id": "nvidia/nemotron-3-super-120b-a12b:free", "label": "NVIDIA Nemotron 3 120B", "context_length": 131_072, "tier": "free", "details": "120B MoE, strong reasoning"},
            {"id": "inclusionai/ring-2.6-1t:free", "label": "InclusionAI Ring 2.6 1T", "context_length": 131_072, "tier": "free", "details": "1T MoE, very capable"},
            {"id": "openrouter/pareto-code", "label": "Pareto Code", "context_length": 131_072, "tier": "free", "details": "Code-optimized model"},
        ],
    ),
    Provider(
        name="OpenCode Zen",
        env_var="OPENCODE_ZEN_API_KEY",
        base_url="https://opencode.ai/zen/v1",
        hermes_name="opencode-zen",
        models=[
            {"id": "opencode-zen/big-pickle", "label": "BIG Pickle", "context_length": 128_000, "tier": "free", "details": "Free tier, strong general model"},
            {"id": "opencode-zen/deepseek-v4-flash-free", "label": "DeepSeek V4 Flash Free", "context_length": 128_000, "tier": "free", "details": "Fast reasoning, free"},
            {"id": "opencode-zen/qwen3.6-plus-free", "label": "Qwen 3.6 Plus Free", "context_length": 128_000, "tier": "free", "details": "Alibaba's Qwen, free tier"},
            {"id": "opencode-zen/minimax-m2.5-free", "label": "MiniMax M2.5 Free", "context_length": 128_000, "tier": "free", "details": "MiniMax model, free tier"},
            {"id": "opencode-zen/nemotron-3-super-free", "label": "Nemotron 3 Super Free", "context_length": 128_000, "tier": "free", "details": "NVIDIA Nemotron, free via Zen"},
            # Paid but commonly used
            {"id": "opencode-zen/gpt-5.4-mini", "label": "GPT 5.4 Mini", "context_length": 128_000, "tier": "paid", "details": "OpenAI GPT 5.4 Mini"},
            {"id": "opencode-zen/gpt-5.4", "label": "GPT 5.4", "context_length": 128_000, "tier": "paid", "details": "OpenAI GPT 5.4"},
            {"id": "opencode-zen/claude-sonnet-4", "label": "Claude Sonnet 4", "context_length": 200_000, "tier": "paid", "details": "Anthropic Sonnet 4"},
        ],
    ),
    Provider(
        name="Mistral",
        env_var="MISTRAL_API_KEY",
        base_url="https://api.mistral.ai/v1",
        hermes_name="mistral",
        models=[
            {"id": "mistral/mistral-large-2508", "label": "Mistral Large", "context_length": 128_000, "tier": "free", "details": "~1B tokens/mo, strongest Mistral model, huge free pool"},
            {"id": "mistral/ministral-8b-2508", "label": "Ministral 8B", "context_length": 128_000, "tier": "free", "details": "Lightweight, fast, free within quota"},
            {"id": "mistral/codestral-2505", "label": "Codestral", "context_length": 256_000, "tier": "free", "details": "Code-specialized, 256K context, free"},
            {"id": "mistral/mistral-saba-2502", "label": "Mistral Saba", "context_length": 32_000, "tier": "free", "details": "Arabic-focused model, free tier"},
        ],
    ),
    Provider(
        name="Groq",
        env_var="GROQ_API_KEY",
        base_url="https://api.groq.com/openai/v1",
        hermes_name="groq",
        models=[
            {"id": "groq/llama-3.3-70b-versatile", "label": "Llama 3.3 70B", "context_length": 128_000, "tier": "free", "details": "~30M/mo, fastest inference, Meta Llama 70B"},
            {"id": "groq/llama-4-scout", "label": "Llama 4 Scout", "context_length": 128_000, "tier": "free", "details": "Meta Llama 4 Scout, 30M/mo"},
            {"id": "groq/qwen-3-32b", "label": "Qwen3 32B", "context_length": 128_000, "tier": "free", "details": "Alibaba Qwen3 32B, 30M/mo"},
            {"id": "groq/gpt-oss-120b", "label": "GPT-OSS 120B", "context_length": 128_000, "tier": "free", "details": "Open-source GPT, 120B params"},
        ],
    ),
    Provider(
        name="Cerebras",
        env_var="CEREBRAS_API_KEY",
        base_url="https://api.cerebras.ai/v1",
        hermes_name="cerebras",
        models=[
            {"id": "cerebras/qwen3-235b", "label": "Qwen3 235B", "context_length": 128_000, "tier": "free", "details": "~30M/mo shared, Qwen 235B, fastest chips"},
            {"id": "cerebras/gpt-oss-120b", "label": "GPT-OSS 120B", "context_length": 128_000, "tier": "free", "details": "Open-source GPT 120B, fast inference"},
            {"id": "cerebras/llama-3.1-8b", "label": "Llama 3.1 8B", "context_length": 128_000, "tier": "free", "details": "Lightweight, fastest tokens"},
        ],
    ),
    Provider(
        name="SambaNova",
        env_var="SAMBANOVA_API_KEY",
        base_url="https://api.sambanova.ai/v1",
        hermes_name="sambanova",
        models=[
            {"id": "sambanova/deepseek-v3.1", "label": "DeepSeek V3.1", "context_length": 128_000, "tier": "free", "details": "~3M/mo shared, DeepSeek V3.1"},
            {"id": "sambanova/deepseek-v3.2", "label": "DeepSeek V3.2", "context_length": 128_000, "tier": "free", "details": "DeepSeek V3.2, free tier"},
            {"id": "sambanova/llama-4-maverick", "label": "Llama 4 Maverick", "context_length": 128_000, "tier": "free", "details": "Meta Llama 4 Maverick, free"},
            {"id": "sambanova/llama-3.3-70b", "label": "Llama 3.3 70B", "context_length": 128_000, "tier": "free", "details": "Meta Llama 3.3 70B"},
            {"id": "sambanova/gemma-3-12b", "label": "Gemma 3 12B", "context_length": 128_000, "tier": "free", "details": "Google Gemma 3, free"},
            {"id": "sambanova/gpt-oss-120b", "label": "GPT-OSS 120B", "context_length": 128_000, "tier": "free", "details": "Open-source GPT 120B"},
        ],
    ),
    Provider(
        name="NVIDIA NIM",
        env_var="NVIDIA_API_KEY",
        base_url="https://integrate.api.nvidia.com/v1",
        hermes_name="nvidia-nim",
        models=[
            {"id": "nvidia/llama-3.1-70b", "label": "Llama 3.1 70B", "context_length": 128_000, "tier": "free", "details": "Credit-based free tier, Meta Llama 70B"},
            {"id": "nvidia/nemotron-4-340b", "label": "Nemotron 4 340B", "context_length": 128_000, "tier": "free", "details": "NVIDIA Nemotron 4, 340B params"},
            {"id": "nvidia/mistral-large", "label": "Mistral Large", "context_length": 128_000, "tier": "free", "details": "Mistral Large hosted on NIM"},
        ],
    ),
    Provider(
        name="Ollama Local (GPU)",
        env_var="",
        base_url="http://localhost:11434/v1",
        hermes_name="ollama-local",
        models=[
            {"id": "ollama-local/qwen3.5:9b", "label": "Qwen3.5 9B", "context_length": 32_768, "tier": "free", "details": "RTX 3080 Ti, 6.6 GB, local GPU inference"},
            {"id": "ollama-local/gemma4-obliterated-tools:latest", "label": "Gemma 4 E4B Tools (Obliterated)", "context_length": 32_768, "tier": "free", "details": "5 GB, local, tools-capable, uncensored"},
            {"id": "ollama-local/gemma4-uncensored:latest", "label": "Gemma 4 E4B Uncensored", "context_length": 32_768, "tier": "free", "details": "5.8 GB, local GPU, uncensored"},
            {"id": "ollama-local/huihui_ai/qwen3.5-abliterated:9b", "label": "Qwen3.5 9B Abliterated", "context_length": 32_768, "tier": "free", "details": "6.6 GB, local, uncensored Qwen"},
            {"id": "ollama-local/hf.co/OBLITERATUS/gemma-4-E4B-it-OBLITERATED:Q8_0", "label": "Gemma 4 E4B Obliterated Q8", "context_length": 32_768, "tier": "free", "details": "8 GB, local, Q8 quant, high quality"},
            {"id": "ollama-local/qwen3.5:4b", "label": "Qwen3.5 4B", "context_length": 32_768, "tier": "free", "details": "3.4 GB, fast local inference"},
            {"id": "ollama-local/llama3.2:1b", "label": "Llama 3.2 1B", "context_length": 128_000, "tier": "free", "details": "1.3 GB, tiny, fast, 128K context"},
            {"id": "ollama-local/hf.co/unsloth/Nemotron-3-Nano-30B-A3B-GGUF:Q4_K_M", "label": "Nemotron 3 Nano 30B A3B Q4", "context_length": 32_768, "tier": "free", "details": "24 GB (split), local, strong reasoning"},
        ],
    ),
    Provider(
        name="Ollama Cloud",
        env_var="OLLAMA_API_KEY",
        base_url="https://api.ollama.ai/v1",
        hermes_name="ollama-cloud",
        models=[
            {"id": "ollama-cloud/gpt-oss", "label": "GPT-OSS", "context_length": 128_000, "tier": "free", "details": "Free GPU-time, 1 concurrent model"},
            {"id": "ollama-cloud/glm-4.7", "label": "GLM-4.7", "context_length": 128_000, "tier": "free", "details": "Zhipu GLM-4.7, free GPU-time"},
            {"id": "ollama-cloud/qwen3", "label": "Qwen3", "context_length": 128_000, "tier": "free", "details": "Alibaba Qwen3, free GPU-time"},
            {"id": "ollama-cloud/kimi-k2", "label": "Kimi K2", "context_length": 128_000, "tier": "free", "details": "Moonshot Kimi K2, free GPU-time"},
        ],
    ),
]


def _all_models() -> list[tuple[Provider, dict]]:
    """Return list of (provider, model_dict) for every model across all providers."""
    result: list[tuple[Provider, dict]] = []
    for prov in PROVIDERS:
        for m in prov.models:
            result.append((prov, m))
    return result


def _find_provider_by_model(model_id: str) -> Provider | None:
    for prov in PROVIDERS:
        for m in prov.models:
            if m["id"] == model_id or m["id"].split("/", 1)[-1] == model_id:
                return prov
    return None


def _find_model(model_id: str) -> tuple[Provider | None, dict | None]:
    for prov in PROVIDERS:
        for m in prov.models:
            if m["id"] == model_id or m["id"].split("/", 1)[-1] == model_id:
                return prov, m
    return None, None


# ── Helpers ───────────────────────────────────────────────────────────

def _run(cmd: list[str]) -> int:
    return subprocess.call(cmd)


def _hermes(*args: str) -> int:
    return _run(["hermes", *args])


def _require_key(env_var: str) -> bool:
    if not env_var:
        return True  # local providers don't need keys
    if os.getenv(env_var):
        return True
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith(f"{env_var}=") and line.split("=", 1)[1].strip():
                return True
    print(f"WARNING: {env_var} not found; continuing.", file=sys.stderr)
    return True


# ── Commands ──────────────────────────────────────────────────────────

def cmd_list(args: argparse.Namespace) -> int:
    """Show all free models with context size and details."""
    # Filter
    only_free = getattr(args, "free", False)
    provider_filter = getattr(args, "provider", None)

    # Header
    header = f"{'Provider':<16} {'Model ID':<42} {'Ctx':>8} {'Tier':<6}  Details"
    print(header)
    print("-" * len(header))

    for prov in PROVIDERS:
        if provider_filter and provider_filter.lower() not in prov.name.lower() and provider_filter.lower() not in prov.hermes_name.lower():
            continue
        for m in prov.models:
            if only_free and m["tier"] != "free":
                continue
            ctx = f"{m['context_length']:,}"
            print(f"{prov.name:<16} {m['id']:<42} {ctx:>8} {m['tier']:<6}  {m['details']}")

    print()

    # Summary
    free_count = sum(1 for _, m in _all_models() if m["tier"] == "free")
    total_count = sum(1 for _ in _all_models())
    print(f"Total: {total_count} models  |  Free: {free_count}  |  Providers: {len(PROVIDERS)}")
    return 0


def cmd_free(args: argparse.Namespace) -> int:
    """Shortcut: show only free models."""
    args.free = True
    return cmd_list(args)


def cmd_auto(_: argparse.Namespace) -> int:
    """Configure all free providers in Hermes."""
    for prov in PROVIDERS:
        if not _require_key(prov.env_var):
            print(f"⚠ Skipping {prov.name}: missing {prov.env_var}", file=sys.stderr)
            continue
        steps = [
            ["config", "set", f"providers.{prov.hermes_name}.base_url", prov.base_url],
        ]
        if prov.env_var:
            steps.append(["config", "set", f"providers.{prov.hermes_name}.api_key_env_var", prov.env_var])
        # Add free models to the provider config
        free_models = [m for m in prov.models if m["tier"] == "free"]
        if free_models:
            steps.append(["config", "set", f"providers.{prov.hermes_name}.default_model", free_models[0]["id"]])
        for step in steps:
            if _hermes(*step) != 0:
                print(f"⚠ Failed to configure {prov.name}", file=sys.stderr)
                return 1
        print(f"✓ Configured {prov.name} ({len(free_models)} free models)")

    # Set first free model as default
    first_free = None
    for prov in PROVIDERS:
        free_m = [m for m in prov.models if m["tier"] == "free"]
        if free_m:
            first_free = (prov, free_m[0])
            break
    if first_free:
        prov, model = first_free
        steps = [
            ["config", "set", "model.provider", prov.hermes_name],
            ["config", "set", "model.default", model["id"]],
            ["config", "set", "model.base_url", prov.base_url],
        ]
        for step in steps:
            if _hermes(*step) != 0:
                return 1
        print(f"✓ Default model set to {model['id']}")

    print("Done. Start a new Hermes session or restart to apply.")
    return 0


def cmd_switch(args: argparse.Namespace) -> int:
    """Switch to a specific model across any provider."""
    model_id = args.model
    prov, model = _find_model(model_id)
    if not prov or not model:
        print(f"✗ Model '{model_id}' not found. Use 'freeride list' to see available models.", file=sys.stderr)
        # Try partial match
        for p in PROVIDERS:
            for m in p.models:
                if model_id.lower() in m["id"].lower():
                    prov, model = p, m
                    break
            if prov:
                break
        if not prov:
            return 1
        print(f"  Did you mean '{model['id']}'?")

    if not _require_key(prov.env_var):
        print(f"✗ {prov.env_var} is not set — cannot use {prov.name}", file=sys.stderr)
        return 1

    steps = [
        ["config", "set", "model.provider", prov.hermes_name],
        ["config", "set", "model.default", model["id"]],
        ["config", "set", "model.base_url", prov.base_url],
        ["config", "set", f"providers.{prov.hermes_name}.default_model", model["id"]],
        ["config", "set", f"providers.{prov.hermes_name}.base_url", prov.base_url],
    ]
    if prov.env_var:
        steps.append(["config", "set", f"providers.{prov.hermes_name}.api_key_env_var", prov.env_var])
    for step in steps:
        if _hermes(*step) != 0:
            return 1

    ctx_str = f"{model['context_length']:,}"
    print(f"✓ Switched to {model['id']} ({model['label']})")
    print(f"  Provider: {prov.name}  |  Context: {ctx_str}  |  Tier: {model['tier']}")
    print(f"  Env var: {prov.env_var}")
    print("  Start a new session or restart Hermes to apply.")
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    """Show current Hermes provider/model and available fallbacks."""
    return _hermes("config", "check")


# ── Parser ────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="freeride",
        description="Multi-provider free-model manager for Hermes (OpenRouter + OpenCode Zen + more)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    for name, fn, help_text in [
        ("auto", cmd_auto, "Configure all free providers in Hermes"),
        ("list", cmd_list, "List all available models with context size"),
        ("free", cmd_free, "Show only free-tier models"),
        ("status", cmd_status, "Show current Hermes config / provider"),
    ]:
        sp = sub.add_parser(name, help=help_text)
        sp.set_defaults(func=fn)
        if name in ("list", "free"):
            sp.add_argument("--provider", "-p", help="Filter by provider name")

    sp = sub.add_parser("switch", help="Switch to a specific model (auto-detects provider)")
    sp.add_argument("model", help="Model ID or partial name (e.g. 'big-pickle', 'owl-alpha')")
    sp.set_defaults(func=cmd_switch)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
