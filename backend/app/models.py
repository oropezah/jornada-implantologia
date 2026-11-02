from datetime import date, datetime, timezone

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Cita(Base):
    __tablename__ = "citas"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    fecha_nacimiento: Mapped[str] = mapped_column(String(10), default="")
    telefono: Mapped[str] = mapped_column(String(32))
    email: Mapped[str | None] = mapped_column(String(160), nullable=True)
    servicios: Mapped[list] = mapped_column(JSON)
    is_express: Mapped[bool] = mapped_column(Boolean, default=False)
    manicurista_pedida: Mapped[str] = mapped_column(String(40), default="Sin preferencia")
    fecha: Mapped[date] = mapped_column(Date, index=True)
    horario: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(16), default="confirmada")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    staff: Mapped[list["CitaStaff"]] = relationship(back_populates="cita", cascade="all, delete-orphan", order_by="CitaStaff.id")


class CitaStaff(Base):
    """Un bloque de tiempo ocupado de una manicurista. Express = 2 filas (Edu manos + Anabel pies).
    starts_at/ends_at se guardan como hora local de Caracas (sin zona; Venezuela no tiene horario de verano)."""

    __tablename__ = "cita_staff"
    __table_args__ = (Index("ix_cita_staff_staff_start", "staff", "starts_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    cita_id: Mapped[int] = mapped_column(ForeignKey("citas.id", ondelete="CASCADE"))
    staff: Mapped[str] = mapped_column(String(40))
    servicio: Mapped[str] = mapped_column(Text)
    minutos: Mapped[int] = mapped_column()
    auto_asignada: Mapped[bool] = mapped_column(Boolean, default=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime)
    ends_at: Mapped[datetime] = mapped_column(DateTime)
    google_event_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    cita: Mapped[Cita] = relationship(back_populates="staff")
