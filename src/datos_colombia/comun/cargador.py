"""Carga data/raw/**/part.parquet → raw_series.observaciones (upsert).

- Por defecto carga la partición `extraido=` más reciente de cada fuente/conjunto.
  La base acumula la historia (necesario para GDELT, cuya API solo cubre una
  ventana reciente).
- `todo=True` recorre todas las particiones en orden cronológico (reconstrucción).
- Upsert por (fuente, serie_id, fecha): solo actualiza si cambió el valor, la
  unidad o la frecuencia.
- Duplicados idénticos dentro de un lote se descartan y se reportan. Duplicados
  con VALORES DISTINTOS abortan la carga: significan que dos series comparten
  serie_id (error de parser), y quedarse con una perdería datos en silencio.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import psycopg
import pyarrow.parquet as pq

from datos_colombia.comun.config import DATOS_DIR

COLUMNAS = ["fuente", "conjunto", "serie_id", "fecha", "valor", "unidad", "frecuencia", "extraido_en"]

SQL_TEMP = """
CREATE TEMP TABLE carga_observaciones (LIKE raw_series.observaciones INCLUDING DEFAULTS)
ON COMMIT DROP
"""

SQL_UPSERT = """
WITH lote AS (
    SELECT DISTINCT ON (fuente, serie_id, fecha) *
    FROM carga_observaciones
    ORDER BY fuente, serie_id, fecha, extraido_en DESC
)
INSERT INTO raw_series.observaciones AS o
SELECT * FROM lote
ON CONFLICT (fuente, serie_id, fecha) DO UPDATE
SET valor = EXCLUDED.valor,
    unidad = EXCLUDED.unidad,
    frecuencia = EXCLUDED.frecuencia,
    conjunto = EXCLUDED.conjunto,
    extraido_en = EXCLUDED.extraido_en
WHERE (o.valor, o.unidad, o.frecuencia) IS DISTINCT FROM (EXCLUDED.valor, EXCLUDED.unidad, EXCLUDED.frecuencia)
RETURNING (xmax = 0) AS insertado
"""


SQL_CONFLICTOS = """
SELECT fuente, serie_id, count(*) AS fechas
FROM (
    SELECT fuente, serie_id, fecha
    FROM carga_observaciones
    GROUP BY fuente, serie_id, fecha
    HAVING count(DISTINCT (valor, unidad, frecuencia)) > 1
) c
GROUP BY fuente, serie_id
ORDER BY fechas DESC
LIMIT 5
"""


class SerieAmbigua(RuntimeError):
    """Dos series distintas con el mismo serie_id en un lote."""


@dataclass
class Resultado:
    archivos: int = 0
    filas_leidas: int = 0
    duplicadas: int = 0
    insertadas: int = 0
    actualizadas: int = 0

    def __str__(self) -> str:
        sin_cambio = self.filas_leidas - self.duplicadas - self.insertadas - self.actualizadas
        return (
            f"{self.archivos} archivos, {self.filas_leidas} filas: {self.insertadas} nuevas, "
            f"{self.actualizadas} actualizadas, {sin_cambio} sin cambio, {self.duplicadas} duplicadas en lote"
        )


def particiones(fuente: str | None = None, todo: bool = False, base: Path | None = None) -> list[Path]:
    """Rutas part.parquet a cargar, en orden cronológico de extracción."""
    raiz = (base or DATOS_DIR) / "raw"
    if not raiz.exists():
        return []
    dirs_fuente = [raiz / fuente] if fuente else sorted(p for p in raiz.iterdir() if p.is_dir())
    rutas: list[Path] = []
    for d_fuente in dirs_fuente:
        if not d_fuente.exists():
            continue
        for d_conjunto in sorted(p for p in d_fuente.iterdir() if p.is_dir()):
            parts = sorted(d_conjunto.glob("extraido=*/part.parquet"))
            rutas.extend(parts if todo else parts[-1:])
    return sorted(rutas, key=lambda p: p.parent.name)


def cargar_archivo(conexion: psycopg.Connection, ruta: Path, resultado: Resultado) -> None:
    tabla = pq.read_table(ruta, columns=COLUMNAS)
    filas = tabla.to_pylist()
    with conexion.transaction():
        conexion.execute(SQL_TEMP)
        with conexion.cursor() as cur:
            with cur.copy(f"COPY carga_observaciones ({', '.join(COLUMNAS)}) FROM STDIN") as copia:
                for f in filas:
                    copia.write_row([f[c] for c in COLUMNAS])
            conflictos = cur.execute(SQL_CONFLICTOS).fetchall()
            if conflictos:
                detalle = ", ".join(f"{f}/{s} ({n} fechas)" for f, s, n in conflictos)
                raise SerieAmbigua(f"{ruta}: serie_id compartido por series distintas → {detalle}")
            distintas = cur.execute(
                "SELECT count(*) FROM (SELECT DISTINCT fuente, serie_id, fecha FROM carga_observaciones) d"
            ).fetchone()[0]
            marcas = [r[0] for r in cur.execute(SQL_UPSERT).fetchall()]
    resultado.archivos += 1
    resultado.filas_leidas += len(filas)
    resultado.duplicadas += len(filas) - distintas
    resultado.insertadas += sum(1 for m in marcas if m)
    resultado.actualizadas += sum(1 for m in marcas if not m)


def cargar(conexion: psycopg.Connection, fuente: str | None = None, todo: bool = False, base: Path | None = None) -> Resultado:
    resultado = Resultado()
    for ruta in particiones(fuente, todo, base):
        cargar_archivo(conexion, ruta, resultado)
    return resultado
