import logging
import os
import re

from dotenv import load_dotenv

load_dotenv()

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from pydantic import BaseModel, EmailStr, ValidationError, field_validator  # noqa: E402

from drive import upload_receipt  # noqa: E402
from mailer import send_confirmation_email  # noqa: E402
from sheets import DuplicateAttendee, append_attendee, cedula_exists  # noqa: E402
from whatsapp import notify_whatsapp  # noqa: E402

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("jornada")

MAX_FILE_BYTES = 8 * 1024 * 1024

app = FastAPI(title="Jornada Implantología API")

# Reemplaza la configuración de CORS existente por esta:
allowed_origins_env = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:3000,https://jornada-implantologia.vercel.app/"
)

origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Permite cualquier preview o despliegue en Vercel
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


@app.post("/register")
def register(
    bg: BackgroundTasks,
    nombre: str = Form(...),
    cedula: str = Form(...),
    correo: str = Form(...),
    telefono: str = Form(...),
    institucion: str = Form(...),
    comprobante: UploadFile = File(...),
):
    try:
        a = Attendee(
            nombre=nombre,
            cedula=cedula,
            correo=correo,
            telefono=telefono,
            institucion=institucion,
        )
    except ValidationError:
        raise HTTPException(status_code=422, detail="Revisa los datos del formulario.")

    mime = comprobante.content_type or ""
    if not mime.startswith("image/"):
        raise HTTPException(status_code=422, detail="El comprobante debe ser una imagen.")

    content = comprobante.file.read(MAX_FILE_BYTES + 1)
    if not content:
        raise HTTPException(status_code=422, detail="El comprobante está vacío.")
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="La imagen es muy pesada (máx. 8 MB).")

    data = a.model_dump()
    data["correo"] = str(a.correo)
    data["telefono_wa"] = normalize_phone(a.telefono)

    try:
        if cedula_exists(data["cedula"]):
            raise DuplicateAttendee()
        data["comprobante_url"] = upload_receipt(content, mime, data["cedula"], data["nombre"])
        append_attendee(data)
    except DuplicateAttendee:
        raise HTTPException(status_code=409, detail="Esta cédula ya está inscrita.")
    except Exception:
        log.exception("Error guardando la inscripción")
        raise HTTPException(
            status_code=500,
            detail="No pudimos guardar tu inscripción. Intenta de nuevo.",
        )

    bg.add_task(send_confirmation_email, data)
    bg.add_task(notify_whatsapp, data)
    return {"ok": True}