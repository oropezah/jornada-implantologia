import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_URL

log = logging.getLogger("mocca.db")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=5, pool_recycle=300)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_session():
    with SessionLocal() as session:
        yield session


def init_db() -> None:
    from . import models  # noqa: F401

    Base.metadata.create_all(engine)
    if engine.dialect.name != "postgresql":
        return
    # Red de seguridad contra carreras: Postgres rechaza dos citas solapadas de la misma manicurista.
    try:
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gist"))
            conn.execute(
                text(
                    """
                    DO $$ BEGIN
                      IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'cita_staff_no_overlap') THEN
                        ALTER TABLE cita_staff ADD CONSTRAINT cita_staff_no_overlap
                          EXCLUDE USING gist (staff WITH =, tsrange(starts_at, ends_at) WITH &&);
                      END IF;
                    END $$;
                    """
                )
            )
    except Exception:  # noqa: BLE001
        log.exception("No se pudo crear la restriccion anti-solapamiento (la logica de app sigue activa)")
