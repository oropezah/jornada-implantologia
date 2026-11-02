"""Aviso por WhatsApp al estudio (YCloud) · opcional. Misma plantilla `cita_mocca` que usaba n8n."""

import logging

import httpx

from . import config
from .emailer import CitaView, fecha_larga

log = logging.getLogger("mocca.whatsapp")


def notify_studio(v: CitaView) -> None:
    if not (config.YCLOUD_API_KEY and config.YCLOUD_FROM and config.YCLOUD_TO):
        return
    for i in v.items:
        params = [
            v.nombre,
            v.telefono,
            "N/A",  # cédula: el formulario actual ya no la pide, la plantilla sí la espera
            v.fecha_nacimiento or "N/A",
            i.servicio,
            i.staff,
            fecha_larga(v.fecha),
            v.horario,
        ]
        body = {
            "type": "template",
            "template": {
                "name": config.YCLOUD_TEMPLATE,
                "language": {"code": "es"},
                "components": [{"type": "body", "parameters": [{"type": "text", "text": p} for p in params]}],
            },
            "from": config.YCLOUD_FROM,
            "to": config.YCLOUD_TO,
        }
        r = httpx.post(
            "https://api.ycloud.com/v2/whatsapp/messages/sendDirectly",
            headers={"X-API-Key": config.YCLOUD_API_KEY, "accept": "application/json"},
            json=body,
            timeout=20,
        )
        if r.status_code >= 400:
            log.error("YCloud %s: %s", r.status_code, r.text)
