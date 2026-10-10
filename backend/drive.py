import base64
import logging
import os
import re

import httpx

log = logging.getLogger("jornada.drive")


class DriveUploadError(Exception):
    pass


def upload_receipt(content: bytes, mime: str, cedula: str, nombre: str) -> str:
    url = os.environ["DRIVE_UPLOAD_URL"]
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", nombre).strip("_")[:40] or "asistente"
    ext = {"image/png": "png", "image/webp": "webp", "image/heic": "heic"}.get(mime, "jpg")

    payload = {
        "secret": os.environ.get("DRIVE_UPLOAD_SECRET", ""),
        "filename": cedula + "_" + safe + "." + ext,
        "mimeType": mime,
        "data": base64.b64encode(content).decode("ascii"),
    }

    resp = httpx.post(url, json=payload, timeout=60, follow_redirects=True)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise DriveUploadError(str(data.get("error", "Error subiendo a Drive")))
    return data["url"]