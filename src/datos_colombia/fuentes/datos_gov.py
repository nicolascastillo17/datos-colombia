"""datos.gov.co (Socrata SODA). Cliente genérico + TRM (32sa-8pi3).

Verificado 2026-11-23: /resource/32sa-8pi3.json devuelve
[{"valor": "3461.92", "unidad": "COP", "vigenciadesde": "...", "vigenciahasta": "..."}].
"""

from __future__ import annotations

from datetime import date

from datos_colombia.comun.almacen import Observacion, a_float, guardar_observaciones
from datos_colombia.comun.config import DATOS_GOV_APP_TOKEN
from datos_colombia.comun.http import TIMEOUT, TIMEOUT_PROBAR, sesion

FUENTE = "datos_gov"
BASE = "https://www.datos.gov.co/resource"
PAGINA = 50_000

CONJUNTOS = {
    # nombre → (dataset_id, campo_fecha, campo_valor, unidad, frecuencia)
    "trm": ("32sa-8pi3", "vigenciadesde", "valor", "COP por USD", "diaria"),
}


def consultar(dataset_id: str, params: dict | None = None) -> list[dict]:
    """Pagina con $limit/$offset hasta agotar resultados."""
    s = sesion()
    if DATOS_GOV_APP_TOKEN:
        s.headers["X-App-Token"] = DATOS_GOV_APP_TOKEN
    filas: list[dict] = []
    offset = 0
    while True:
        p = {"$limit": PAGINA, "$offset": offset, "$order": ":id", **(params or {})}
        r = s.get(f"{BASE}/{dataset_id}.json", params=p, timeout=TIMEOUT)
        r.raise_for_status()
        lote = r.json()
        filas.extend(lote)
        if len(lote) < PAGINA:
            return filas
        offset += PAGINA


def parsear(filas: list[dict], conjunto: str) -> list[Observacion]:
    _, campo_fecha, campo_valor, unidad, frecuencia = CONJUNTOS[conjunto]
    return [
        Observacion(
            FUENTE,
            conjunto,
            f"{conjunto}",
            date.fromisoformat(f[campo_fecha][:10]),
            a_float(f.get(campo_valor)),
            f.get("unidad") or unidad,
            frecuencia,
        )
        for f in filas
        if f.get(campo_fecha)
    ]


def extraer(conjuntos: list[str] | None = None) -> dict[str, int]:
    resultado = {}
    for c in conjuntos or list(CONJUNTOS):
        obs = parsear(consultar(CONJUNTOS[c][0]), c)
        guardar_observaciones(obs, FUENTE, c)
        resultado[c] = len(obs)
    return resultado


def probar() -> str:
    s = sesion(reintentos=1)
    if DATOS_GOV_APP_TOKEN:
        s.headers["X-App-Token"] = DATOS_GOV_APP_TOKEN
    r = s.get(f"{BASE}/32sa-8pi3.json", params={"$limit": 1, "$order": "vigenciadesde DESC"}, timeout=TIMEOUT_PROBAR)
    r.raise_for_status()
    filas = r.json()
    o = parsear(filas, "trm")[0]
    token = "con token" if DATOS_GOV_APP_TOKEN else "sin token"
    return f"TRM {o.fecha} = {o.valor} ({token})"
