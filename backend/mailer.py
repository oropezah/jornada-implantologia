import logging
import os
from html import escape
import resend

log = logging.getLogger("jornada.mail")

EVENT = "III Jornada de Actualización en Implantología Bucal"
IG_URL = "https://instagram.com/synco.ia"


def _first(name: str) -> str:
    parts = name.split()
    return parts[0] if parts else name


def _row(label: str, value: str) -> str:
    return f"""\
<tr>
  <td style="padding:12px 16px;color:#64748b;font-size:13px;border-bottom:1px solid #e2e8f0;font-weight:500">{label}</td>
  <td style="padding:12px 16px;text-align:right;font-weight:600;color:#0f172a;font-size:13px;border-bottom:1px solid #e2e8f0">{escape(value)}</td>
</tr>"""


def _html(d: dict) -> str:
    first = escape(_first(d["nombre"]))
    rows = (
        _row("Nombre completo", d["nombre"])
        + _row("Cédula de identidad", d["cedula"])
        + _row("Teléfono", d["telefono"])
        + _row("Condición", d["institucion"])
    )
    return f"""\
<!DOCTYPE html>
<html lang="es" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="color-scheme" content="light">
  <meta name="supported-color-schemes" content="light">
  <title>{EVENT}</title>
  <style>
    :root {{ color-scheme: light; supported-color-schemes: light; }}
    body {{ margin: 0 !important; padding: 0 !important; width: 100% !important; background-color: #f8fafc !important; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
    table {{ border-collapse: collapse !important; mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
    img {{ border: 0; line-height: 100%; outline: none; text-decoration: none; }}
  </style>
</head>
<body style="margin:0;padding:0;background-color:#f8fafc;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif">
  
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="width:100%;background-color:#f8fafc;margin:0;padding:24px 0">
    <tr>
      <td align="center" style="padding:0">
        
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="width:100%;max-width:560px;background-color:#ffffff;margin:0 auto;border-radius:16px;border:1px solid #e2e8f0;overflow:hidden">
          
          <tr>
            <td style="padding:32px 32px 24px;border-bottom:1px solid #f1f5f9">
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="vertical-align:top">
                    <div style="font-size:10px;font-weight:700;color:#0082c8;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:6px">
                      UNIVERSIDAD DE CARABOBO
                    </div>
                    <div style="font-size:18px;font-weight:800;color:#1c2a39;letter-spacing:-0.02em;line-height:1.2;text-transform:uppercase">
                      III JORNADA DE IMPLANTOLOGÍA
                    </div>
                  </td>
                  <td align="right" style="vertical-align:top;width:48px">
                    <div style="width:44px;height:44px;background-color:#f0f9ff;border-radius:12px;border:1px solid #bae6fd;display:inline-block;text-align:center;line-height:44px">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none;margin-top:10px" style="vertical-align:middle">
                        <path d="M7 3C5.5 3 4.5 4.5 4.5 6C4.5 8.5 6 10 7.5 11C8.5 11.7 9 12.5 9 13.5V14H15V13.5C15 12.5 15.5 11.7 16.5 11C18 10 19.5 8.5 19.5 6C19.5 4.5 18.5 3 17 3C15 3 14 5 12 5C10 5 9 3 7 3Z" stroke="#0082c8" stroke-width="1.6" stroke-linejoin="round"/>
                        <path d="M9 14H15M9 16.5H15M10 19H14M11 21.5H13" stroke="#0082c8" stroke-width="1.6" stroke-linecap="round"/>
                      </svg>
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <tr>
            <td style="padding:28px 32px">
              
              <h2 style="font-size:20px;font-weight:700;color:#0f172a;margin:0 0 8px;letter-spacing:-0.02em">
                &iexcl;Hola, {first}!
              </h2>
              <p style="color:#64748b;font-size:14px;line-height:1.6;margin:0 0 24px">
                Hemos recibido tu solicitud de registro. Tu comprobante de pago est&aacute; en proceso de verificaci&oacute;n por nuestro equipo.
              </p>

              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color:#f8fafc;border-radius:12px;border:1px solid #e2e8f0;margin-bottom:24px">
                <tr>
                  <td style="padding:16px 20px">
                    <div style="font-size:10px;font-weight:700;color:#0082c8;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px">
                      EVENTO PRESENCIAL
                    </div>
                    <div style="font-size:15px;font-weight:700;color:#0f172a;margin-bottom:2px">
                      21 de Noviembre 2026
                    </div>
                    <div style="font-size:13px;color:#64748b">
                      Instituto Docente de Urolog&iacute;a
                    </div>
                  </td>
                </tr>
              </table>

              <div style="font-size:11px;font-weight:700;color:#0f172a;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px">
                RESUMEN DE REGISTRO
              </div>
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="width:100%;border-collapse:collapse;margin-bottom:24px;border:1px solid #e2e8f0;border-radius:8px;overflow:hidden">
                {rows}
              </table>

              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color:#fffbebf5;border:1px solid #fef3c7;border-radius:10px;margin-bottom:24px">
                <tr>
                  <td style="padding:12px 16px">
                    <p style="margin:0;font-size:13px;color:#92400e;line-height:1.5">
                      <strong>Estatus:</strong> Comprobante en revisión. Una vez verificado el pago te enviaremos tu confirmación oficial por este medio.
                    </p>
                  </td>
                </tr>
              </table>

              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="border-top:1px solid #f1f5f9;padding-top:20px">
                <tr>
                  <td align="center">
                    <p style="margin:0 0 4px;font-size:12px;color:#94a3b8">
                      III Jornada de Actualizaci&oacute;n en Implantolog&iacute;a Bucal &bull; UC
                    </p>
                    <p style="margin:0;font-size:11px;color:#cbd5e1">
                      Desarrollado por <a href="{IG_URL}" style="color:#0082c8;font-weight:600;text-decoration:none">Synco</a>
                    </p>
                  </td>
                </tr>
              </table>

            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>

</body>
</html>"""


