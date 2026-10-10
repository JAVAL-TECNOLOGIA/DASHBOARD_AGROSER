import os
from pathlib import Path
import logging

import requests
from django.conf import settings


class IdentityLookupError(Exception):
    pass


logger = logging.getLogger(__name__)


def _token_file_candidates():
    configured = str(getattr(settings, "APIPERU_TOKEN_FILE", "") or "").strip()
    candidates = []
    if configured:
        candidates.append(Path(configured))
    candidates.extend([
        Path(settings.BASE_DIR) / "runtime_secrets" / "apiperu.token",
        Path(r"C:\ProgramData\Agroservice\apiperu.token"),
    ])
    return tuple(dict.fromkeys(candidates))


def _api_token():
    token = os.getenv("APIPERU_TOKEN", "").strip()
    if token:
        return token
    for token_file in _token_file_candidates():
        try:
            if token_file.is_file():
                token = token_file.read_text(encoding="utf-8").strip()
                if token:
                    return token
        except OSError:
            logger.warning("No se pudo leer el archivo de credenciales de API Peru: %s", token_file)
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
