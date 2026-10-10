import os
from pathlib import Path

import requests
from django.conf import settings


class IdentityLookupError(Exception):
    pass


def _api_token():
    token = os.getenv("APIPERU_TOKEN", "").strip()
    token_file = Path(getattr(settings, "APIPERU_TOKEN_FILE", ""))
    if not token and token_file.is_file():
        token = token_file.read_text(encoding="utf-8").strip()
    if not token:
        raise IdentityLookupError("La consulta de identidad no está configurada.")
    return token


def lookup_dni(dni):
    try:
        response = requests.post(
            getattr(settings, "APIPERU_DNI_URL", "https://api.apiperu.dev/dni"),
            headers={
                "Accept": "application/json",
                "Authorization": "Bearer {}".format(_api_token()),
                "Content-Type": "application/json",
            },
            json={"dni": dni},
            timeout=12,
        )
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise IdentityLookupError("No fue posible consultar el DNI en este momento.") from exc
    if response.status_code != 200 or not payload.get("success"):
        raise IdentityLookupError(payload.get("message") or "No se encontró el DNI.")
    data = payload.get("data") or {}
    return {
        "document": str(data.get("numero") or dni),
        "first_names": data.get("nombres") or "",
        "paternal_surname": data.get("apellido_paterno") or "",
        "maternal_surname": data.get("apellido_materno") or "",
    }
