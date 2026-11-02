import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class BookingRequest(BaseModel):
    """Mismo JSON que ya manda el frontend (camelCase). `email` es opcional."""

    model_config = ConfigDict(extra="ignore")

    encabezado: str | None = None
    isExpress: bool = False
    nombre: str = Field(min_length=2, max_length=120)
    fechaNacimiento: str | None = None
    telefono: str = Field(min_length=7, max_length=32)
    email: str | None = None
    servicios: list[str] = []
    manicurista: str | None = None
    fecha: str  # YYYY-MM-DD
    horario: str | None = None  # solo al confirmar

    @field_validator("email")
    @classmethod
    def _clean_email(cls, v: str | None) -> str | None:
        v = (v or "").strip()
        return v if v and _EMAIL_RE.match(v) else None
