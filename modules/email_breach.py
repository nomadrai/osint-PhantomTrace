from typing import Dict, List, Optional

import requests


HIBP_ENDPOINT = "https://haveibeenpwned.com/api/v3/breachedaccount/{email}"


def check_breaches(
    email: str, api_key: Optional[str], user_agent: str
) -> Dict[str, object]:
    if not api_key:
        return {
            "error": "HIBP API key missing. Set HIBP_API_KEY in .env.",
            "status": None,
            "breaches": [],
        }

    headers = {"hibp-api-key": api_key, "user-agent": user_agent}
    params = {"truncateResponse": "false"}
    try:
        response = requests.get(
            HIBP_ENDPOINT.format(email=email),
            headers=headers,
            params=params,
            timeout=10,
        )
    except requests.RequestException as exc:
        return {"status": None, "breaches": [], "error": str(exc)}

    if response.status_code == 200:
        breaches: List[Dict[str, object]] = response.json()
        return {"status": response.status_code, "breaches": breaches, "error": None}
    if response.status_code == 404:
        return {"status": response.status_code, "breaches": [], "error": None}

    return {
        "status": response.status_code,
        "breaches": [],
        "error": response.text or "Unexpected response from HIBP.",
    }
