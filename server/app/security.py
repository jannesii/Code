"""Security-related application setup (rate limiting, request filters)."""

from __future__ import annotations

import logging
from flask import request, current_app
from .extensions import limiter

logger = logging.getLogger(__name__)


def configure_rate_limiting(app) -> None:
    """Initialize Flask-Limiter and register a whitelist request filter.

    Whitelist supports:
      - Exact IP match, e.g. "127.0.0.1"
      - Wildcard suffix, e.g. "192.168.10.*"
      - CIDR ranges, e.g. "192.168.10.0/24"
    """
    limiter.init_app(app)

    try:
        from ipaddress import ip_address, ip_network
    except Exception:
        ip_address = ip_network = None  # type: ignore

    def _rate_limit_whitelist_filter() -> bool:
        try:
            addr_raw = request.headers.get('X-Forwarded-For', request.remote_addr)
            if not addr_raw:
                return False
            addr = str(addr_raw).split(',')[0].strip()
            wl = current_app.config.get('whitelist', []) or []
            for item in wl:
                s = str(item).strip()
                if not s:
                    continue
                if s.endswith('.*'):
                    if addr.startswith(s[:-1]):
                        return True
                    continue
                if '/' in s and ip_address and ip_network:
                    try:
                        if ip_address(addr) in ip_network(s, strict=False):
                            return True
                        continue
                    except Exception:
                        pass
                if addr == s:
                    return True
            return False
        except Exception:
            return False

    try:
        limiter.request_filter(_rate_limit_whitelist_filter)  # type: ignore[attr-defined]
    except Exception:
        pass

    logger.info(
        "Rate limiting enabled (whitelist size: %d)",
        len(app.config.get('whitelist', []) or [])
    )

