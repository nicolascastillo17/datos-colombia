"""Pruebas de aplicar-sql y del cargador contra un Postgres real.

Se ejecutan solo si TEST_DATABASE_URL apunta a una base desechable con un rol
dueño (se omiten en CI y en máquinas sin Postgres). Ejemplo local:
  TEST_DATABASE_URL=postgresql://neondb_owner@localhost:5433/neondb pytest -q
"""

import os
from datetime import date

import psycopg
import pytest

from datos_colombia.comun import cargador, db
from datos_colombia.comun.almacen import Observacion, guardar_observaciones

URL = os.environ.get("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not URL, reason="sin TEST_DATABASE_URL")

CLAVE_ESCRITOR = "prueba-escritor"


@pytest.fixture()
def base_limpia():
    with psycopg.connect(URL, autocommit=True) as c:
        c.execute("DROP SCHEMA IF EXISTS raw_series, macro, sentimiento, vida, kpi CASCADE")
        for rol in ("escritor_cron", "lector"):
            c.execute(f"DROP OWNED BY {rol}") if c.execute(
                "SELECT 1 FROM pg_roles WHERE rolname = %s", (rol,)
            ).fetchone() else None
            c.execute(f"DROP ROLE IF EXISTS {rol}")
        c.execute(f"CREATE ROLE escritor_cron WITH LOGIN PASSWORD '{CLAVE_ESCRITOR}'")
        c.execute("CREATE ROLE lector WITH LOGIN PASSWORD 'prueba-lector'")
        db.aplicar_sql(c)
    yield


def _url_rol(rol: str, clave: str) -> str:
    info = psycopg.conninfo.conninfo_to_dict(URL)
    info.update(user=rol, password=clave)
    return psycopg.conninfo.make_conninfo(**info)


def _obs(valor: float, dia: int = 21) -> Observacion:
    return Observacion("banrep", "tpm", "tpm:IRCBRM01", date(2026, 11, dia), valor, "PA", "diaria")


def test_aplicar_sql_es_idempotente(base_limpia):
    with psycopg.connect(URL) as c:
        assert db.aplicar_sql(c) == ["00_schemas.sql", "01_grants.sql"]


def test_aplicar_sql_rechaza_rol_no_dueno(base_limpia):
    with psycopg.connect(_url_rol("lector", "prueba-lector")) as c:
        with pytest.raises(RuntimeError, match="conecta como 'lector'"):
            db.aplicar_sql(c)


def test_carga_aborta_si_dos_series_comparten_serie_id(base_limpia, tmp_path):
    guardar_observaciones([_obs(9.45, 21), _obs(9.05, 21)], "banrep", "ibr", base=tmp_path)
    with psycopg.connect(_url_rol("escritor_cron", CLAVE_ESCRITOR)) as c:
        with pytest.raises(cargador.SerieAmbigua, match="tpm:IRCBRM01"):
            cargador.cargar(c, base=tmp_path)
        assert c.execute("SELECT count(*) FROM raw_series.observaciones").fetchone()[0] == 0


def test_carga_upsert_y_permisos(base_limpia, tmp_path):
    guardar_observaciones([_obs(12.25, 21), _obs(12.25, 22), _obs(12.25, 22)], "banrep", "tpm", base=tmp_path)

    with psycopg.connect(_url_rol("escritor_cron", CLAVE_ESCRITOR)) as c:
        r = cargador.cargar(c, base=tmp_path)
        assert (r.filas_leidas, r.duplicadas, r.insertadas, r.actualizadas) == (3, 1, 2, 0)

        r = cargador.cargar(c, base=tmp_path)  # misma partición: sin cambios
        assert (r.insertadas, r.actualizadas) == (0, 0)

        # revisión del dato en la fuente → actualización
        ruta = cargador.particiones(base=tmp_path)[0]
        ruta.unlink()
        guardar_observaciones([_obs(12.25, 21), _obs(12.0, 22)], "banrep", "tpm", base=tmp_path)
        r = cargador.cargar(c, base=tmp_path)
        assert (r.insertadas, r.actualizadas) == (0, 1)

        # escritor_cron no puede hacer DDL
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            c.execute("CREATE TABLE raw_series.otra (x int)")

    with psycopg.connect(_url_rol("lector", "prueba-lector")) as c:
        assert c.execute("SELECT valor FROM raw_series.observaciones WHERE fecha = '2026-11-22'").fetchone()[0] == 12.0
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            c.execute("DELETE FROM raw_series.observaciones")
