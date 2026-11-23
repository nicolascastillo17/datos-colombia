"""Configuración por variables de entorno (con lectura opcional de .env)."""

from __future__ import annotations

import os
from pathlib import Path


def _cargar_env(ruta: Path = Path(".env")) -> None:
    """Carga .env sin dependencias externas. No sobrescribe variables ya definidas."""
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip())


_cargar_env()

DATOS_DIR = Path(os.environ.get("DATOS_DIR", "./data"))
DATOS_GOV_APP_TOKEN = os.environ.get("DATOS_GOV_APP_TOKEN") or None
