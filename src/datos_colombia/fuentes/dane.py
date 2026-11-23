"""DANE — anexos publicados (sin API).

Por ahora solo descarga el anexo de variaciones del IPC y lo guarda tal cual.
Patrón observado en una respuesta oficial del DANE (dic-2024):
  https://www.dane.gov.co/files/operaciones/IPC/dic2024/anex-IPC-Variacion-dic2024.xlsx
Parser del xlsx: pendiente (BACKLOG 🟡). Validar el patrón mes a mes.
"""

from __future__ import annotations

from datetime import date

from datos_colombia.comun.almacen import guardar_binario
from datos_colombia.comun.http import TIMEOUT, TIMEOUT_PROBAR, sesion

FUENTE = "dane"
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def url_anexo_ipc(anio: int, mes: int) -> str:
    m = f"{MESES[mes - 1]}{anio}"
    return f"https://www.dane.gov.co/files/operaciones/IPC/{m}/anex-IPC-Variacion-{m}.xlsx"


def _ultimo_mes_publicado(hoy: date | None = None) -> tuple[int, int]:
    """El IPC de un mes se publica en los primeros días del mes siguiente."""
    hoy = hoy or date.today()
    anio, mes = (hoy.year, hoy.month - 1) if hoy.month > 1 else (hoy.year - 1, 12)
    if hoy.day < 10:  # aún no publicado: retroceder un mes más
        anio, mes = (anio, mes - 1) if mes > 1 else (anio - 1, 12)
    return anio, mes


def extraer_ipc(anio: int | None = None, mes: int | None = None) -> dict[str, str]:
    if anio is None or mes is None:
        anio, mes = _ultimo_mes_publicado()
    url = url_anexo_ipc(anio, mes)
    r = sesion().get(url, timeout=TIMEOUT)
    r.raise_for_status()
    ruta = guardar_binario(r.content, FUENTE, "ipc_anexo_variacion", url.rsplit("/", 1)[-1])
    return {"ipc_anexo_variacion": str(ruta)}


def probar() -> str:
    anio, mes = _ultimo_mes_publicado()
    url = url_anexo_ipc(anio, mes)
    r = sesion(reintentos=1).head(url, timeout=TIMEOUT_PROBAR, allow_redirects=True)
    tipo = r.headers.get("Content-Type", "")
    if r.status_code != 200 or "html" in tipo:
        raise RuntimeError(f"{r.status_code} {tipo} en {url}")
    return f"anexo IPC {MESES[mes - 1]}{anio} disponible ({r.headers.get('Content-Length', '?')} bytes)"
