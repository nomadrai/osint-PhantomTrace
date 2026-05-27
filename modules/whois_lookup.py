from typing import Any, Dict

import whois


def _format_value(value: Any) -> Any:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return value


def lookup_domain(domain: str) -> Dict[str, Any]:
    try:
        data = whois.whois(domain)
    except Exception as exc:
        return {
            "error": f"WHOIS lookup failed: {exc}",
            "domain_name": domain,
            "registrar": None,
            "creation_date": None,
            "expiration_date": None,
            "updated_date": None,
            "name_servers": None,
            "status": None,
            "emails": None,
        }

    return {
        "error": None,
        "domain_name": _format_value(data.domain_name),
        "registrar": data.registrar,
        "creation_date": _format_value(data.creation_date),
        "expiration_date": _format_value(data.expiration_date),
        "updated_date": _format_value(data.updated_date),
        "name_servers": _format_value(data.name_servers),
        "status": _format_value(data.status),
        "emails": _format_value(data.emails),
    }
