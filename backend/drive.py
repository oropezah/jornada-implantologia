import base64
import logging
import os
import re
import requests

log = logging.getLogger("jornada.drive")


class DriveUploadError(Exception):
    pass


def upload_receipt(content: bytes, mime: str, cedula: str, nombre: str) -> str:
    url = os.environ.get("DRIVE_UPLOAD_URL", "").strip()
    secret = os.environ.get("DRIVE_UPLOAD_SECRET", "").strip()

    if not url:
        raise DriveUploadError("DRIVE_UPLOAD_URL no está configurada en las variables de entorno.")

    safe_nombre = re.sub(r"[^A-Za-z0-9_-]+", "_", nombre).strip("_")[:40] or "asistente"
    ext = {"image/png": "png", "image/webp": "webp", "image/heic": "heic"}.get(mime, "jpg")

    payload = {
        "secret": secret,
        "filename": f"{cedula}_{safe_nombre}.{ext}",
        "mimeType": mime,
        "data": base64.b64encode(content).decode("ascii"),
    }

    try:
        # Usamos requests que maneja correctamente los redirects POST de Google Apps Script
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()

        # Intentar parsear el JSON de Apps Script
        try:
            data = resp.json()
        except Exception:
            log.error(f"Apps Script no devolvió un JSON válido. Respuesta recibida: {resp.text}")
            raise DriveUploadError("Google Apps Script respondió con un formato no válido.")

        if not data.get("ok"):
            error_msg = data.get("error", "Error desconocido subiendo a Drive")
            log.error(f"Error desde Google Apps Script: {error_msg}")
            raise DriveUploadError(error_msg)

        return data["url"]

    except requests.RequestException as e:
        log.exception(f"Excepción HTTP al subir a Drive: {e}")
        raise DriveUploadError(f"Error de conexión con Google Drive: {e}")