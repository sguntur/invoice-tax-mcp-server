
from __future__ import annotations

import os
import time
from pathlib import Path
from threading import Lock
from typing import Any, Dict

import yaml


_CONFIG_CACHE: Dict[str, Any] | None = None
_CONFIG_MTIME: float | None = None
_CONFIG_LOADED_AT: float | None = None
_LOCK = Lock()


def get_config_path() -> Path:
    return Path(os.getenv("TAX_RULES_PATH", "config/tax_rules.yaml"))


def load_tax_rules() -> Dict[str, Any]:
    """Load and cache tax rules. Cache persists during warm Lambda execution."""
    global _CONFIG_CACHE, _CONFIG_MTIME, _CONFIG_LOADED_AT

    path = get_config_path()
    if not path.exists():
        raise FileNotFoundError(f"Tax rules file not found: {path}")

    mtime = path.stat().st_mtime

    with _LOCK:
        if _CONFIG_CACHE is not None and _CONFIG_MTIME == mtime:
            return _CONFIG_CACHE

        with path.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        if not isinstance(config, dict):
            raise ValueError("Tax rules config must be a YAML mapping.")

        if "regions" not in config or "oversight" not in config:
            raise ValueError("Tax rules config must include 'regions' and 'oversight'.")

        _CONFIG_CACHE = config
        _CONFIG_MTIME = mtime
        _CONFIG_LOADED_AT = time.time()
        return config
