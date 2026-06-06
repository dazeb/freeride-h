#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

import main as freeride
from main import PROVIDERS, Provider

STATE_FILE = Path.home() / ".hermes" / ".freeride-watcher-state.json"
DEFAULT_INTERVAL_SECONDS = 60
MIN_INTERVAL_SECONDS = 15


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content)
    tmp.replace(path)


def _load_state() -> dict:
    if not STATE_FILE.exists():
        return {"rotation_count": 0}
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {"rotation_count": 0}


def _save_state(state: dict) -> None:
    _atomic_write(STATE_FILE, json.dumps(state, indent=2))


def _hermes_config_get(key: str) -> str:
    proc = subprocess.run(["hermes", "config", "path"], capture_output=True, text=True)
    cfg = Path(proc.stdout.strip())
    if not cfg.exists():
        return ""
    try:
        import yaml
        data = yaml.safe_load(cfg.read_text()) or {}
    except Exception:
        return ""
    parts = key.split(".")
    cur = data
    for part in parts:
        if not isinstance(cur, dict) or part not in cur:
            return ""
        cur = cur[part]
    return str(cur) if cur is not None else ""


def _all_free_model_ids() -> list[tuple[str, Provider]]:
    """Return list of (model_id, provider) for all free models across all providers."""
    result: list[tuple[str, Provider]] = []
    for prov in PROVIDERS:
        for m in prov.models:
            if m["tier"] == "free":
                result.append((m["id"], prov))
    return result


def _pick_next_model(current: str | None) -> tuple[str, Provider] | None:
    all_models = _all_free_model_ids()
    if not all_models:
        return None
    for i, (mid, prov) in enumerate(all_models):
        if current and (mid == current or mid.split("/", 1)[-1] == current.split("/", 1)[-1]):
            next_idx = (i + 1) % len(all_models)
            return all_models[next_idx]
    return all_models[0]


def _set_model(model_id: str, prov: Provider) -> int:
    steps = [
        ["config", "set", "model.provider", prov.hermes_name],
        ["config", "set", "model.default", model_id],
        ["config", "set", "model.base_url", prov.base_url],
        ["config", "set", f"providers.{prov.hermes_name}.base_url", prov.base_url],
        ["config", "set", f"providers.{prov.hermes_name}.api_key_env_var", prov.env_var],
        ["config", "set", f"providers.{prov.hermes_name}.default_model", model_id],
    ]
    for step in steps:
        if subprocess.call(["hermes", *step]) != 0:
            return 1
    return 0


def _record_rotation(state: dict, reason: str, model: str, prov: Provider | None = None) -> None:
    state["rotation_count"] = state.get("rotation_count", 0) + 1
    state["last_rotation_at"] = datetime.now().isoformat()
    state["last_rotation_reason"] = reason
    state["last_model"] = model
    state["last_provider"] = prov.hermes_name if prov else "unknown"
    _save_state(state)


def _resolve_provider_for_model(model_id: str) -> Provider | None:
    """Find which provider owns a given model ID."""
    for prov in PROVIDERS:
        for m in prov.models:
            if m["id"] == model_id or m["id"].split("/", 1)[-1] == model_id.split("/", 1)[-1]:
                return prov
    return None


def _resolve_api_key(env_var: str) -> str:
    key = os.getenv(env_var) or ""
    if not key:
        env_path = Path.home() / ".hermes" / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith(f"{env_var}="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    return key


def _probe_model(model_id: str, timeout_s: int = 20) -> tuple[bool, float]:
    prov = _resolve_provider_for_model(model_id)
    if not prov:
        return False, float("inf")
    key = _resolve_api_key(prov.env_var)
    if not key:
        return False, float("inf")
    payload = json.dumps({
        "model": model_id,
        "messages": [{"role": "user", "content": "Reply with exactly: pong"}],
        "temperature": 0,
        "max_tokens": 8,
    }).encode()
    req = urllib.request.Request(
        f"{prov.base_url.rstrip('/')}/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Shaivpidadi/FreeRide",
            "X-Title": "FreeRide Watcher",
        },
        method="POST",
    )
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return (200 <= resp.status < 300), time.monotonic() - start
    except Exception:
        return False, time.monotonic() - start


def check_and_rotate(state: dict, once: bool = False) -> bool:
    current = _hermes_config_get("model.default") or "openrouter/owl-alpha"
    ok, elapsed = _probe_model(current)
    if ok and elapsed < 12 and not once:
        return False

    next_item = _pick_next_model(current)
    if not next_item:
        print("No free models available.", file=sys.stderr)
        return False
    next_model, next_prov = next_item
    changed = _set_model(next_model, next_prov) == 0
    if changed:
        reason = "quota" if not ok else f"slow:{elapsed:.1f}s"
        _record_rotation(state, reason, next_model, next_prov)
        print(f"[{datetime.now().isoformat()}] switched to {next_model} ({next_prov.name}) — {reason}")
    return changed
def run_daemon(interval: int) -> None:
    interval = max(interval, MIN_INTERVAL_SECONDS)
    state = _load_state()
    print(f"FreeRide Watcher started (interval {interval}s)")
    while True:
        try:
            check_and_rotate(state)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] watcher error: {e}", file=sys.stderr)
        time.sleep(interval)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="freeride-watcher", description="Rotate Hermes between verified free OpenRouter models.")
    p.add_argument("--once", action="store_true")
    p.add_argument("--status", action="store_true")
    p.add_argument("--interval", "-i", type=int, default=DEFAULT_INTERVAL_SECONDS)
    args = p.parse_args(argv)
    state = _load_state()
    if args.status:
        print(json.dumps(state, indent=2))
        return 0
    if args.once:
        return 0 if check_and_rotate(state, once=True) else 0
    run_daemon(args.interval)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
