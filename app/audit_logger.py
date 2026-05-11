
from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Dict

from app.logging_config import logger


_EXECUTOR = ThreadPoolExecutor(max_workers=int(os.getenv("AUDIT_WORKERS", "2")))


def _write_audit_event(record: Dict[str, Any]) -> None:
    """Write audit event. CloudWatch JSON logging is default; DynamoDB can be added by env."""
    logger.info(
        "audit_event",
        extra={
            "event_type": record.get("event_type"),
            "calculation_id": record.get("calculation_id"),
            "invoice_id": record.get("invoice_id"),
            "audit_record": record,
        },
    )

    # Optional local audit file for development only.
    audit_path = os.getenv("LOCAL_AUDIT_FILE")
    if audit_path:
        with open(audit_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")


def publish_audit_event(record: Dict[str, Any]) -> None:
    """Non-blocking audit publishing for performance-sensitive Lambda execution."""
    _EXECUTOR.submit(_write_audit_event, record)


def build_audit_record(
    *,
    calculation_id: str,
    invoice_id: str,
    region: str,
    request: Dict[str, Any],
    response: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "event_type": "INVOICE_TAX_CALCULATED",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "calculation_id": calculation_id,
        "invoice_id": invoice_id,
        "region": region,
        "request": request,
        "response": response,
    }
