from typing import Any

import requests

from app.config import get_settings


def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict[str, Any]:
    """Call a public JSON REST API for a small, useful agent tool demo."""
    settings = get_settings()
    response = requests.get(
        f"{settings.frankfurter_base_url}/latest",
        params={
            "amount": amount,
            "from": from_currency.upper(),
            "to": to_currency.upper(),
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
