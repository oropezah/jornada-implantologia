import os
import tempfile

os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tempfile.mkdtemp(), "test.db")

from datetime import datetime  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import google_client, logic  # noqa: E402
from app.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

FAKE_NOW = datetime(2026, 11, 2, 6, 0)  # lunes 6:00 am
TUESDAY = "2026-11-03"


@pytest.fixture(autouse=True)
def fresh(monkeypatch):
    monkeypatch.setattr(logic, "now_local", lambda: FAKE_NOW)
    monkeypatch.setattr(google_client, "busy_by_staff", lambda a, b: {})
    from app import models  # noqa: F401

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def payload(**kw):
    base = dict(nombre="Ana Pérez", telefono="04121234567", servicios=["Manicure Tradicional"], manicurista="Sin preferencia", fecha=TUESDAY)
    base.update(kw)
    return base
