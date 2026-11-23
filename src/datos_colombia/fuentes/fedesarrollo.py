"""Fedesarrollo — Encuesta de Opinión del Consumidor (carga manual).

Sin API. Cada mes se actualiza a mano data/manual/fedesarrollo/eoc.csv con
columnas: fecha (AAAA-MM), icc, iec, ice  (balances en %).
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from datos_colombia.comun.almacen import Observacion, a_float, guardar_observaciones
from datos_colombia.comun.config import DATOS_DIR
from datos_colombia.comun.errores import Aviso

FUENTE = "fedesarrollo"
CONJUNTO = "eoc"
COLUMNAS = {"icc": "Índice de Confianza del Consumidor", "iec": "Índice de Expectativas", "ice": "Índice de Condiciones Económicas"}


def ruta_manual() -> Path:
    return DATOS_DIR / "manual" / FUENTE / "eoc.csv"


def parsear(lineas) -> list[Observacion]:
    obs = []
    for fila in csv.DictReader(lineas):
        anio, mes = fila["fecha"].strip()[:7].split("-")
        f = date(int(anio), int(mes), 1)
        for col in COLUMNAS:
            if col in fila:
                obs.append(Observacion(FUENTE, CONJUNTO, col, f, a_float(fila[col]), "balance %", "mensual"))
    return obs


def extraer() -> dict[str, int]:
    ruta = ruta_manual()
    if not ruta.exists():
        raise FileNotFoundError(f"Falta {ruta} (columnas: fecha,icc,iec,ice)")
    with ruta.open(encoding="utf-8") as fh:
        obs = parsear(fh)
    guardar_observaciones(obs, FUENTE, CONJUNTO)
    return {CONJUNTO: len(obs)}


def probar() -> str:
    ruta = ruta_manual()
    if not ruta.exists():
        raise Aviso(f"carga manual pendiente: falta {ruta} (columnas fecha,icc,iec,ice)")
    with ruta.open(encoding="utf-8") as fh:
        obs = parsear(fh)
    ultima = max(o.fecha for o in obs) if obs else None
    return f"{len(obs)} obs; último mes {ultima}"
