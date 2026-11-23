"""Escritura del aterrizaje raw en Parquet con el esquema común `observaciones`."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from datos_colombia.comun.config import DATOS_DIR

ESQUEMA_OBSERVACIONES = pa.schema(
    [
        ("fuente", pa.string()),
        ("conjunto", pa.string()),
        ("serie_id", pa.string()),
        ("fecha", pa.date32()),
        ("valor", pa.float64()),
        ("unidad", pa.string()),
        ("frecuencia", pa.string()),
        ("extraido_en", pa.timestamp("s", tz="UTC")),
    ]
)


@dataclass(frozen=True)
class Observacion:
    fuente: str
    conjunto: str
    serie_id: str
    fecha: date
    valor: float | None
    unidad: str | None = None
    frecuencia: str | None = None


def a_float(valor) -> float | None:
    """Convierte texto/número a float; vacíos y marcadores no numéricos → None."""
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).strip()
    if texto in {"", "NaN", "nan", "-", ".."}:
        return None
    if "," in texto and "." not in texto:  # decimal con coma: "12,25"
        texto = texto.replace(",", ".")
    return float(texto)


def guardar_observaciones(
    observaciones: list[Observacion],
    fuente: str,
    conjunto: str,
    base: Path | None = None,
) -> Path | None:
    """Escribe data/raw/<fuente>/<conjunto>/extraido=AAAA-MM-DD/part.parquet. Devuelve la ruta."""
    if not observaciones:
        return None
    ahora = datetime.now(timezone.utc).replace(microsecond=0)
    filas = [{**asdict(o), "extraido_en": ahora} for o in observaciones]
    tabla = pa.Table.from_pylist(filas, schema=ESQUEMA_OBSERVACIONES)
    destino = (base or DATOS_DIR) / "raw" / fuente / conjunto / f"extraido={ahora.date().isoformat()}"
    destino.mkdir(parents=True, exist_ok=True)
    ruta = destino / "part.parquet"
    pq.write_table(tabla, ruta)
    return ruta


def guardar_binario(contenido: bytes, fuente: str, conjunto: str, nombre: str, base: Path | None = None) -> Path:
    """Para fuentes sin API (xlsx/pdf): guarda el archivo original tal cual."""
    hoy = datetime.now(timezone.utc).date().isoformat()
    destino = (base or DATOS_DIR) / "raw" / fuente / conjunto / f"extraido={hoy}"
    destino.mkdir(parents=True, exist_ok=True)
    ruta = destino / nombre
    ruta.write_bytes(contenido)
    return ruta