def send_confirmation_email(d: dict) -> None:
    try:
        resend.api_key = os.environ.get("RESEND_API_KEY")
        first = _first(d["nombre"])

        text = (
            "Hola " + first + ", tu inscripción a la " + EVENT
            + " quedó agendada para el 21 de noviembre de 2026.\n"
            + "Hemos recibido tu comprobante de pago. Verificaremos los datos y te confirmaremos en breve.\n\n"
            + "Este reporte fue hecho por Synco (" + IG_URL + ")"
        )

        params = {
            "from": f"{EVENT} <onboarding@resend.dev>",
            "to": [d["correo"]],
            "subject": f"Confirmación de inscripción · {EVENT}",
            "text": text,
            "html": _html(d),
        }

        resend.Emails.send(params)
        log.info("Correo enviado exitosamente vía Resend API a %s", d.get("correo"))

    except Exception:
        log.exception("No se pudo enviar el correo a %s", d.get("correo"))


def _html_verified(d: dict) -> str:
    first = escape(_first(d["nombre"]))
    rows = (
        _row("Nombre completo", d["nombre"])
        + _row("Cédula de identidad", d["cedula"])
        + _row("Teléfono", d["telefono"])
        + _row("Condición", d["institucion"])
    )
    return f"""\
<!DOCTYPE html>
<html lang="es" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="color-scheme" content="light">
  <meta name="supported-color-schemes" content="light">
  <title>{EVENT}</title>
  <style>
    :root {{ color-scheme: light; supported-color-schemes: light; }}
    body {{ margin: 0 !important; padding: 0 !important; width: 100% !important; background-color: #f8fafc !important; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
    table {{ border-collapse: collapse !important; mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
    img {{ border: 0; line-height: 100%; outline: none; text-decoration: none; }}
  </style>
</head>
<body style="margin:0;padding:0;background-color:#f8fafc;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif">
  
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="width:100%;background-color:#f8fafc;margin:0;padding:24px 0">
    <tr>
      <td align="center" style="padding:0">
        
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="width:100%;max-width:560px;background-color:#ffffff;margin:0 auto;border-radius:16px;border:1px solid #e2e8f0;overflow:hidden">
          
          <tr>
            <td style="padding:32px 32px 24px;border-bottom:1px solid #f1f5f9">
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="vertical-align:top">
                    <div style="font-size:10px;font-weight:700;color:#0082c8;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:6px">
                      UNIVERSIDAD DE CARABOBO
                    </div>
                    <div style="font-size:18px;font-weight:800;color:#1c2a39;letter-spacing:-0.02em;line-height:1.2;text-transform:uppercase">
                      III JORNADA DE IMPLANTOLOGÍA
                    </div>
                  </td>
                  <td align="right" style="vertical-align:top;width:48px">
                    <div style="width:44px;height:44px;background-color:#f0f9ff;border-radius:12px;border:1px solid #bae6fd;display:inline-block;text-align:center;line-height:44px">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none;margin-top:10px" style="vertical-align:middle">
                        <path d="M7 3C5.5 3 4.5 4.5 4.5 6C4.5 8.5 6 10 7.5 11C8.5 11.7 9 12.5 9 13.5V14H15V13.5C15 12.5 15.5 11.7 16.5 11C18 10 19.5 8.5 19.5 6C19.5 4.5 18.5 3 17 3C15 3 14 5 12 5C10 5 9 3 7 3Z" stroke="#0082c8" stroke-width="1.6" stroke-linejoin="round"/>
                        <path d="M9 14H15M9 16.5H15M10 19H14M11 21.5H13" stroke="#0082c8" stroke-width="1.6" stroke-linecap="round"/>
                      </svg>
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <tr>
            <td style="padding:28px 32px">
              
              <div style="margin-bottom:20px">
                <span style="display:inline-block;background-color:#ecfdf5;color:#059669;border:1px solid #a7f3d0;font-size:11px;font-weight:700;padding:4px 12px;border-radius:20px;text-transform:uppercase;letter-spacing:0.05em">
                  &check; Pago Verificado &bull; Inscripción Confirmada
                </span>
              </div>

              <h2 style="font-size:20px;font-weight:700;color:#0f172a;margin:0 0 8px;letter-spacing:-0.02em">
                &iexcl;Todo listo, {first}!
              </h2>
              <p style="color:#64748b;font-size:14px;line-height:1.6;margin:0 0 24px">
                Hemos verificado exitosamente tu pago. Tu cupo para la jornada est&aacute; oficialmente reservado.
              </p>

              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color:#f8fafc;border-radius:12px;border:1px solid #e2e8f0;margin-bottom:24px">
                <tr>
                  <td style="padding:16px 20px">
                    <div style="font-size:10px;font-weight:700;color:#0082c8;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px">
                      EVENTO PRESENCIAL
                    </div>
                    <div style="font-size:15px;font-weight:700;color:#0f172a;margin-bottom:2px">
                      21 de Noviembre 2026
                    </div>
                    <div style="font-size:13px;color:#64748b">
                      Instituto Docente de Urolog&iacute;a
                    </div>
                  </td>
                </tr>
              </table>

              <div style="font-size:11px;font-weight:700;color:#0f172a;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px">
                DATOS DEL PARTICIPANTE
              </div>
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="width:100%;border-collapse:collapse;margin-bottom:24px;border:1px solid #e2e8f0;border-radius:8px;overflow:hidden">
                {rows}
              </table>

              <p style="color:#64748b;font-size:13px;line-height:1.5;margin:0 0 24px">
                Guarda este correo electr&oacute;nico como tu comprobante digital para la acreditaci&oacute;n el d&iacute;a del evento.
              </p>

              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="border-top:1px solid #f1f5f9;padding-top:20px">
                <tr>
                  <td align="center">
                    <p style="margin:0 0 4px;font-size:12px;color:#94a3b8">
                      III Jornada de Actualizaci&oacute;n en Implantolog&iacute;a Bucal &bull; UC
                    </p>
                    <p style="margin:0;font-size:11px;color:#cbd5e1">
                      Desarrollado por <a href="{IG_URL}" style="color:#0082c8;font-weight:600;text-decoration:none">Synco</a>
                    </p>
                  </td>
                </tr>
              </table>

            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>

</body>
</html>"""


def send_verified_email(d: dict) -> None:
    try:
        resend.api_key = os.environ.get("RESEND_API_KEY")
        first = _first(d["nombre"])

        text = (
            f"¡Hola {first}! Tu pago para la {EVENT} ha sido VERIFICADO exitosamente.\n"
            "Tu cupo está oficialmente reservado para este 21 de noviembre de 2026."
        )

        params = {
            "from": f"{EVENT} <onboarding@resend.dev>",
            "to": [d["correo"]],
            "subject": f"¡Pago Verificado! Tu inscripción está confirmada · {EVENT}",
            "text": text,
            "html": _html_verified(d),
        }

        resend.Emails.send(params)
        log.info("Correo de verificación enviado a %s", d.get("correo"))
    except Exception:
        log.exception("Error enviando correo de pago verificado a %s", d.get("correo"))