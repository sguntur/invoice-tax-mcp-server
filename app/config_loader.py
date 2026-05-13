from __future__ import annotations

import os
import time
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Tuple

import boto3
import yaml

_CONFIG_CACHE: Dict[str, Any] | None = None
_CONFIG_VERSION: str | None = None
_CONFIG_SOURCE: str | None = None
_CONFIG_LOADED_AT: float | None = None
_LOCK = Lock()


def get_config_path() -> Path:
    return Path(os.getenv("TAX_RULES_PATH", "config/tax_rules.yaml"))


def get_cache_ttl_seconds() -> int:
    return int(os.getenv("TAX_RULES_CACHE_TTL_SECONDS", "60"))


def get_s3_bucket() -> str | None:
    return os.getenv("TAX_RULES_S3_BUCKET")


def get_s3_key() -> str:
    return os.getenv("TAX_RULES_S3_KEY", "tax_rules.yaml")


def _validate_config(config: Dict[str, Any]) -> None:
    if "regions" not in config:
        raise ValueError("Missing regions config")
    if "oversight" not in config:
        raise ValueError("Missing oversight config")


def _load_local_yaml() -> Tuple[Dict[str, Any], str, str]:
    path = get_config_path()

    with path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config, str(path.stat().st_mtime), f"local:{path}"


def _load_s3_yaml() -> Tuple[Dict[str, Any], str, str]:
    bucket = get_s3_bucket()
    key = get_s3_key()

    if not bucket:
        return _load_local_yaml()

    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket, Key=key)

    raw_yaml = response["Body"].read().decode("utf-8")
    config = yaml.safe_load(raw_yaml)

    version = (
        response.get("VersionId")
        or response.get("ETag")
        or str(response.get("LastModified"))
    )

    return config, str(version), f"s3://{bucket}/{key}"


def load_tax_rules() -> Dict[str, Any]:
    global _CONFIG_CACHE, _CONFIG_VERSION, _CONFIG_SOURCE, _CONFIG_LOADED_AT

    now = time.time()
    ttl_seconds = get_cache_ttl_seconds()

    with _LOCK:
        if (
            _CONFIG_CACHE is not None
            and _CONFIG_LOADED_AT is not None
            and now - _CONFIG_LOADED_AT < ttl_seconds
        ):
            return _CONFIG_CACHE

        config, version, source = _load_s3_yaml()

        _validate_config(config)

        _CONFIG_CACHE = config
        _CONFIG_VERSION = version
        _CONFIG_SOURCE = source
        _CONFIG_LOADED_AT = now

        return config
