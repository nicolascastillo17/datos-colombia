"""CLI: python -m datos_colombia {probar|extraer} ..."""

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


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="datos_colombia")
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)
    for cmd in ("probar", "extraer"):
        s = sub.add_parser(cmd)
        s.add_argument("fuente", nargs="?", default="todas", choices=[*FUENTES, "todas"])
    args = p.parse_args(argv)

    nombres = list(FUENTES) if args.fuente == "todas" else [args.fuente]
    indice = 0 if args.cmd == "probar" else 1
    oks = [_correr(n, FUENTES[n][indice], args.verbose) for n in nombres]
    return 0 if all(oks) else 1


if __name__ == "__main__":
    sys.exit(main())
