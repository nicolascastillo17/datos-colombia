"""Banco de la República — servicios web SDMX (NSI).

Endpoint verificado 2026-11-23:
  {BASE}/dataflow/all/all/latest          → catálogo de dataflows (agencia ESTAT)
  {BASE}/data/ESTAT,<DF>,1.0/all/ALL      → datos (estructura OECD/STES)

El parser acepta SDMX-ML 2.1 genérico y structure-specific.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import date

from datos_colombia.comun.almacen import Observacion, a_float, guardar_observaciones
from datos_colombia.comun.http import TIMEOUT, TIMEOUT_PROBAR, sesion

FUENTE = "banrep"
BASE = "https://totoro.banrep.gov.co/nsi-jax-ws/rest"

# nombre corto → dataflow (ver docs/FUENTES.md)
DATAFLOWS = {
    "tpm": "DF_CBR_DAILY_HIST",
    "trm": "DF_TRM_DAILY_HIST",
    "ibr": "DF_IBR_DAILY_HIST",
    "dtf": "DF_DTF_DAILY_HIST",
    "uvr": "DF_UVR_DAILY_HIST",
    "colcap": "DF_COLCAP_MONTHLY_HIST",
    "agregados_monetarios": "DF_MONAGG_MONTHLY_HIST",
    "tes": "DF_TES_MONTHLY_HIST",
}

FRECUENCIAS = {"D": "diaria", "M": "mensual", "Q": "trimestral", "A": "anual"}

# Dimensiones que distinguen series dentro de un dataflow (estructura OECD/STES).
# Observado 2026-11-23: IBR publica SUBJECT=IRIBRM00 dos veces, con
# UNIT_MEASURE=ER (efectiva) y NR (nominal). "_Z" = no aplica → se omite.
DIMENSIONES_SERIE = ("SUBJECT", "EXPENDITURE", "ACTIVITY", "ADJUSTMENT", "UNIT_MEASURE")


def serie_id(conjunto: str, dims: dict) -> str:
    """'ibr' + {SUBJECT: IRIBRM00, UNIT_MEASURE: ER, ...} → 'ibr:IRIBRM00.ER'."""
    partes = [dims[d] for d in DIMENSIONES_SERIE if dims.get(d) and dims[d] != "_Z"]
    return f"{conjunto}:{'.'.join(partes) or 'serie'}"


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _hijos(elem: ET.Element, nombre: str):
    return [h for h in elem.iter() if _local(h.tag) == nombre]


def _fecha(periodo: str) -> date:
    """Periodo SDMX → date (inicio del periodo).

    Formatos aceptados: '2026-11-21', '2026-11-21T00:00:00', '20260101' (BanRep,
    observado 2026-11-23), '202601', '2026-11', '2026-M11', '2026-Q3', '2026'.
    """
    p = periodo.strip()
    if "-Q" in p:
        anio, q = p.split("-Q")
        return date(int(anio), (int(q) - 1) * 3 + 1, 1)
    if "-M" in p:
        anio, mes = p.split("-M")
        return date(int(anio), int(mes), 1)
    if len(p) >= 10 and p[4] == "-" and p[7] == "-":
        return date.fromisoformat(p[:10])
    if len(p) == 7 and p[4] == "-":
        return date(int(p[:4]), int(p[5:7]), 1)
    if p.isdigit() and len(p) == 8:
        return date(int(p[:4]), int(p[4:6]), int(p[6:8]))
    if p.isdigit() and len(p) == 6:
        return date(int(p[:4]), int(p[4:6]), 1)
    if p.isdigit() and len(p) == 4:
        return date(int(p), 1, 1)
    raise ValueError(f"Periodo SDMX no reconocido: {periodo!r}")


def parsear(xml: bytes | str, conjunto: str) -> list[Observacion]:
    raiz = ET.fromstring(xml)
    obs: list[Observacion] = []
    for serie in [e for e in raiz.iter() if _local(e.tag) == "Series"]:
        # dimensiones: atributos (structure-specific) o SeriesKey/Value (genérico)
        dims = {k: v for k, v in serie.attrib.items()}
        for clave in _hijos(serie, "SeriesKey"):
            for v in clave:
                dims[v.get("id")] = v.get("value")
        sid = serie_id(conjunto, dims)
        unidad = dims.get("UNIT_MEASURE")
        frecuencia = FRECUENCIAS.get(dims.get("FREQ", ""), dims.get("FREQ"))
        for o in _hijos(serie, "Obs"):
            periodo = o.get("TIME_PERIOD")
            valor = o.get("OBS_VALUE")
            if periodo is None:  # genérico
                for h in o:
                    nombre = _local(h.tag)
                    if nombre == "ObsDimension":
                        periodo = h.get("value")
                    elif nombre == "ObsValue":
                        valor = h.get("value")
            if periodo is None:
                continue
            obs.append(
                Observacion(FUENTE, conjunto, sid, _fecha(periodo), a_float(valor), unidad, frecuencia)
            )
    return obs


def descargar(conjunto: str, desde: str | None = None, rapido: bool = False) -> bytes:
    df = DATAFLOWS[conjunto]
    params = {"dimensionAtObservation": "TIME_PERIOD", "detail": "full"}
    # startPeriod se respeta solo por año (observado 2026-11-23: desde 2026-11-01 → datos desde 2026-01-02)
    if desde:
        params["startPeriod"] = desde
    s, t = (sesion(reintentos=1), TIMEOUT_PROBAR) if rapido else (sesion(), TIMEOUT)
    r = s.get(f"{BASE}/data/ESTAT,{df},1.0/all/ALL", params=params, timeout=t)
    r.raise_for_status()
    return r.content


def extraer(conjuntos: list[str] | None = None, desde: str | None = None) -> dict[str, int]:
    resultado = {}
    for c in conjuntos or list(DATAFLOWS):
        obs = parsear(descargar(c, desde), c)
        guardar_observaciones(obs, FUENTE, c)
        resultado[c] = len(obs)
    return resultado


def probar() -> str:
    obs = parsear(descargar("tpm", desde=_hace_dias(15), rapido=True), "tpm")
    ultima = max(obs, key=lambda o: o.fecha) if obs else None
    return f"{len(obs)} obs; última TPM {ultima.fecha} = {ultima.valor}" if ultima else "0 obs"


def _hace_dias(n: int) -> str:
    from datetime import timedelta

    return (date.today() - timedelta(days=n)).isoformat()
