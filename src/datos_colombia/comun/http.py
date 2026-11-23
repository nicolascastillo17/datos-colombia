"""Sesión HTTP con reintentos y User-Agent identificable."""

from __future__ import annotations

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from datos_colombia import __version__

USER_AGENT = f"datos-colombia/{__version__} (proyecto abierto de datos de Colombia)"
TIMEOUT = (10, 60)  # (conexión, lectura) en segundos — extracción
TIMEOUT_PROBAR = (10, 20)  # `probar` falla rápido en vez de esperar minutos
TIMEOUT_LENTO = (10, 90)  # fuentes que tardan >20 s en responder aun estando sanas (GDELT)


def sesion(reintentos: int = 4) -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    politica = Retry(
        total=reintentos,
        backoff_factor=2,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "HEAD"),
        respect_retry_after_header=True,
    )
    adaptador = HTTPAdapter(max_retries=politica)
    s.mount("https://", adaptador)
    s.mount("http://", adaptador)
    return s
