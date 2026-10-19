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
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{EVENT}</title>
</head>
<body style="margin:0;padding:0;background-color:#f8fafc;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif">
  
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="width:100%;background-color:#f8fafc;margin:0;padding:24px 0">
    <tr>
      <td align="center" style="padding:0">
        
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="width:100%;max-width:580px;background-color:#ffffff;margin:0 auto;border-radius:16px;border:1px solid #e2e8f0;overflow:hidden">
          
          <!-- Encabezado con imagen oficial del diente -->
          <tr>
            <td style="padding:32px 32px 24px;border-bottom:1px solid #f1f5f9">
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="vertical-align:top">
                    <div style="font-size:11px;font-weight:800;color:#0082c8;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:4px">
                      UNIVERSIDAD DE CARABOBO
                    </div>
                    <div style="font-size:10px;font-weight:700;color:#0082c8;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px">
                      FACULTAD DE ODONTOLOGÍA
                    </div>
                    <div style="font-size:18px;font-weight:800;color:#1c2a39;letter-spacing:-0.01em;line-height:1.2;text-transform:uppercase">
                      III JORNADA
                    </div>
                    <div style="font-size:16px;font-weight:800;color:#0082c8;letter-spacing:-0.01em;line-height:1.2;text-transform:uppercase">
                      ACTUALIZACIÓN EN IMPLANTOLOGÍA BUCAL
                    </div>
                  </td>
                  <td align="right" style="vertical-align:top;width:56px;padding-left:12px">
                    <div style="width:52px;height:52px;background-color:#f0f9ff;border-radius:12px;border:1px solid #bae6fd;text-align:center">
                      <img src="https://www.svgrepo.com/show/352590/tooth.svg" width="30" height="30" alt="Diente" style="margin-top:11px;display:inline-block" />
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Contenido -->
          <tr>
            <td style="padding:28px 32px">
              
              <div style="margin-bottom:20px">
                <span style="display:inline-block;background-color:#ecfdf5;color:#059669;border:1px solid #a7f3d0;font-size:11px;font-weight:700;padding:6px 14px;border-radius:20px;text-transform:uppercase;letter-spacing:0.05em">
                  &#10003; PAGO VERIFICADO &bull; INSCRIPCIÓN CONFIRMADA
                </span>
              </div>

              <h2 style="font-size:20px;font-weight:700;color:#0f172a;margin:0 0 8px;letter-spacing:-0.02em">
                &iexcl;Pago Confirmado, {first}!
              </h2>
              <p style="color:#64748b;font-size:14px;line-height:1.6;margin:0 0 24px">
                Hemos validado exitosamente tu pago. Tu cupo para la <strong>III Jornada de Actualización en Implantología Bucal</strong> está oficialmente reservado y verificado.
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

              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color:#f0f9ff;border:1px solid #bae6fd;border-radius:10px;margin-bottom:24px">
                <tr>
                  <td style="padding:14px 18px">
                    <div style="font-size:11px;font-weight:800;color:#0082c8;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px">
                      REGISTRO &amp; ACCESO OFICIAL CONFIRMADO
                    </div>
                    <p style="margin:0;font-size:13px;color:#1e40af;line-height:1.5">
                      Guarda este correo electrónico. Te servirá como tu pase digital de acreditación en la entrada del evento.
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
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{EVENT}</title>
</head>
<body style="margin:0;padding:0;background-color:#f8fafc;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif">
  
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="width:100%;background-color:#f8fafc;margin:0;padding:24px 0">
    <tr>
      <td align="center" style="padding:0">
        
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="width:100%;max-width:580px;background-color:#ffffff;margin:0 auto;border-radius:16px;border:1px solid #e2e8f0;overflow:hidden">
          
          <!-- Encabezado -->
          <tr>
            <td style="padding:32px 32px 24px;border-bottom:1px solid #f1f5f9">
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="vertical-align:top">
                    <div style="font-size:11px;font-weight:800;color:#0082c8;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:4px">
                      UNIVERSIDAD DE CARABOBO
                    </div>
                    <div style="font-size:10px;font-weight:700;color:#0082c8;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px">
                      FACULTAD DE ODONTOLOGÍA
                    </div>
                    <div style="font-size:18px;font-weight:800;color:#1c2a39;letter-spacing:-0.01em;line-height:1.2;text-transform:uppercase">
                      III JORNADA
                    </div>
                    <div style="font-size:16px;font-weight:800;color:#0082c8;letter-spacing:-0.01em;line-height:1.2;text-transform:uppercase">
                      ACTUALIZACIÓN EN IMPLANTOLOGÍA BUCAL
                    </div>
                  </td>
                  <td align="right" style="vertical-align:top;width:56px;padding-left:12px">
                    <div style="width:52px;height:52px;background-color:#f0f9ff;border-radius:12px;border:1px solid #bae6fd;text-align:center">
                      <img src="https://www.svgrepo.com/show/352590/tooth.svg" width="30" height="30" alt="Diente" style="margin-top:11px;display:inline-block" />
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Contenido -->
          <tr>
            <td style="padding:28px 32px">
              
              <div style="margin-bottom:20px">
                <span style="display:inline-block;background-color:#ecfdf5;color:#059669;border:1px solid #a7f3d0;font-size:11px;font-weight:700;padding:6px 14px;border-radius:20px;text-transform:uppercase;letter-spacing:0.05em">
                  &#10003; PAGO VERIFICADO &bull; INSCRIPCIÓN CONFIRMADA
                </span>
              </div>

              <h2 style="font-size:20px;font-weight:700;color:#0f172a;margin:0 0 8px;letter-spacing:-0.02em">
                &iexcl;Pago Confirmado, {first}!
              </h2>
              <p style="color:#64748b;font-size:14px;line-height:1.6;margin:0 0 24px">
                Hemos validado exitosamente tu pago. Tu cupo para la <strong>III Jornada de Actualización en Implantología Bucal</strong> está oficialmente reservado y verificado.
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

              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color:#f0f9ff;border:1px solid #bae6fd;border-radius:10px;margin-bottom:24px">
                <tr>
                  <td style="padding:14px 18px">
                    <div style="font-size:11px;font-weight:800;color:#0082c8;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px">
                      REGISTRO &amp; ACCESO OFICIAL CONFIRMADO
                    </div>
                    <p style="margin:0;font-size:13px;color:#1e40af;line-height:1.5">
                      Guarda este correo electrónico. Te servirá como tu pase digital de acreditación en la entrada del evento.
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


def send_verified_email(d: dict) -> None:
    try:
        resend.api_key = os.environ.get("RESEND_API_KEY")
        first = _first(d["nombre"])

        text = (
            f"¡Pago Confirmado, {first}!\n"
            "Hemos validado exitosamente tu pago. Tu cupo para la III Jornada de Actualización en Implantología Bucal está oficialmente reservado y verificado.\n\n"
            "REGISTRO & ACCESO OFICIAL CONFIRMADO\n"
            "Guarda este correo electrónico. Te servirá como tu pase digital de acreditación en la entrada del evento."
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