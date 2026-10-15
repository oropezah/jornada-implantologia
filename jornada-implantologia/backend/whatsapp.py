import logging
import os
import requests

log = logging.getLogger("jornada.whatsapp")

YCLOUD_API_KEY = os.environ.get("YCLOUD_API_KEY")
FROM_PHONE = os.environ.get("YCLOUD_FROM_PHONE", "584221638753")
ADMIN_PHONE = os.environ.get("ADMIN_WHATSAPP_PHONE", "584144099988").replace("+", "").strip()


def notify_whatsapp(data: dict) -> None:
    """
    Función invocada como BackgroundTask desde main.py.
    Envía notificación de WhatsApp al administrador vía YCloud.
    """
    print("--------------------------------------------------")
    print(">>> EJECUTANDO NOTIFY_WHATSAPP <<<")
    print(f"YCLOUD_API_KEY presente: {bool(YCLOUD_API_KEY)}")
    print(f"From: {FROM_PHONE} | To: {ADMIN_PHONE}")
    print("--------------------------------------------------")

    if not YCLOUD_API_KEY:
        log.warning("YCLOUD_API_KEY no configurada. Omitiendo notificación de WhatsApp.")
        return

    url = "https://api.ycloud.com/v2/whatsapp/messages"

    headers = {
        "X-API-Key": YCLOUD_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "from": FROM_PHONE,
        "to": ADMIN_PHONE,
        "type": "template",
        "template": {
            "name": "registro_implantologia",
            "language": {"code": "es"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": str(data.get("nombre", "N/A"))},
                        {"type": "text", "text": str(data.get("cedula", "N/A"))},
                        {"type": "text", "text": str(data.get("telefono", "N/A"))},
                        {"type": "text", "text": str(data.get("institucion", "N/A"))},
                        {"type": "text", "text": str(data.get("correo", "N/A"))},
                    ],
                }
            ],
        },
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f">>> YCLOUD RESPUESTA STATUS: {response.status_code}")
        print(f">>> YCLOUD RESPUESTA BODY: {response.text}")
        
        if response.status_code in (200, 201):
            log.info("Notificación de WhatsApp enviada al admin exitosamente.")
        else:
            log.error("Error al enviar WhatsApp vía YCloud (%s): %s", response.status_code, response.text)
    except Exception as e:
        log.exception("Excepción al intentar enviar mensaje por YCloud")