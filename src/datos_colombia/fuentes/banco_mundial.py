"""Banco Mundial — API v2 (WDI) para Colombia.

Verificado 2026-11-23: /v2/country/COL/indicator/NY.GDP.MKTP.KD.ZG?format=json
devuelve [metadatos, [ {indicator:{id,value}, date:"2025", value:2.6, ...}, ... ]].
"""

from __future__ import annotations

from datetime import date

from datos_colombia.comun.almacen import Observacion, a_float, guardar_observaciones
from datos_colombia.comun.http import TIMEOUT, TIMEOUT_PROBAR, sesion

FUENTE = "banco_mundial"
BASE = "https://api.worldbank.org/v2/country/COL/indicator"

INDICADORES = {
    "NY.GDP.MKTP.KD.ZG": "% anual",  # crecimiento del PIB
    "NY.GDP.PCAP.KD": "USD constantes",  # PIB per cápita
    "FP.CPI.TOTL.ZG": "% anual",  # inflación IPC
    "SL.UEM.TOTL.ZS": "% fuerza laboral",  # desempleo (OIT modelado)
    "SI.POV.GINI": "índice 0-100",  # Gini
    "SI.POV.NAHC": "% población",  # pobreza línea nacional
}

CONJUNTO = "wdi"


def parsear(respuesta: list) -> list[Observacion]:
    if not isinstance(respuesta, list) or len(respuesta) < 2 or respuesta[1] is None:
        return []
    obs = []
    for fila in respuesta[1]:
        ind = fila["indicator"]["id"]
        if not str(fila.get("date", "")).isdigit():
            continue
        obs.append(
            Observacion(
                FUENTE,
                CONJUNTO,
                ind,
                date(int(fila["date"]), 1, 1),
                a_float(fila.get("value")),
                INDICADORES.get(ind),
                "anual",
            )
        )
    return obs


def descargar(indicador: str, mrv: int | None = None, rapido: bool = False) -> list:
    """mrv = most recent values (consulta liviana para `probar`)."""
    params = {"format": "json", "per_page": 20_000}
    if mrv:
        params["mrv"] = mrv
    s, t = (sesion(reintentos=1), TIMEOUT_PROBAR) if rapido else (sesion(), TIMEOUT)
    r = s.get(f"{BASE}/{indicador}", params=params, timeout=t)
    r.raise_for_status()
    return r.json()


def extraer() -> dict[str, int]:
    obs: list[Observacion] = []
    for ind in INDICADORES:
        obs.extend(parsear(descargar(ind)))
    guardar_observaciones(obs, FUENTE, CONJUNTO)
    return {CONJUNTO: len(obs)}


def probar() -> str:
    obs = [o for o in parsear(descargar("NY.GDP.MKTP.KD.ZG", mrv=5, rapido=True)) if o.valor is not None]
    o = max(obs, key=lambda x: x.fecha)
    return f"crecimiento PIB {o.fecha.year} = {o.valor}"
