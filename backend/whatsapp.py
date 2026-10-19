import logging
import os
import requests

log = logging.getLogger("jornada.whatsapp")

YCLOUD_API_KEY = os.environ.get("YCLOUD_API_KEY")
ADMIN_PHONE = os.environ.get("ADMIN_WHATSAPP_PHONE")  # Ejemplo: "+584144000000"
YCLOUD_FROM = os.environ.get("YCLOUD_WHATSAPP_NUMBER", "")  # Tu número emisor registrado en YCloud


def send_admin_whatsapp_notification(data: dict) -> None:
    """
    Envía una notificación al administrador vía YCloud (WhatsApp API)
    usando la plantilla aprobada 'registro_implantologia'.
    """
    if not YCLOUD_API_KEY or not ADMIN_PHONE:
        log.warning("YCloud API Key o ADMIN_WHATSAPP_PHONE no configurados. Omitiendo WhatsApp.")
        return

    url = "https://api.ycloud.com/v2/whatsapp/messages"
    
    headers = {
        "X-API-Key": YCLOUD_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "from": YCLOUD_FROM,
        "to": ADMIN_PHONE,
        "type": "template",
        "template": {
            "name": "registro_implantologia",
            "language": {
                "code": "es"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": str(data.get("nombre", "N/A"))},
                        {"type": "text", "text": str(data.get("cedula", "N/A"))},
                        {"type": "text", "text": str(data.get("telefono", "N/A"))},
                        {"type": "text", "text": str(data.get("institucion", "N/A"))},
                        {"type": "text", "text": str(data.get("correo", "N/A"))}
                    ]
                }
            ]
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in (200, 201):
            log.info("Notificación de WhatsApp enviada al administrador exitosamente.")
        else:
            log.error("Error al enviar WhatsApp vía YCloud (%s): %s", response.status_code, response.text)
    except Exception:
        log.exception("Excepción al intentar enviar mensaje por YCloud")