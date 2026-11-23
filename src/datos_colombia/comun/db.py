"""Conexión a Postgres (Neon) y aplicación de sql/NN_*.sql.

Variables de entorno:
  DATABASE_URL        rol escritor_cron (carga raw; la usa el cron de GitHub Actions)
  DATABASE_URL_OWNER  rol dueño (solo local, para aplicar sql/; nunca en GitHub)
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import psycopg

RAIZ = Path(__file__).resolve().parents[3]
DIR_SQL = RAIZ / "sql"
PATRON_SQL = re.compile(r"^\d{2}_.+\.sql$")


def url(variable: str = "DATABASE_URL") -> str:
    valor = os.environ.get(variable)
    if not valor:
        raise RuntimeError(f"Falta {variable} en el entorno o en .env (ver .env.example)")
    return valor


def conectar(variable: str = "DATABASE_URL") -> psycopg.Connection:
    return psycopg.connect(url(variable), connect_timeout=15, application_name="datos-colombia")


def archivos_sql(directorio: Path = DIR_SQL) -> list[Path]:
    """sql/NN_*.sql en orden numérico. Cada archivo debe ser idempotente."""
    return sorted(p for p in directorio.iterdir() if PATRON_SQL.match(p.name))


def aplicar_sql(conexion: psycopg.Connection, archivos: list[Path] | None = None) -> list[str]:
    """Aplica cada archivo en su propia transacción; se detiene en el primer error."""
    aplicados = []
    for archivo in archivos or archivos_sql():
        with conexion.transaction():
            conexion.execute(archivo.read_text(encoding="utf-8"))
        aplicados.append(archivo.name)
    return aplicados
