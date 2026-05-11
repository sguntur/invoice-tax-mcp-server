from __future__ import annotations

import os
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from app.tax_engine import calculate_invoice_tax


def _csv_env(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


mcp = FastMCP(
    "invoice-tax-mcp-server",
    stateless_http=True,
    json_response=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=_csv_env(
            "MCP_ALLOWED_HOSTS",
            "localhost,localhost:*,127.0.0.1,127.0.0.1:*,m4g7x97otj.execute-api.us-east-1.amazonaws.com",
        ),
        allowed_origins=_csv_env(
            "MCP_ALLOWED_ORIGINS",
            "http://localhost,http://localhost:*,https://m4g7x97otj.execute-api.us-east-1.amazonaws.com",
        ),
    ),
)


@mcp.tool()
def calculate_invoice_tax_tool(invoice: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate invoice tax and return totals, line-level tax, and oversight signal."""
    return calculate_invoice_tax(invoice)


app = mcp.streamable_http_app()