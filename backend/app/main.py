import logging
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from .config import ALLOWED_ORIGINS
from .db import get_session, init_db
from .logic import BookingError, available_slots, create_cita
from .notifications import run_post_booking
from .schemas import BookingRequest

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Mocca Beauty Studio API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["*"])


@app.exception_handler(BookingError)
async def booking_error_handler(_, exc: BookingError):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.get("/")
def root():
    return {"ok": True, "service": "mocca-api"}


@app.get("/health")
def health():
    return {"ok": True}


# Mismas rutas que los webhooks de n8n: el frontend solo cambia el dominio.
@app.post("/webhook/mocca_beauty")
def horarios(req: BookingRequest, session: Session = Depends(get_session)):
    return {"disponibles": available_slots(session, req)}


@app.post("/webhook/citamocca")
def confirmar(req: BookingRequest, background: BackgroundTasks, session: Session = Depends(get_session)):
    cita = create_cita(session, req)
    background.add_task(run_post_booking, cita.id)  # Calendar, Sheets, emails, WhatsApp
    return {
        "ok": True,
        "id": cita.id,
        "fecha": cita.fecha.isoformat(),
        "horario": cita.horario,
        "manicuristas": [r.staff for r in cita.staff],
    }
