"""CLI: python -m datos_colombia {probar|extraer|cargar|aplicar-sql} ..."""

from __future__ import annotations

import argparse
import sys
import time
import traceback

from datos_colombia.comun.errores import Aviso
from datos_colombia.fuentes import banco_mundial, banrep_sdmx, dane, datos_gov, fedesarrollo, gdelt

FUENTES = {
    "banrep": (banrep_sdmx.probar, banrep_sdmx.extraer),
    "datos_gov": (datos_gov.probar, datos_gov.extraer),
    "banco_mundial": (banco_mundial.probar, banco_mundial.extraer),
    "gdelt": (gdelt.probar, gdelt.extraer),
    "dane_ipc": (dane.probar, dane.extraer_ipc),
    "fedesarrollo": (fedesarrollo.probar, fedesarrollo.extraer),
}

# nombre en el CLI → directorio en data/raw (cuando difieren)
DIR_RAW = {"dane_ipc": "dane"}


def _correr(nombre: str, funcion, verbose: bool) -> bool:
    t0 = time.monotonic()
    try:
        resultado = funcion()
        print(f"✅ {nombre:<14} {time.monotonic() - t0:5.1f}s  {resultado}")
        return True
    except Aviso as e:
        print(f"⚠️  {nombre:<14} {time.monotonic() - t0:5.1f}s  {e}")
        return True
    except Exception as e:  # noqa: BLE001 — se reporta y se sigue con la siguiente fuente
        print(f"❌ {nombre:<14} {time.monotonic() - t0:5.1f}s  {type(e).__name__}: {e}")
        if verbose:
            traceback.print_exc()
        return False


def _cargar(fuente: str, todo: bool):
    from datos_colombia.comun import cargador, db

    def ejecutar():
        with db.conectar("DATABASE_URL") as conexion:
            return cargador.cargar(conexion, None if fuente == "todas" else DIR_RAW.get(fuente, fuente), todo)

    return ejecutar


def _aplicar_sql():
    from datos_colombia.comun import db

    with db.conectar("DATABASE_URL_OWNER") as conexion:
        return "aplicados: " + ", ".join(db.aplicar_sql(conexion))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="datos_colombia")
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)
    for cmd in ("probar", "extraer"):
        s = sub.add_parser(cmd)
        s.add_argument("fuente", nargs="?", default="todas", choices=[*FUENTES, "todas"])
    s = sub.add_parser("cargar", help="data/raw → raw_series.observaciones (DATABASE_URL)")
    s.add_argument("fuente", nargs="?", default="todas", choices=[*FUENTES, "todas"])
    s.add_argument("--todo", action="store_true", help="todas las particiones, no solo la última")
    sub.add_parser("aplicar-sql", help="aplica sql/NN_*.sql en orden (DATABASE_URL_OWNER, solo local)")
    args = p.parse_args(argv)

    if args.cmd == "aplicar-sql":
        return 0 if _correr("aplicar-sql", _aplicar_sql, args.verbose) else 1
    if args.cmd == "cargar":
        return 0 if _correr(f"cargar {args.fuente}", _cargar(args.fuente, args.todo), args.verbose) else 1

    nombres = list(FUENTES) if args.fuente == "todas" else [args.fuente]
    indice = 0 if args.cmd == "probar" else 1
    oks = [_correr(n, FUENTES[n][indice], args.verbose) for n in nombres]
    return 0 if all(oks) else 1


if __name__ == "__main__":
    sys.exit(main())
