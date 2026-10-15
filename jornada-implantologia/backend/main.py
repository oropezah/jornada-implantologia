import logging
import os
import re
import time

from dotenv import load_dotenv

load_dotenv()

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402
from pydantic import BaseModel, EmailStr, ValidationError, field_validator  # noqa: E402

from drive import upload_receipt  # noqa: E402
from mailer import send_confirmation_email  # noqa: E402
from sheets import DuplicateAttendee, append_attendee, cedula_exists  # noqa: E402
from whatsapp import notify_whatsapp  # noqa: E402

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("jornada")

MAX_FILE_BYTES = 8 * 1024 * 1024

app = FastAPI(title="Jornada Implantología API")

allowed_origins_env = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:3000,https://jornada-implantologia.vercel.app,https://plantologia.vercel.app"
)

origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configuración permisiva para evitar bloqueos por CORS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def normalize_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("00"):
        digits = digits[2:]
    if digits.startswith("0"):
        return "58" + digits[1:]
    if len(digits) == 10 and digits.startswith("4"):
        return "58" + digits
    return digits


class Attendee(BaseModel):
    nombre: str
    cedula: str
    correo: EmailStr
    telefono: str
    institucion: str

    @field_validator("nombre", "institucion")
    @classmethod
    def _text(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 120:
            raise ValueError("Texto inválido")
        return v

    @field_validator("cedula")
    @classmethod
    def _cedula(cls, v: str) -> str:
        v = re.sub(r"\D", "", v)
        if not 6 <= len(v) <= 9:
            raise ValueError("Cédula inválida")
        return v

    @field_validator("telefono")
    @classmethod
    def _tel(cls, v: str) -> str:
        if not 10 <= len(re.sub(r"\D", "", v)) <= 13:
            raise ValueError("Teléfono inválido")
        return v.strip()


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/api/v1/register")
def register(
    bg: BackgroundTasks,
    nombre: str = Form(...),
    cedula: str = Form(...),
    correo: str = Form(...),
    telefono: str = Form(...),
    institucion: str = Form(...),
    comprobante: UploadFile = File(...),
):
    t0 = time.perf_counter()

    try:
        a = Attendee(
            nombre=nombre,
            cedula=cedula,
            correo=correo,
            telefono=telefono,
            institucion=institucion,
        )
    except ValidationError as e:
        log.warning(f"Validation error: {e}")
        return JSONResponse(status_code=422, content={"detail": "Revisa los datos del formulario."})

    mime = comprobante.content_type or ""
    content = comprobante.file.read(MAX_FILE_BYTES + 1)
    if not content:
        return JSONResponse(status_code=422, content={"detail": "El comprobante está vacío."})
    if len(content) > MAX_FILE_BYTES:
        return JSONResponse(status_code=413, content={"detail": "La imagen es muy pesada (máx. 8 MB)."})

    data = a.model_dump()
    data["correo"] = str(a.correo)
    data["telefono_wa"] = normalize_phone(a.telefono)
    cedula_clean = str(data["cedula"]).strip()

    # 1. Verificación de duplicado (Sheets)
    try:
        if cedula_exists(cedula_clean):
            return JSONResponse(status_code=409, content={"detail": "Esta cédula ya está inscrita."})
    except Exception as e:
        log.exception(f"Error verificando cédula en Sheets: {e}")
    t1 = time.perf_counter()

    # 2. Guardar comprobante en Google Drive
    try:
        data["comprobante_url"] = upload_receipt(content, mime, cedula_clean, data["nombre"])
    except Exception as e:
        log.exception(f"Error subiendo comprobante a Google Drive: {e}")
        return JSONResponse(status_code=500, content={"detail": "Error al guardar el comprobante en Google Drive."})
    t2 = time.perf_counter()

    # 3. Registrar fila en Google Sheets
    try:
        append_attendee(data, check_duplicate=False)
    except DuplicateAttendee:
        return JSONResponse(status_code=409, content={"detail": "Esta cédula ya está inscrita."})
    except Exception as e:
        log.exception(f"Error guardando en Google Sheets: {e}")
        return JSONResponse(status_code=500, content={"detail": "No pudimos registrar los datos en Google Sheets."})
    t3 = time.perf_counter()

    log.info(
        "register OK · duplicado %.1fs · drive %.1fs · sheets %.1fs · total %.1fs",
        t1 - t0, t2 - t1, t3 - t2, t3 - t0,
    )

    # 4. Programar tareas de segundo plano (Correo y WhatsApp)
    try:
        bg.add_task(send_confirmation_email, data)
        bg.add_task(notify_whatsapp, data)
    except Exception as e:
        log.error(f"Error programando tareas secundarias: {e}")

    return JSONResponse(status_code=200, content={"ok": True})