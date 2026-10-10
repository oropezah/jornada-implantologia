import logging
import os

import httpx

log = logging.getLogger("jornada.whatsapp")


def notify_whatsapp(d: dict) -> None:
    url = os.getenv("WHATSAPP_WEBHOOK_URL")
    if not url:
        return
    try:
        headers = {}
        if os.getenv("WHATSAPP_WEBHOOK_SECRET"):
          headers["x-api-key"] = os.environ["WHATSAPP_WEBHOOK_SECRET"]
        first = (d["nombre"].split() or [d["nombre"]])[0]
        httpx.post(
            url,
            headers=headers,
            timeout=15,
            json={
                "telefono": d["telefono_wa"],
                "nombre": first,
                "mensaje": (
                    f"Hola {first}, recibimos tu inscripción a la III Jornada de Actualización en "
                    "Implantología Bucal (21 de noviembre). Por aquí te enviaremos los datos para realizar el pago."
                ),
            },
        ).raise_for_status()
    except Exception:
        log.exception("No se pudo notificar por WhatsApp a %s", d.get("telefono_wa"))
