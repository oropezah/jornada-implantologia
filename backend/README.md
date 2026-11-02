# Mocca Beauty Studio · API

FastAPI + Neon (Postgres) + Render. Reemplaza el workflow de n8n completo.

| Antes (n8n) | Ahora |
|---|---|
| Webhook horarios + Google Calendar getAll | `POST /webhook/mocca_beauty` (BD + Calendar freebusy) |
| Webhook cita + Preparar Personas + Sheets + Calendar + Gmail + YCloud | `POST /webhook/citamocca` → responde rápido y manda todo en segundo plano |

## Reglas (igual que n8n, con correcciones)
- Slots: 9:00, 10:30, 12:30, 2:00, 3:30 · cerrado domingo y lunes · no se ofrecen horas pasadas de hoy.
- Duración: 90 min por servicio, Jelly 120, varios servicios suman. **Corregido:** n8n siempre bloqueaba 90 min al calcular horarios.
- Sin preferencia: Edu primero; si está ocupada, Anabel.
- Express: Edu = manos, Anabel = pies, en paralelo (ambas libres).
- Anabel = el calendario que en n8n se llamaba "Ninia".
- Anti doble reserva: chequeo en app + restricción `EXCLUDE` en Postgres (dos clientes a la vez → uno recibe 409).
- Bloqueos manuales en Google Calendar (vacaciones, citas por fuera) siguen ocultando horarios.

## Después de confirmar (en segundo plano, cada paso independiente)
1. Evento en el Google Calendar de cada manicurista
2. Fila(s) en Google Sheets (mismas columnas + `Email` al final)
3. Email al estudio (Resend)
4. Email al cliente con botón Google Calendar + `.ics` (si dejó correo)
5. WhatsApp al estudio vía YCloud (opcional)

## Local
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
pytest                              # 15 tests
python scripts/preview_emails.py    # abre previews/*.html
uvicorn app.main:app --reload
```
