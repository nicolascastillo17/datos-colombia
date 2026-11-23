"""GDELT DOC 2.0 — tono promedio diario de noticias de medios colombianos.

Verificado 2026-11-23: mode=timelinetone&format=json devuelve
{"query_details": {"date_resolution": "day", ...},
 "timeline": [{"series": "Average Tone", "data": [{"date": "20261025T000000Z", "value": -0.34}]}]}.

- Con timespan corto GDELT puede devolver resolución menor a un día: el parser
  promedia por día calendario (UTC).
- El día en curso está incompleto (primera prueba: tono 0.0 hoy): se excluye.
- Responde lento (20-50 s) aun estando sana: usa TIMEOUT_LENTO.
- Devuelve 429 tras varias consultas seguidas desde la misma IP (observado
  2026-11-23 tras 3 corridas en 10 min): no reintentar en caliente.
- La API cubre una ventana reciente: la historia se construye acumulando
  ejecuciones diarias. GDELT pide espaciar las peticiones (~1 cada 5 s).
"""

from __future__ import annotations

import time
from collections import defaultdict
from datetime import date, datetime, timezone

from datos_colombia.comun.almacen import Observacion, a_float, guardar_observaciones
from datos_colombia.comun.errores import Aviso
from datos_colombia.comun.http import TIMEOUT_LENTO, sesion

FUENTE = "gdelt"
BASE = "https://api.gdeltproject.org/api/v2/doc/doc"
CONJUNTO = "tono_noticias"
PAUSA_S = 10  # GDELT pide ≥5 s entre peticiones; margen por 429 observados

# tema → consulta (por validar en BACKLOG)
CONSULTAS = {
    "general": "colombia sourcecountry:CO",
    "economia": "(economia OR inflacion OR desempleo) sourcecountry:CO",
}


def _hoy_utc() -> date:
    return datetime.now(timezone.utc).date()


def parsear(respuesta: dict, tema: str, modo: str = "timelinetone", excluir_desde: date | None = None) -> list[Observacion]:
    """Promedia por día y descarta fechas >= excluir_desde (día en curso por defecto)."""
    corte = excluir_desde or _hoy_utc()
    por_dia: dict[date, list[float]] = defaultdict(list)
    for linea in respuesta.get("timeline", []) or []:
        for punto in linea.get("data", []) or []:
            fecha = datetime.strptime(punto["date"][:8], "%Y%m%d").date()
            valor = a_float(punto.get("value"))
            if fecha < corte and valor is not None:
                por_dia[fecha].append(valor)
    unidad = "tono promedio" if modo == "timelinetone" else "% cobertura"
    return [
        Observacion(FUENTE, CONJUNTO, f"{modo}:{tema}", f, sum(v) / len(v), unidad, "diaria")
        for f, v in sorted(por_dia.items())
    ]


def descargar(consulta: str, timespan: str = "3m", modo: str = "timelinetone", rapido: bool = False) -> dict:
    # GDELT tarda 20-50 s en responder aun sano (medido 2026-11-23): sin timeout corto.
    # Un 429 significa límite de tasa por IP: no se reintenta en caliente, se avisa.
    s = sesion(reintentos=0 if rapido else 2, reintentar_429=False)
    r = s.get(BASE, params={"query": consulta, "mode": modo, "format": "json", "timespan": timespan}, timeout=TIMEOUT_LENTO)
    if r.status_code == 429:
        raise Aviso("GDELT 429: límite de tasa por IP. Esperar ~15 min antes de volver a consultar")
    r.raise_for_status()
    if not r.text.strip().startswith("{"):
        # GDELT responde texto plano ante consultas inválidas o exceso de peticiones
        raise RuntimeError(f"GDELT respondió texto: {r.text[:200]!r}")
    return r.json()


def extraer(timespan: str = "3m") -> dict[str, int]:
    obs: list[Observacion] = []
    primera = True
    for tema, consulta in CONSULTAS.items():
        for modo in ("timelinetone", "timelinevol"):
            if not primera:
                time.sleep(PAUSA_S)
            primera = False
            obs.extend(parsear(descargar(consulta, timespan, modo), tema, modo))
    guardar_observaciones(obs, FUENTE, CONJUNTO)
    return {CONJUNTO: len(obs)}


def probar() -> str:
    resp = descargar(CONSULTAS["general"], "1m", rapido=True)
    resolucion = (resp.get("query_details") or {}).get("date_resolution", "?")
    obs = parsear(resp, "general")
    o = obs[-1]
    return f"{len(obs)} días (resolución {resolucion}); tono {o.fecha} = {o.valor:.3f}"
