from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from watchdog.core.config import Settings
from watchdog.core.paths import resolve_database_url


def build_engine(settings: Settings) -> Engine:
    connect_args: dict[str, object] = {}
    database_url = resolve_database_url(settings.database_url)
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(database_url, future=True, connect_args=connect_args)


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
