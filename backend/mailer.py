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
return f"""



{label}


{escape(value)}

"""

def _html(d: dict) -> str:
first_name = escape(_first(d["nombre"]))
full_name = d["nombre"]
cedula = d["cedula"]
telefono = d["telefono"]
institucion = d["institucion"]

rows = (
    _row("Nombre completo", full_name)
    + _row("Cédula de Identidad", cedula)
    + _row("Teléfono de contacto", telefono)
    + _row("Institución / Universidad", institucion)
)

return f"""\


      <!-- Header Banner with Gradient Accent -->
      <tr>
        <td style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 36px 32px 32px; color: #ffffff;">
          <!-- Pill Badge -->
          <div style="display: inline-block; background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 100px; padding: 4px 12px; margin-bottom: 16px;">
            <span style="color: #38bdf8; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em;">
              • Inscripción Registrada
            </span>
          </div>
          <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em; color: #94a3b8; margin-bottom: 6px;">
            Universidad de Carabobo
          </div>
          <h1 style="margin: 0; font-size: 24px; font-weight: 800; line-height: 1.25; letter-spacing: -0.02em; color: #ffffff;">
            {EVENT}
          </h1>
        </td>
      </tr>

      <!-- Body Content -->
      <tr>
        <td style="padding: 32px 32px 24px;">
          <p style="margin: 0 0 12px; font-size: 20px; font-weight: 700; letter-spacing: -0.01em; color: #0f172a;">
            ¡Hola, {first_name}! 👋
          </p>
          <p style="margin: 0 0 24px; font-size: 15px; line-height: 1.6; color: #475569;">
            Hemos recibido tu solicitud de inscripción y el comprobante adjunto. A continuación encontrarás el resumen de tu registro:
          </p>

          <!-- Ticket / Data Table Box -->
          <div style="background-color: #fafafa; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; margin-bottom: 24px;">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
              {rows}
            </table>
          </div>

          <!-- Event Details Pill Banner -->
          <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border: 1px solid #bae6fd; border-radius: 16px; padding: 18px 20px; margin-bottom: 24px;">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
              <tr>
                <td style="vertical-align: top; width: 28px; font-size: 18px; line-height: 1;">📅</td>
                <td style="font-size: 13px; line-height: 1.5; color: #0369a1;">
                  <strong style="color: #0c4a6e; font-size: 14px;">Fecha y Lugar</strong><br>
                  Sábado, 21 de noviembre de 2026<br>
                  Instituto Docente de Urología (IDU)
                </td>
              </tr>
            </table>
          </div>

          <!-- Verification Notice -->
          <p style="margin: 0; font-size: 13px; line-height: 1.6; color: #64748b; background-color: #f8fafc; border-left: 3px solid #38bdf8; padding: 12px 16px; border-radius: 0 8px 8px 0;">
            <strong style="color: #334155;">Siguiente paso:</strong> Nuestro equipo validará la acreditación de tu pago en Google Drive. Te enviaremos tu pase definitivo en cuanto sea confirmado.
          </p>
        </td>
      </tr>

      <!-- Footer Divider -->
      <tr>
        <td style="padding: 0 32px;">
          <div style="border-top: 1px solid #f1f5f9; width: 100%;"></div>
        </td>
      </tr>

      <!-- Clean Footer -->
      <tr>
        <td style="padding: 24px 32px 32px; text-align: center; background-color: #ffffff;">
          <p style="margin: 0 0 8px; font-size: 12px; color: #94a3b8;">
            Facultad de Odontología · Universidad de Carabobo
          </p>
          <p style="margin: 0; font-size: 12px; color: #cbd5e1;">
            Desarrollado con precisión por 
            <a href="{IG_URL}" target="_blank" style="color: #0284c7; font-weight: 600; text-decoration: none;">Synco.ia</a>
          </p>
        </td>
      </tr>

    </table>
  </td>
</tr>


def send_confirmation_email(d: dict) -> None:
try:
resend.api_key = os.environ.get("RESEND_API_KEY")
first = _first(d["nombre"])

    text = (
        f"Hola {first}, tu inscripción a la {EVENT} quedó agendada para el 21 de noviembre de 2026.\n"
        "Hemos recibido tu comprobante de pago. Verificaremos los datos y te confirmaremos en breve.\n\n"
        f"Desarrollado por Synco ({IG_URL})"
    )

    params = {
        "from": f"{EVENT} <onboarding@resend.dev>",
        "to": [d["correo"]],
        "subject": f"Inscripción Agendada · {EVENT}",
        "text": text,
        "html": _html(d),
    }

    resend.Emails.send(params)
    log.info("Correo enviado exitosamente vía Resend API a %s", d.get("correo"))

except Exception:
    log.exception("No se pudo enviar el correo a %s", d.get("correo"))
